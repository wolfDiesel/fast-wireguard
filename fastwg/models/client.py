import sqlite3
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class Client:
    """WireGuard client model"""

    id: Optional[int]
    name: str
    public_key: str
    private_key: str
    ip_address: str
    created_at: datetime
    is_active: bool
    is_blocked: bool
    last_seen: Optional[datetime]
    config_path: Optional[str]

    @classmethod
    def create_table(cls, conn: sqlite3.Connection) -> None:
        """Creates clients table in database"""
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                public_key TEXT UNIQUE NOT NULL,
                private_key TEXT NOT NULL,
                ip_address TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                is_blocked BOOLEAN DEFAULT FALSE,
                last_seen TIMESTAMP,
                config_path TEXT
            )
        """
        )
        conn.commit()

    def to_dict(self) -> dict[str, Any]:
        """Converts client to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "public_key": self.public_key,
            "private_key": self.private_key,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
            "is_blocked": self.is_blocked,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "config_path": self.config_path,
        }
