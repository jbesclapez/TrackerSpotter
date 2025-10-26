"""
Utility functions for TrackerSpotter
"""

import bencodepy
from typing import Dict, Any
from urllib.parse import unquote_to_bytes


def bencode(data: Any) -> bytes:
    """
    Encode data to bencode format
    
    Args:
        data: Dictionary, list, int, or bytes to encode
        
    Returns:
        Bencoded bytes
    """
    return bencodepy.encode(data)


def bdecode(data: bytes) -> Any:
    """
    Decode bencode format data
    
    Args:
        data: Bencoded bytes
        
    Returns:
        Decoded data structure
    """
    return bencodepy.decode(data)


def parse_info_hash(encoded_hash: str) -> tuple[bytes, str]:
    """
    Parse URL-encoded info hash
    
    Args:
        encoded_hash: URL-encoded 20-byte info hash
        
    Returns:
        Tuple of (raw bytes, hex string representation)
    """
    try:
        # Decode URL encoding to get raw bytes
        raw_bytes = unquote_to_bytes(encoded_hash)
        
        # Convert to hex string for display
        hex_string = raw_bytes.hex()
        
        return raw_bytes, hex_string
    except Exception:
        # If parsing fails, return empty values
        return b"", ""


def parse_peer_id(encoded_peer_id: str) -> str:
    """
    Parse URL-encoded peer ID
    
    Args:
        encoded_peer_id: URL-encoded 20-byte peer ID
        
    Returns:
        Hex string representation
    """
    try:
        raw_bytes = unquote_to_bytes(encoded_peer_id)
        return raw_bytes.hex()
    except Exception:
        return ""


def create_tracker_response(
    interval: int = 1800,
    complete: int = 0,
    incomplete: int = 0,
    compact: bool = True
) -> bytes:
    """
    Create a minimal valid tracker response
    
    Args:
        interval: Seconds until next announce (default 30 minutes)
        complete: Number of seeders (fake, default 0)
        incomplete: Number of leechers (fake, default 0)
        compact: Use compact format (default True)
        
    Returns:
        Bencoded tracker response
    """
    response = {
        b'interval': interval,
        b'complete': complete,
        b'incomplete': incomplete,
    }
    
    if compact:
        # Empty compact peer list (6-byte format: 4 bytes IP + 2 bytes port)
        response[b'peers'] = b''
    else:
        # Empty regular peer list
        response[b'peers'] = []
    
    return bencode(response)


def extract_client_info(user_agent: str, peer_id: str) -> Dict[str, str]:
    """
    Extract client information from user agent and peer ID
    
    Args:
        user_agent: HTTP User-Agent header
        peer_id: BitTorrent peer ID (hex string)
        
    Returns:
        Dictionary with client name and version if identifiable
    """
    info = {
        'name': 'Unknown',
        'version': ''
    }
    
    # Try to parse from user agent first
    if user_agent:
        # Common patterns: "qBittorrent/4.5.0", "Transmission/3.00"
        if '/' in user_agent:
            parts = user_agent.split('/', 1)
            info['name'] = parts[0]
            if len(parts) > 1:
                info['version'] = parts[1].split()[0]  # Take first part before space
            return info
    
    # Try to parse from peer ID (Azureus-style: -XX####-)
    if peer_id and len(peer_id) >= 16:
        try:
            # Convert hex to ASCII for first 8 chars
            peer_id_ascii = bytes.fromhex(peer_id[:16]).decode('ascii', errors='ignore')
            
            if peer_id_ascii.startswith('-') and len(peer_id_ascii) >= 7:
                client_code = peer_id_ascii[1:3]
                version = peer_id_ascii[3:7]
                
                # Known client codes
                client_map = {
                    'qB': 'qBittorrent',
                    'TR': 'Transmission',
                    'UT': 'μTorrent',
                    'DE': 'Deluge',
                    'lt': 'libtorrent',
                    'AZ': 'Azureus/Vuze',
                    'BI': 'BiglyBT',
                }
                
                if client_code in client_map:
                    info['name'] = client_map[client_code]
                    info['version'] = version
        except Exception:
            pass
    
    return info


def format_timestamp(dt: Any, include_ms: bool = True) -> str:
    """
    Format datetime for display
    
    Args:
        dt: datetime object or ISO string
        include_ms: Include milliseconds in output
        
    Returns:
        Formatted time string (HH:MM:SS.mmm or HH:MM:SS)
    """
    from datetime import datetime
    
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    
    if include_ms:
        return dt.strftime("%H:%M:%S.%f")[:-3]  # Remove last 3 digits of microseconds
    return dt.strftime("%H:%M:%S")

