"""
Database operations for TrackerSpotter using SQLite
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from .models import AnnounceEvent


class Database:
    """SQLite database manager for announce events"""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file (default: trackerspotter.db in user's home)
        """
        if db_path is None:
            # Store in user's AppData on Windows
            if Path.home().exists():
                app_data = Path.home() / "AppData" / "Local" / "TrackerSpotter"
                app_data.mkdir(parents=True, exist_ok=True)
                db_path = str(app_data / "trackerspotter.db")
            else:
                db_path = "trackerspotter.db"
        
        self.db_path = db_path
        self._create_tables()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS announces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    info_hash BLOB NOT NULL,
                    info_hash_hex TEXT NOT NULL,
                    peer_id TEXT NOT NULL,
                    client_ip TEXT NOT NULL,
                    client_port INTEGER NOT NULL,
                    uploaded INTEGER NOT NULL,
                    downloaded INTEGER NOT NULL,
                    left INTEGER NOT NULL,
                    event TEXT NOT NULL,
                    user_agent TEXT,
                    numwant INTEGER,
                    compact INTEGER,
                    key TEXT,
                    raw_query TEXT
                )
            """)
            
            # Create indices for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON announces(timestamp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_info_hash 
                ON announces(info_hash_hex)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_event 
                ON announces(event)
            """)
    
    def insert_announce(self, event: AnnounceEvent) -> int:
        """
        Insert a new announce event
        
        Args:
            event: AnnounceEvent object
            
        Returns:
            ID of inserted row
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO announces (
                    timestamp, info_hash, info_hash_hex, peer_id,
                    client_ip, client_port, uploaded, downloaded, left,
                    event, user_agent, numwant, compact, key, raw_query
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.timestamp.isoformat(),
                event.info_hash.encode() if isinstance(event.info_hash, str) else event.info_hash,
                event.info_hash_hex,
                event.peer_id,
                event.client_ip,
                event.client_port,
                event.uploaded,
                event.downloaded,
                event.left,
                event.event,
                event.user_agent,
                event.numwant,
                event.compact,
                event.key,
                event.raw_query
            ))
            return cursor.lastrowid
    
    def get_recent_announces(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get most recent announce events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of announce event dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM announces
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor.fetchall():
                event_dict = dict(row)
                # Convert BLOB to hex string if it's bytes
                if isinstance(event_dict.get('info_hash'), bytes):
                    event_dict['info_hash'] = event_dict['info_hash'].hex()
                results.append(event_dict)
            
            return results
    
    def get_announces_by_filter(
        self,
        event_type: Optional[str] = None,
        info_hash: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        search: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get announces with optional filters
        
        Args:
            event_type: Filter by event type (started, completed, stopped, or empty for updates)
            info_hash: Filter by info hash (hex)
            start_time: Filter events after this time
            end_time: Filter events before this time
            search: Search in info_hash_hex, client_ip, or user_agent
            limit: Maximum results
            
        Returns:
            List of announce event dictionaries
        """
        query = "SELECT * FROM announces WHERE 1=1"
        params = []
        
        if event_type is not None:
            query += " AND event = ?"
            params.append(event_type)
        
        if info_hash:
            query += " AND info_hash_hex = ?"
            params.append(info_hash)
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        if search:
            query += " AND (info_hash_hex LIKE ? OR client_ip LIKE ? OR user_agent LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                event_dict = dict(row)
                # Convert BLOB to hex string if it's bytes
                if isinstance(event_dict.get('info_hash'), bytes):
                    event_dict['info_hash'] = event_dict['info_hash'].hex()
                results.append(event_dict)
            
            return results
    
    def get_unique_torrents(self) -> List[Dict[str, str]]:
        """
        Get list of unique torrents (info hashes) that have been announced
        
        Returns:
            List of dictionaries with info_hash_hex and count
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT info_hash_hex, COUNT(*) as count
                FROM announces
                GROUP BY info_hash_hex
                ORDER BY MAX(timestamp) DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_event_counts(self) -> Dict[str, int]:
        """
        Get count of events by type
        
        Returns:
            Dictionary mapping event type to count
        """
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT event, COUNT(*) as count
                FROM announces
                GROUP BY event
            """)
            
            result = {row['event'] if row['event'] else 'update': row['count'] 
                     for row in cursor.fetchall()}
            return result
    
    def delete_old_announces(self, days: int = 7) -> int:
        """
        Delete announces older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            Number of deleted rows
        """
        cutoff = datetime.now() - timedelta(days=days)
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM announces
                WHERE timestamp < ?
            """, (cutoff.isoformat(),))
            return cursor.rowcount
    
    def clear_all_announces(self) -> int:
        """
        Delete all announce events
        
        Returns:
            Number of deleted rows
        """
        with self.get_connection() as conn:
            cursor = conn.execute("DELETE FROM announces")
            return cursor.rowcount
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with total events, unique torrents, date range
        """
        with self.get_connection() as conn:
            # Total events
            cursor = conn.execute("SELECT COUNT(*) as total FROM announces")
            total = cursor.fetchone()['total']
            
            # Unique torrents
            cursor = conn.execute("SELECT COUNT(DISTINCT info_hash_hex) as unique_torrents FROM announces")
            unique = cursor.fetchone()['unique_torrents']
            
            # Date range
            cursor = conn.execute("""
                SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest
                FROM announces
            """)
            dates = cursor.fetchone()
            
            return {
                'total_events': total,
                'unique_torrents': unique,
                'earliest_event': dates['earliest'],
                'latest_event': dates['latest']
            }

