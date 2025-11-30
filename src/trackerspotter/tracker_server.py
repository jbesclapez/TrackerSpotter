"""
BitTorrent Tracker HTTP Server
Implements BEP 3: The BitTorrent Protocol
"""

from flask import Flask, request, Response, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
from typing import Optional
import logging
import sys
import secrets
from pathlib import Path

from .models import AnnounceEvent
from .database import Database
from .utils import (
    parse_info_hash,
    parse_peer_id,
    create_tracker_response,
    extract_client_info
)
from .udp_tracker import UDPTrackerServer
from . import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# UDP event broadcasting is handled via callback in TrackerServer instance


class TrackerServer:
    """BitTorrent tracker server with web UI"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 6969, debug: bool = False, 
                 enable_ipv6: bool = False):
        """
        Initialize tracker server
        
        Args:
            host: Host to bind to (default: localhost only)
            port: Port to listen on
            debug: Enable debug mode
            enable_ipv6: Also bind to IPv6 (::1)
        """
        self.host = host
        self.port = port
        self.debug = debug
        self.enable_ipv6 = enable_ipv6
        
        # Determine static folder path based on execution mode
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            # PyInstaller extracts to sys._MEIPASS
            base_path = Path(sys._MEIPASS) / 'trackerspotter' / 'static'
        else:
            # Running from source
            base_path = Path(__file__).parent / 'static'
        
        # Initialize Flask app with correct static folder path
        self.app = Flask(__name__, 
                        static_folder=str(base_path),
                        static_url_path='/static')
        # Generate random secret key at runtime for session security
        self.app.config['SECRET_KEY'] = secrets.token_hex(32)
        
        # Initialize SocketIO for real-time updates
        # Simple configuration for maximum compatibility
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            logger=False,
            engineio_logger=False
        )
        
        # Initialize database
        self.db = Database()
        
        # Initialize UDP tracker (shares same database)
        # Pass broadcast callback for real-time event updates
        self.udp_tracker = UDPTrackerServer(
            host=host,  # Use same host as HTTP tracker (127.0.0.1 by default)
            port=port,
            database=self.db,
            event_callback=self._broadcast_event,  # Use instance method for broadcasting
            enable_ipv6=enable_ipv6
        )
        
        # IPv6 UDP tracker (optional)
        self.udp_tracker_ipv6 = None
        if enable_ipv6:
            ipv6_host = '::1' if host == '127.0.0.1' else '::' if host == '0.0.0.0' else None
            if ipv6_host:
                self.udp_tracker_ipv6 = UDPTrackerServer(
                    host=ipv6_host,
                    port=port,
                    database=self.db,
                    event_callback=self._broadcast_event,
                    enable_ipv6=True,
                    is_ipv6=True
                )
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"TrackerSpotter initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve main dashboard"""
            return send_from_directory(self.app.static_folder, 'index.html')
        
        @self.app.route('/scrape')
        def scrape():
            """
            Handle BitTorrent tracker scrape requests
            Scrape returns stats about specified torrents
            """
            try:
                # Parse info_hash(es) - can be multiple
                info_hashes = request.args.getlist('info_hash')
                
                # Capture raw HTTP headers
                raw_headers_lines = []
                for header_name, header_value in request.headers:
                    raw_headers_lines.append(f"{header_name}: {header_value}")
                raw_headers = "\r\n".join(raw_headers_lines)
                
                # Get client info
                client_ip = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                
                # Process each info_hash and log as scrape event
                scraped_hashes = []
                for info_hash_raw in info_hashes:
                    try:
                        info_hash_raw_bytes, info_hash_hex = parse_info_hash(info_hash_raw)
                        if info_hash_hex:
                            scraped_hashes.append(info_hash_hex)
                            
                            # Create scrape event
                            scrape_event = AnnounceEvent(
                                timestamp=datetime.now(),
                                info_hash=info_hash_raw_bytes.hex() if info_hash_raw_bytes else info_hash_hex,
                                info_hash_hex=info_hash_hex,
                                peer_id="",  # Scrape doesn't have peer_id
                                client_ip=client_ip,
                                client_port=0,
                                uploaded=0,
                                downloaded=0,
                                left=0,
                                event="scrape",  # Special event type for scrape
                                user_agent=user_agent,
                                numwant=0,
                                compact=0,
                                key="",
                                raw_query=request.query_string.decode('utf-8', errors='ignore'),
                                raw_headers=raw_headers
                            )
                            
                            # Store in database
                            event_id = self.db.insert_announce(scrape_event)
                            scrape_event.id = event_id
                            
                            # Broadcast to connected web clients
                            self._broadcast_event(scrape_event)
                    except Exception:
                        continue
                
                # Log the scrape
                hash_count = len(scraped_hashes)
                logger.info(
                    f"Scrape received: {hash_count} hash(es) | "
                    f"Client: {client_ip} | "
                    f"Hashes: {', '.join(h[:8] + '...' for h in scraped_hashes[:3])}"
                    f"{'...' if hash_count > 3 else ''}"
                )
                
                # Return minimal valid scrape response (we're just monitoring)
                from .utils import bencode
                
                files = {}
                for info_hash_hex in scraped_hashes:
                    # Convert hex back to bytes for the response key
                    files[bytes.fromhex(info_hash_hex)] = {
                        b'complete': 0,    # Seeders
                        b'incomplete': 0,  # Leechers
                        b'downloaded': 0   # Times completed
                    }
                
                response_dict = {b'files': files}
                return Response(bencode(response_dict), mimetype='text/plain')
                
            except Exception as e:
                logger.error(f"Error processing scrape: {e}", exc_info=True)
                from .utils import bencode
                error_dict = {b'failure reason': b'Internal server error'}
                return Response(bencode(error_dict), mimetype='text/plain')
        
        @self.app.route('/announce')
        def announce():
            """
            Handle BitTorrent tracker announce requests
            BEP 3: The BitTorrent Protocol
            """
            try:
                # Parse required parameters
                info_hash_raw, info_hash_hex = parse_info_hash(request.args.get('info_hash', ''))
                peer_id = parse_peer_id(request.args.get('peer_id', ''))
                
                if not info_hash_hex or not peer_id:
                    return self._create_error_response("Missing required parameters")
                
                # Parse optional parameters with safe integer conversion
                def safe_int(value, default=0, min_val=0, max_val=None):
                    """Safely convert to int with bounds checking"""
                    try:
                        result = int(value) if value else default
                        if result < min_val:
                            result = min_val
                        if max_val is not None and result > max_val:
                            result = max_val
                        return result
                    except (ValueError, TypeError):
                        return default
                
                port = safe_int(request.args.get('port'), 0, 0, 65535)
                uploaded = safe_int(request.args.get('uploaded'), 0, 0)
                downloaded = safe_int(request.args.get('downloaded'), 0, 0)
                left = safe_int(request.args.get('left'), 0, 0)
                event = request.args.get('event', '') or ''
                compact = safe_int(request.args.get('compact'), 1, 0, 1)
                numwant = safe_int(request.args.get('numwant'), 50, 0, 200)
                key = request.args.get('key', '') or ''
                
                # Get client info
                client_ip = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                
                # Capture raw HTTP headers as-is (important for client file making)
                # Format: "Header-Name: value\r\n" for each header
                raw_headers_lines = []
                for header_name, header_value in request.headers:
                    raw_headers_lines.append(f"{header_name}: {header_value}")
                raw_headers = "\r\n".join(raw_headers_lines)
                
                # Create announce event
                announce_event = AnnounceEvent(
                    timestamp=datetime.now(),
                    info_hash=info_hash_raw.hex(),
                    info_hash_hex=info_hash_hex,
                    peer_id=peer_id,
                    client_ip=client_ip,
                    client_port=port,
                    uploaded=uploaded,
                    downloaded=downloaded,
                    left=left,
                    event=event,
                    user_agent=user_agent,
                    numwant=numwant,
                    compact=compact,
                    key=key,
                    raw_query=request.query_string.decode('utf-8', errors='ignore'),
                    raw_headers=raw_headers
                )
                
                # Store in database
                event_id = self.db.insert_announce(announce_event)
                announce_event.id = event_id
                
                # Log the event
                event_type = event if event else "update"
                logger.info(
                    f"Announce received: {event_type} | "
                    f"Torrent: {info_hash_hex[:8]}... | "
                    f"Client: {client_ip}:{port} | "
                    f"↓{downloaded} ↑{uploaded} ⏳{left}"
                )
                
                # Broadcast to connected web clients via WebSocket
                self._broadcast_event(announce_event)
                
                # Return minimal valid tracker response
                response_data = create_tracker_response(
                    interval=1800,  # 30 minutes
                    compact=(compact == 1)
                )
                
                return Response(response_data, mimetype='text/plain')
                
            except ValueError as e:
                logger.error(f"Invalid announce parameters: {e}")
                return self._create_error_response(f"Invalid parameters: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing announce: {e}", exc_info=True)
                return self._create_error_response("Internal server error")
        
        @self.app.route('/api/events')
        def get_events():
            """Get announce events with optional filters"""
            try:
                # Parse query parameters
                event_type = request.args.get('event_type')
                info_hash = request.args.get('info_hash')
                search = request.args.get('search')
                limit = int(request.args.get('limit', 100))
                
                # Query database
                if any([event_type, info_hash, search]):
                    events = self.db.get_announces_by_filter(
                        event_type=event_type if event_type != 'all' else None,
                        info_hash=info_hash if info_hash != 'all' else None,
                        search=search,
                        limit=limit
                    )
                else:
                    events = self.db.get_recent_announces(limit=limit)
                
                # Clean up events for JSON serialization
                clean_events = []
                for event in events:
                    clean_event = dict(event)
                    # Ensure info_hash is a string, not bytes
                    if isinstance(clean_event.get('info_hash'), bytes):
                        clean_event['info_hash'] = clean_event['info_hash'].decode('utf-8', errors='ignore')
                    clean_events.append(clean_event)
                
                return jsonify({
                    'success': True,
                    'events': clean_events,
                    'count': len(clean_events)
                })
            except Exception as e:
                logger.error(f"Error fetching events: {e}", exc_info=True)
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/torrents')
        def get_torrents():
            """Get list of unique torrents"""
            try:
                torrents = self.db.get_unique_torrents()
                return jsonify({
                    'success': True,
                    'torrents': torrents
                })
            except Exception as e:
                logger.error(f"Error fetching torrents: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/stats')
        def get_stats():
            """Get database statistics"""
            try:
                stats = self.db.get_stats()
                event_counts = self.db.get_event_counts()
                
                return jsonify({
                    'success': True,
                    'stats': stats,
                    'event_counts': event_counts
                })
            except Exception as e:
                logger.error(f"Error fetching stats: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/config')
        def get_config():
            """Get server configuration for UI"""
            # Determine display host (use 127.0.0.1 if bound to all interfaces)
            display_host = '127.0.0.1' if self.host == '0.0.0.0' else self.host
            
            config = {
                'success': True,
                'host': self.host,
                'display_host': display_host,
                'port': self.port,
                'http_url': f"http://{display_host}:{self.port}/announce",
                'udp_url': f"udp://{display_host}:{self.port}/announce",
                'is_localhost': self.host in ('127.0.0.1', 'localhost', '::1'),
                'ipv6_enabled': self.enable_ipv6
            }
            
            # Add IPv6 URLs if enabled
            if self.enable_ipv6:
                ipv6_host = '::1' if self.host in ('127.0.0.1', 'localhost') else '::' if self.host == '0.0.0.0' else None
                if ipv6_host:
                    config['ipv6_host'] = ipv6_host
                    config['http_url_ipv6'] = f"http://[{ipv6_host}]:{self.port}/announce"
                    config['udp_url_ipv6'] = f"udp://[{ipv6_host}]:{self.port}/announce"
            
            # Add version info
            config['version'] = __version__
            
            return jsonify(config)
        
        @self.app.route('/api/clear', methods=['POST'])
        def clear_logs():
            """Clear all announce logs"""
            try:
                count = self.db.clear_all_announces()
                logger.info(f"Cleared {count} announce events")
                
                # Notify all clients
                self.socketio.emit('logs_cleared', {'count': count})
                
                return jsonify({
                    'success': True,
                    'deleted': count
                })
            except Exception as e:
                logger.error(f"Error clearing logs: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/export/csv')
        def export_csv():
            """Export events to CSV"""
            try:
                events = self.db.get_recent_announces(limit=10000)
                
                # Generate CSV
                csv_lines = [
                    'timestamp,event,info_hash,client_ip,client_port,downloaded,uploaded,left,user_agent,raw_query'
                ]
                
                for event in events:
                    # Escape quotes in raw_query for CSV
                    raw_query = event.get('raw_query', '') or ''
                    raw_query_escaped = raw_query.replace('"', '""')
                    csv_lines.append(
                        f"{event['timestamp']},"
                        f"{event['event'] if event['event'] else 'update'},"
                        f"{event['info_hash_hex']},"
                        f"{event['client_ip']},"
                        f"{event['client_port']},"
                        f"{event['downloaded']},"
                        f"{event['uploaded']},"
                        f"{event['left']},"
                        f"\"{event['user_agent']}\","
                        f"\"{raw_query_escaped}\""
                    )
                
                csv_data = '\n'.join(csv_lines)
                
                return Response(
                    csv_data,
                    mimetype='text/csv',
                    headers={
                        'Content-Disposition': f'attachment; filename=trackerspotter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
                    }
                )
            except Exception as e:
                logger.error(f"Error exporting CSV: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/export/json')
        def export_json():
            """Export events to JSON"""
            try:
                events = self.db.get_recent_announces(limit=10000)
                
                return Response(
                    jsonify({
                        'export_date': datetime.now().isoformat(),
                        'total_events': len(events),
                        'events': events
                    }).get_data(as_text=True),
                    mimetype='application/json',
                    headers={
                        'Content-Disposition': f'attachment; filename=trackerspotter_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                    }
                )
            except Exception as e:
                logger.error(f"Error exporting JSON: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        # WebSocket events
        @self.socketio.on('connect')
        def handle_connect():
            """Handle WebSocket connection"""
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'message': 'Connected to TrackerSpotter'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle WebSocket disconnection"""
            logger.info(f"Client disconnected: {request.sid}")
    
    def _create_error_response(self, error_message: str) -> Response:
        """
        Create bencoded error response
        
        Args:
            error_message: Error message to send
            
        Returns:
            Flask Response with bencoded error
        """
        from .utils import bencode
        
        error_dict = {b'failure reason': error_message.encode('utf-8')}
        return Response(bencode(error_dict), mimetype='text/plain')
    
    def _broadcast_event(self, event: AnnounceEvent):
        """
        Broadcast announce event to all connected WebSocket clients
        
        Args:
            event: AnnounceEvent to broadcast
        """
        try:
            self.socketio.emit('new_announce', event.to_dict())
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}", exc_info=True)
    
    def run(self):
        """Start the tracker server (HTTP and UDP)"""
        try:
            logger.info(f"Starting TrackerSpotter on http://{self.host}:{self.port}")
            logger.info(f"HTTP Tracker URL: http://{self.host}:{self.port}/announce")
            logger.info(f"UDP Tracker URL: udp://{self.host}:{self.port}/announce")
            logger.info(f"Dashboard: http://{self.host}:{self.port}")
            
            if self.enable_ipv6:
                ipv6_host = '::1' if self.host == '127.0.0.1' else '::' if self.host == '0.0.0.0' else self.host
                logger.info(f"IPv6 Tracker URL: http://[{ipv6_host}]:{self.port}/announce")
            
            # Start UDP tracker in background thread
            try:
                self.udp_tracker.start()
                logger.info("UDP Tracker (IPv4) started successfully")
            except Exception as e:
                logger.error(f"Failed to start UDP tracker: {e}")
                logger.info("Continuing with HTTP tracker only...")
            
            # Start IPv6 UDP tracker if enabled
            if self.udp_tracker_ipv6:
                try:
                    self.udp_tracker_ipv6.start()
                    logger.info("UDP Tracker (IPv6) started successfully")
                except Exception as e:
                    logger.error(f"Failed to start IPv6 UDP tracker: {e}")
            
            # Start HTTP server (blocking)
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=self.debug,
                allow_unsafe_werkzeug=True  # For PyInstaller packaging
            )
        except OSError as e:
            if "Address already in use" in str(e):
                logger.error(f"Port {self.port} is already in use!")
                logger.error("Try changing the port or stop the other application")
            else:
                logger.error(f"Failed to start server: {e}")
            raise
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            # Stop UDP trackers on shutdown
            if self.udp_tracker:
                self.udp_tracker.stop()
            if self.udp_tracker_ipv6:
                self.udp_tracker_ipv6.stop()

