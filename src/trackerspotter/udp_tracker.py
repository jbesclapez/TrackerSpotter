"""
UDP Tracker Server
Implements BEP 15: UDP Tracker Protocol
"""

import socket
import struct
import time
import logging
import threading
from typing import Optional, Tuple
from datetime import datetime

from .models import AnnounceEvent
from .database import Database

logger = logging.getLogger(__name__)

# Protocol constants
CONNECT_ACTION = 0
ANNOUNCE_ACTION = 1
SCRAPE_ACTION = 2
ERROR_ACTION = 3

PROTOCOL_ID = 0x41727101980  # Magic constant for BEP 15


class UDPTrackerServer:
    """UDP BitTorrent tracker server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 6969, database: Database = None):
        """
        Initialize UDP tracker server
        
        Args:
            host: Host to bind to
            port: UDP port to listen on
            database: Database instance to store events
        """
        self.host = host
        self.port = port
        self.db = database or Database()
        self.socket = None
        self.running = False
        self.connections = {}  # Track connection IDs
        
        logger.info(f"UDP Tracker initialized on {host}:{port}")
    
    def start(self):
        """Start the UDP tracker server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.running = True
            
            logger.info(f"UDP Tracker listening on {self.host}:{self.port}")
            logger.info(f"UDP Tracker URL: udp://{self.host}:{self.port}/announce")
            
            # Start listening thread
            listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            listen_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start UDP tracker: {e}")
            raise
    
    def stop(self):
        """Stop the UDP tracker server"""
        self.running = False
        if self.socket:
            self.socket.close()
        logger.info("UDP Tracker stopped")
    
    def _listen_loop(self):
        """Main listening loop for UDP packets"""
        logger.info("UDP Tracker listening for packets...")
        
        while self.running:
            try:
                # Receive UDP packet (max 2048 bytes for tracker packets)
                data, addr = self.socket.recvfrom(2048)
                
                # Handle packet in separate thread to not block
                handler_thread = threading.Thread(
                    target=self._handle_packet,
                    args=(data, addr),
                    daemon=True
                )
                handler_thread.start()
                
            except Exception as e:
                if self.running:
                    logger.error(f"Error in UDP listen loop: {e}")
    
    def _handle_packet(self, data: bytes, addr: Tuple[str, int]):
        """
        Handle incoming UDP packet
        
        Args:
            data: Raw packet data
            addr: Client address (ip, port)
        """
        try:
            if len(data) < 16:
                logger.warning(f"Packet too short from {addr}: {len(data)} bytes")
                return
            
            # Parse action from packet (first 8 bytes = connection_id, next 4 = action)
            connection_id = struct.unpack(">Q", data[0:8])[0]
            action = struct.unpack(">I", data[8:12])[0]
            transaction_id = struct.unpack(">I", data[12:16])[0]
            
            if action == CONNECT_ACTION:
                self._handle_connect(data, addr, transaction_id)
            elif action == ANNOUNCE_ACTION:
                self._handle_announce(data, addr, connection_id, transaction_id)
            elif action == SCRAPE_ACTION:
                self._handle_scrape(data, addr, connection_id, transaction_id)
            else:
                logger.warning(f"Unknown action {action} from {addr}")
                self._send_error(addr, transaction_id, "Unknown action")
                
        except Exception as e:
            logger.error(f"Error handling packet from {addr}: {e}", exc_info=True)
    
    def _handle_connect(self, data: bytes, addr: Tuple[str, int], transaction_id: int):
        """
        Handle connect request (BEP 15)
        
        Connect request format:
        - int64_t: protocol_id (0x41727101980)
        - int32_t: action (0 for connect)
        - int32_t: transaction_id
        """
        try:
            protocol_id = struct.unpack(">Q", data[0:8])[0]
            
            if protocol_id != PROTOCOL_ID:
                logger.warning(f"Invalid protocol ID from {addr}: {protocol_id}")
                self._send_error(addr, transaction_id, "Invalid protocol ID")
                return
            
            # Generate connection ID (use timestamp + client IP hash)
            connection_id = int(time.time()) & 0xFFFFFFFFFFFFFFFF
            self.connections[connection_id] = time.time()
            
            # Send connect response
            # Format: action (0) | transaction_id | connection_id
            response = struct.pack(">IIQ", CONNECT_ACTION, transaction_id, connection_id)
            self.socket.sendto(response, addr)
            
            logger.debug(f"Connect from {addr}: connection_id={connection_id}")
            
        except Exception as e:
            logger.error(f"Error in connect handler: {e}")
            self._send_error(addr, transaction_id, "Connect failed")
    
    def _handle_announce(self, data: bytes, addr: Tuple[str, int], 
                        connection_id: int, transaction_id: int):
        """
        Handle announce request (BEP 15)
        
        Announce request format (98 bytes minimum):
        - int64_t: connection_id
        - int32_t: action (1)
        - int32_t: transaction_id
        - char[20]: info_hash
        - char[20]: peer_id
        - int64_t: downloaded
        - int64_t: left
        - int64_t: uploaded
        - int32_t: event (0=none, 1=completed, 2=started, 3=stopped)
        - int32_t: IP address (0 = default)
        - int32_t: key
        - int32_t: num_want (-1 = default)
        - uint16_t: port
        """
        try:
            if len(data) < 98:
                logger.warning(f"Announce packet too short from {addr}: {len(data)} bytes")
                return
            
            # Verify connection ID
            if connection_id not in self.connections:
                logger.warning(f"Invalid connection_id from {addr}: {connection_id}")
                self._send_error(addr, transaction_id, "Invalid connection ID")
                return
            
            # Parse announce fields
            info_hash = data[16:36]
            peer_id = data[36:56]
            downloaded = struct.unpack(">Q", data[56:64])[0]
            left = struct.unpack(">Q", data[64:72])[0]
            uploaded = struct.unpack(">Q", data[72:80])[0]
            event_code = struct.unpack(">I", data[80:84])[0]
            ip_address = struct.unpack(">I", data[84:88])[0]
            key = struct.unpack(">I", data[88:92])[0]
            num_want = struct.unpack(">i", data[92:96])[0]  # signed int
            port = struct.unpack(">H", data[96:98])[0]
            
            # Convert event code to string
            event_map = {0: "", 1: "completed", 2: "started", 3: "stopped"}
            event = event_map.get(event_code, "")
            
            # Create announce event
            announce_event = AnnounceEvent(
                timestamp=datetime.now(),
                info_hash=info_hash.hex(),
                info_hash_hex=info_hash.hex(),
                peer_id=peer_id.hex(),
                client_ip=addr[0],
                client_port=port,
                uploaded=uploaded,
                downloaded=downloaded,
                left=left,
                event=event,
                user_agent="UDP",  # UDP doesn't have user agent
                numwant=num_want if num_want > 0 else 50,
                compact=1,  # UDP always compact
                key=f"{key:08x}",
                raw_query=f"UDP announce from {addr[0]}:{port}"
            )
            
            # Store in database
            event_id = self.db.insert_announce(announce_event)
            announce_event.id = event_id
            
            # Log the event
            event_type = event if event else "update"
            logger.info(
                f"UDP Announce: {event_type} | "
                f"Torrent: {info_hash.hex()[:8]}... | "
                f"Client: {addr[0]}:{port} | "
                f"↓{downloaded} ↑{uploaded} ⏳{left}"
            )
            
            # Send announce response
            # Format: action (1) | transaction_id | interval | leechers | seeders | peers
            interval = 1800  # 30 minutes
            leechers = 0
            seeders = 0
            peers = b''  # Empty peer list (we're just monitoring)
            
            response = struct.pack(
                ">IIIII",
                ANNOUNCE_ACTION,
                transaction_id,
                interval,
                leechers,
                seeders
            ) + peers
            
            self.socket.sendto(response, addr)
            
            # Broadcast to WebSocket clients if HTTP server is available
            try:
                from .tracker_server import broadcast_udp_event
                broadcast_udp_event(announce_event)
            except Exception:
                pass  # HTTP server might not be running
            
        except Exception as e:
            logger.error(f"Error in announce handler: {e}", exc_info=True)
            self._send_error(addr, transaction_id, "Announce failed")
    
    def _handle_scrape(self, data: bytes, addr: Tuple[str, int],
                      connection_id: int, transaction_id: int):
        """
        Handle scrape request (BEP 15)
        
        Scrape request format:
        - int64_t: connection_id
        - int32_t: action (2)
        - int32_t: transaction_id
        - char[20]: info_hash (repeated for multiple hashes)
        """
        try:
            # Verify connection ID
            if connection_id not in self.connections:
                logger.warning(f"Invalid connection_id from {addr}: {connection_id}")
                self._send_error(addr, transaction_id, "Invalid connection ID")
                return
            
            # Return minimal scrape response (we're just monitoring, not tracking peers)
            # Format: action (2) | transaction_id | (seeders | completed | leechers) per hash
            response = struct.pack(">II", SCRAPE_ACTION, transaction_id)
            
            # For each info_hash in the request, add stats
            num_hashes = (len(data) - 16) // 20
            for i in range(num_hashes):
                # Add fake stats for each hash (we don't actually track peers)
                response += struct.pack(">III", 0, 0, 0)  # seeders, completed, leechers
            
            self.socket.sendto(response, addr)
            logger.debug(f"Scrape from {addr}: {num_hashes} hashes")
            
        except Exception as e:
            logger.error(f"Error in scrape handler: {e}")
            self._send_error(addr, transaction_id, "Scrape failed")
    
    def _send_error(self, addr: Tuple[str, int], transaction_id: int, message: str):
        """
        Send error response
        
        Error response format:
        - int32_t: action (3 for error)
        - int32_t: transaction_id
        - string: error message
        """
        try:
            message_bytes = message.encode('utf-8')
            response = struct.pack(">II", ERROR_ACTION, transaction_id) + message_bytes
            self.socket.sendto(response, addr)
            logger.debug(f"Sent error to {addr}: {message}")
        except Exception as e:
            logger.error(f"Failed to send error: {e}")
    
    def cleanup_old_connections(self):
        """Remove connection IDs older than 2 minutes"""
        current_time = time.time()
        expired = [
            conn_id for conn_id, timestamp in self.connections.items()
            if current_time - timestamp > 120  # 2 minutes
        ]
        for conn_id in expired:
            del self.connections[conn_id]
        
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired connections")

