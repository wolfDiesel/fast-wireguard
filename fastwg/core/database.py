import sqlite3
from datetime import datetime
from typing import List, Optional

from ..models import Client, Server


class Database:
    """SQLite database management class"""

    def __init__(self, db_path: str = "wireguard.db") -> None:
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initializes database"""
        conn = sqlite3.connect(self.db_path)

        Client.create_table(conn)
        Server.create_table(conn)

        self._migrate_database(conn)

        conn.close()

    def _migrate_database(self, conn: sqlite3.Connection) -> None:
        """Migrates database if needed"""
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT config_path FROM clients LIMIT 1")
        except sqlite3.OperationalError:
            try:
                print("DB migration: adding config_path column...")
                cursor.execute("ALTER TABLE clients ADD COLUMN config_path TEXT")
                conn.commit()
                print("✓ Migration completed")
            except sqlite3.OperationalError as e:
                if "readonly" in str(e).lower():
                    print("Migration skipped (readonly DB)")
                else:
                    raise

        try:
            cursor.execute("SELECT external_ip FROM server LIMIT 1")
        except sqlite3.OperationalError:
            try:
                print("DB migration: adding external_ip column...")
                cursor.execute("ALTER TABLE server ADD COLUMN external_ip TEXT")
                conn.commit()
                print("✓ external_ip migration completed")
            except sqlite3.OperationalError as e:
                if "readonly" in str(e).lower():
                    print("external_ip migration skipped (readonly DB)")
                else:
                    raise

    def get_connection(self):
        """Gets database connection"""
        return sqlite3.connect(self.db_path)

    def add_client(self, client: Client) -> bool:
        """Adds client to database"""
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
        """Gets client by name"""
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
        """Gets all clients"""
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
                    created_at=(
                        datetime.fromisoformat(row[5]) if row[5] else datetime.now()
                    ),
                    is_active=bool(row[6]),
                    is_blocked=bool(row[7]),
                    last_seen=datetime.fromisoformat(row[8]) if row[8] else None,
                    config_path=row[9],
                )
            )

        conn.close()
        return clients

    def delete_client(self, name: str) -> bool:
        """Deletes client by name"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM clients WHERE name = ?", (name,))
        deleted: bool = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return deleted

    def update_client_status(
        self, name: str, is_active: bool, is_blocked: bool
    ) -> bool:
        """Updates client status"""
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
        """Updates client last seen time"""
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
        """Saves server configuration"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO server
                (interface, private_key, public_key, address, port, dns, mtu, config_path, external_ip)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    server.external_ip,
                ),
            )

            server.id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def get_server_config(self) -> Optional[Server]:
        """Gets server configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, interface, private_key, public_key, address, port, dns, mtu, config_path, external_ip
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
                external_ip=row[9],
            )
        return None
