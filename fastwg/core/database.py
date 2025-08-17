import sqlite3
from datetime import datetime
from typing import List, Optional

from ..models import Client, Server


class Database:
    """Класс для работы с базой данных SQLite"""

    def __init__(self, db_path: str = "wireguard.db") -> None:
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)

        # Создаем таблицы
        Client.create_table(conn)
        Server.create_table(conn)

        conn.close()

    def get_connection(self):
        """Получает соединение с базой данных"""
        return sqlite3.connect(self.db_path)

    def add_client(self, client: Client) -> bool:
        """Добавляет клиента в базу данных"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO clients (name, public_key, private_key, ip_address, created_at, is_active, is_blocked, config_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    client.name,
                    client.public_key,
                    client.private_key,
                    client.ip_address,
                    client.created_at,
                    client.is_active,
                    client.is_blocked,
                    client.config_path,
                ),
            )

            client.id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_client(self, name: str) -> Optional[Client]:
        """Получает клиента по имени"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, public_key, private_key, ip_address, created_at, is_active, is_blocked, last_seen, config_path
            FROM clients WHERE name = ?
        """,
            (name,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return Client(
                id=row[0],
                name=row[1],
                public_key=row[2],
                private_key=row[3],
                ip_address=row[4],
                created_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                is_active=bool(row[6]),
                is_blocked=bool(row[7]),
                last_seen=datetime.fromisoformat(row[8]) if row[8] else None,
                config_path=row[9],
            )
        return None

    def get_all_clients(self) -> List[Client]:
        """Получает всех клиентов"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, public_key, private_key, ip_address, created_at, is_active, is_blocked, last_seen, config_path
            FROM clients ORDER BY name
        """
        )

        clients = []
        for row in cursor.fetchall():
            clients.append(
                Client(
                    id=row[0],
                    name=row[1],
                    public_key=row[2],
                    private_key=row[3],
                    ip_address=row[4],
                    created_at=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                    is_active=bool(row[6]),
                    is_blocked=bool(row[7]),
                    last_seen=datetime.fromisoformat(row[8]) if row[8] else None,
                    config_path=row[9],
                )
            )

        conn.close()
        return clients

    def delete_client(self, name: str) -> bool:
        """Удаляет клиента по имени"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM clients WHERE name = ?", (name,))
        deleted: bool = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

    def update_client_status(self, name: str, is_active: bool, is_blocked: bool) -> bool:
        """Обновляет статус клиента"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE clients SET is_active = ?, is_blocked = ? WHERE name = ?
        """,
            (is_active, is_blocked, name),
        )

        updated: bool = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def update_client_last_seen(self, name: str, last_seen: datetime) -> bool:
        """Обновляет время последнего подключения клиента"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE clients SET last_seen = ? WHERE name = ?
        """,
            (last_seen.isoformat(), name),
        )

        updated: bool = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    def save_server_config(self, server: Server) -> bool:
        """Сохраняет конфигурацию сервера"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO server
                (interface, private_key, public_key, address, port, dns, mtu, config_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    server.interface,
                    server.private_key,
                    server.public_key,
                    server.address,
                    server.port,
                    server.dns,
                    server.mtu,
                    server.config_path,
                ),
            )

            server.id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_server_config(self) -> Optional[Server]:
        """Получает конфигурацию сервера"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, interface, private_key, public_key, address, port, dns, mtu, config_path
            FROM server LIMIT 1
        """
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return Server(
                id=row[0],
                interface=row[1],
                private_key=row[2],
                public_key=row[3],
                address=row[4],
                port=row[5],
                dns=row[6],
                mtu=row[7],
                config_path=row[8],
            )
        return None
