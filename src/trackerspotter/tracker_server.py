"""
BitTorrent Tracker HTTP Server
Implements BEP 3: The BitTorrent Protocol
"""

from flask import Flask, request, Response, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
from typing import Optional
import logging

from .models import AnnounceEvent
from .database import Database
from .utils import (
    parse_info_hash,
    parse_peer_id,
    create_tracker_response,
    extract_client_info
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrackerServer:
    """BitTorrent tracker server with web UI"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 6969, debug: bool = False):
        """
        Initialize tracker server
        
        Args:
            host: Host to bind to (default: localhost only)
            port: Port to listen on
            debug: Enable debug mode
        """
        self.host = host
        self.port = port
        self.debug = debug
        
        # Initialize Flask app
        self.app = Flask(__name__, 
                        static_folder='static',
                        static_url_path='/static')
        self.app.config['SECRET_KEY'] = 'trackerspotter-secret-key-change-in-production'
        
        # Initialize SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Initialize database
        self.db = Database()
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"TrackerSpotter initialized on {host}:{port}")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def index():
            """Serve main dashboard"""
            return send_from_directory(self.app.static_folder, 'index.html')
        
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
                
                # Parse optional parameters
                port = int(request.args.get('port', 0))
                uploaded = int(request.args.get('uploaded', 0))
                downloaded = int(request.args.get('downloaded', 0))
                left = int(request.args.get('left', 0))
                event = request.args.get('event', '')
                compact = int(request.args.get('compact', 1))
                numwant = int(request.args.get('numwant', 50))
                key = request.args.get('key', '')
                
                # Get client info
                client_ip = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                
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
                    raw_query=request.query_string.decode('utf-8', errors='ignore')
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
                
                return jsonify({
                    'success': True,
                    'events': events,
                    'count': len(events)
                })
            except Exception as e:
                logger.error(f"Error fetching events: {e}")
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
                    'timestamp,event,info_hash,client_ip,client_port,downloaded,uploaded,left,user_agent'
                ]
                
                for event in events:
                    csv_lines.append(
                        f"{event['timestamp']},"
                        f"{event['event'] if event['event'] else 'update'},"
                        f"{event['info_hash_hex']},"
                        f"{event['client_ip']},"
                        f"{event['client_port']},"
                        f"{event['downloaded']},"
                        f"{event['uploaded']},"
                        f"{event['left']},"
                        f"\"{event['user_agent']}\""
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
            logger.error(f"Error broadcasting event: {e}")
    
    def run(self):
        """Start the tracker server"""
        try:
            logger.info(f"Starting TrackerSpotter on http://{self.host}:{self.port}")
            logger.info(f"Tracker URL: http://{self.host}:{self.port}/announce")
            logger.info(f"Dashboard: http://{self.host}:{self.port}")
            
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

