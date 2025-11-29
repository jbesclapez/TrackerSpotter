"""
Data models for TrackerSpotter announce events
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class AnnounceEvent:
    """Represents a single announce event from a torrent client"""
    
    id: Optional[int] = None
    timestamp: datetime = None
    info_hash: str = ""
    info_hash_hex: str = ""
    peer_id: str = ""
    client_ip: str = ""
    client_port: int = 0
    uploaded: int = 0
    downloaded: int = 0
    left: int = 0
    event: str = ""  # started, completed, stopped, or empty for update
    user_agent: str = ""
    numwant: int = 50
    compact: int = 1
    key: str = ""
    raw_query: str = ""
    raw_headers: str = ""  # Raw HTTP headers as-is for client file making
    
    def __post_init__(self):
        """Set timestamp if not provided"""
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime to ISO format string
        if isinstance(data['timestamp'], datetime):
            data['timestamp'] = data['timestamp'].isoformat()
        return data
    
    @property
    def event_type(self) -> str:
        """Return friendly event type"""
        if not self.event:
            return "update"
        return self.event.lower()
    
    @property
    def torrent_name(self) -> str:
        """Return shortened info hash for display"""
        return f"{self.info_hash_hex[:8]}..." if len(self.info_hash_hex) > 8 else self.info_hash_hex
    
    @property
    def progress_percent(self) -> float:
        """Calculate download progress percentage"""
        total = self.downloaded + self.left
        if total == 0:
            return 100.0 if self.left == 0 else 0.0
        return (self.downloaded / total) * 100.0
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    @property
    def downloaded_formatted(self) -> str:
        """Formatted download amount"""
        return self.format_bytes(self.downloaded)
    
    @property
    def uploaded_formatted(self) -> str:
        """Formatted upload amount"""
        return self.format_bytes(self.uploaded)
    
    @property
    def left_formatted(self) -> str:
        """Formatted remaining amount"""
        return self.format_bytes(self.left)

