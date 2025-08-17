import sqlite3
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Server:
    """Модель сервера WireGuard"""

    id: Optional[int]
    interface: str
    private_key: str
    public_key: str
    address: str
    port: int
    dns: str
    mtu: int
    config_path: str
    external_ip: Optional[str]

    @classmethod
    def create_table(cls, conn: sqlite3.Connection) -> None:
        """Создает таблицу сервера в базе данных"""
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS server (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface TEXT UNIQUE NOT NULL,
                private_key TEXT NOT NULL,
                public_key TEXT NOT NULL,
                address TEXT NOT NULL,
                port INTEGER NOT NULL,
                dns TEXT NOT NULL,
                mtu INTEGER DEFAULT 1420,
                config_path TEXT NOT NULL,
                external_ip TEXT
            )
        """
        )
        conn.commit()

    def to_dict(self) -> dict[str, Any]:
        """Преобразует сервер в словарь"""
        return {
            "id": self.id,
            "interface": self.interface,
            "private_key": self.private_key,
            "public_key": self.public_key,
            "address": self.address,
            "port": self.port,
            "dns": self.dns,
            "mtu": self.mtu,
            "config_path": self.config_path,
            "external_ip": self.external_ip,
        }
