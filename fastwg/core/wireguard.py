import base64
import ipaddress
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519

from ..models import Client, Server
from .database import Database


class WireGuardManager:
    """Main class for WireGuard server management"""

    def __init__(
        self, config_dir: str = "/etc/wireguard", keys_dir: str = "./wireguard/keys"
    ):
        self.config_dir = config_dir
        self.keys_dir = keys_dir
        self.db = Database()

        try:
            os.makedirs(self.config_dir, exist_ok=True)
            os.makedirs(self.keys_dir, exist_ok=True)
            os.makedirs("./wireguard/configs", exist_ok=True)
        except PermissionError:
            import tempfile

            temp_dir = tempfile.mkdtemp()
            self.config_dir = temp_dir
            self.keys_dir = os.path.join(temp_dir, "keys")
            os.makedirs(self.keys_dir, exist_ok=True)
            os.makedirs("./wireguard/configs", exist_ok=True)

    def check_root_privileges(self) -> bool:
        """Checks for root privileges"""
        return os.geteuid() == 0

    def _find_client_by_ip_and_key(
        self, ip_address: str, public_key: str
    ) -> Optional[Client]:
        """Finds client by IP address and public key"""
        all_clients = self.db.get_all_clients()
        for client in all_clients:
            if client.ip_address == ip_address or client.public_key == public_key:
                return client
        return None

    def scan_existing_configs(self) -> List[Dict]:
        """Scans existing WireGuard configurations"""
        existing_configs = []

        if os.path.exists(self.config_dir):
            for filename in os.listdir(self.config_dir):
                if filename.endswith(".conf"):
                    config_path = os.path.join(self.config_dir, filename)
                    try:
                        with open(config_path, "r") as f:
                            content = f.read()
                            existing_configs.append(
                                {
                                    "path": config_path,
                                    "content": content,
                                    "filename": filename,
                                }
                            )
                    except Exception as e:
                        print(f"Error reading {config_path}: {e}")

        return existing_configs

    def import_existing_config(self, config_path: str) -> bool:
        """Imports existing configuration"""
        try:
            with open(config_path, "r") as f:
                content = f.read()

            lines = content.split("\n")
            server_config: dict[str, str] = {}
            clients: list[dict[str, str]] = []

            current_section = None
            current_client: Optional[dict[str, str]] = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("[Interface]"):
                    current_section = "interface"
                    current_client = None
                elif line.startswith("[Peer]"):
                    current_section = "peer"
                    current_client = {}
                    clients.append(current_client)
                elif line.startswith("#"):
                    if current_section == "peer" and current_client is not None:
                        comment = line[1:].strip()
                        if comment and not comment.startswith(" ") and not comment.startswith("\t"):
                            current_client["Name"] = comment
                elif current_section == "interface":
                    if "=" in line:
                        key, value = line.split("=", 1)
                        server_config[key.strip()] = value.strip()
                elif current_section == "peer" and current_client is not None:
                    if "=" in line:
                        key, value = line.split("=", 1)
                        current_client[key.strip()] = value.strip()

            if not server_config:
                print("Interface section not found in config")
                return False

            private_key = server_config.get("PrivateKey", "")
            public_key = self._generate_public_key(private_key) if private_key else ""

            server = Server(
                id=None,
                interface=os.path.basename(config_path).replace(".conf", ""),
                private_key=private_key,
                public_key=public_key,
                address=server_config.get("Address", ""),
                port=int(server_config.get("ListenPort", 51820)),
                dns=server_config.get("DNS", "8.8.8.8"),
                mtu=int(server_config.get("MTU", 1420)),
                config_path=config_path,
                external_ip=None,
            )

            if not self.db.save_server_config(server):
                print("Error saving server configuration")
                return False

            host_counter = 1
            for client_data in clients:
                if "PublicKey" in client_data:
                    public_key = client_data["PublicKey"]
                    allowed_ips = client_data.get("AllowedIPs", "")
                    ip_address = allowed_ips.split("/")[0] if allowed_ips else ""

                    existing_client = self._find_client_by_ip_and_key(
                        ip_address, public_key
                    )
                    if existing_client:
                        print(f"Client with IP {ip_address} already exists, skipping")
                        continue

                    client_name = f"host_{host_counter}"
                    host_counter += 1

                    if "PrivateKey" not in client_data:
                        private_key = self._generate_private_key()
                    else:
                        private_key = client_data["PrivateKey"]

                    client = Client(
                        id=None,
                        name=client_name,
                        public_key=public_key,
                        private_key=private_key,
                        ip_address=ip_address,
                        created_at=datetime.now(),
                        is_active=True,
                        is_blocked=False,
                        last_seen=None,
                        config_path=None,
                    )

                    self.db.add_client(client)
                    print(f"Imported client: {client_name} (IP: {ip_address})")

            return True
        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False

    def create_client(self, name: str) -> Optional[Client]:
        """Creates a new client"""
        if self.db.get_client(name):
            print(f"Client {name} already exists")
            return None

        server_config = self.db.get_server_config()
        if not server_config:
            print("Server configuration not found. Run fastwg scan first to import existing configurations.")
            return None

        private_key = self._generate_private_key()
        public_key = self._generate_public_key(private_key)

        ip_address = self._get_next_ip()

        config_path = self._create_client_config(
            Client(
                id=None,
                name=name,
                public_key=public_key,
                private_key=private_key,
                ip_address=ip_address,
                created_at=datetime.now(),
                is_active=True,
                is_blocked=False,
                last_seen=None,
                config_path=None,
            )
        )

        if not config_path:
            print(f"Error creating configuration for client {name}")
            return None

        client = Client(
            id=None,
            name=name,
            public_key=public_key,
            private_key=private_key,
            ip_address=ip_address,
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None,
            config_path=config_path,
        )

        if self.db.add_client(client):
            self._update_server_config(restart=False)
            return client
        else:
            print(f"Error creating client {name}")
            return None

    def delete_client(self, name: str) -> bool:
        """Deletes a client"""
        client = self.db.get_client(name)
        if not client:
            print(f"Client {name} not found")
            return False

        self._remove_peer_from_wg(client.public_key)

        if self.db.delete_client(name):
            config_file = f"./wireguard/configs/{name}.conf"
            if os.path.exists(config_file):
                os.remove(config_file)

            self._update_server_config()
            return True
        return False

    def disable_client(self, name: str) -> bool:
        """Blocks a client"""
        client = self.db.get_client(name)
        if not client:
            print(f"Client {name} not found")
            return False

        self._remove_peer_from_wg(client.public_key)

        return self.db.update_client_status(name, is_active=False, is_blocked=True)

    def enable_client(self, name: str) -> bool:
        """Unblocks a client"""
        client = self.db.get_client(name)
        if not client:
            print(f"Client {name} not found")
            return False

        if self.db.update_client_status(name, is_active=True, is_blocked=False):
            self._update_server_config(restart=False)
            return True
        return False

    def get_client_config(self, name: str) -> Optional[str]:
        """Gets client configuration"""
        client = self.db.get_client(name)
        if not client:
            return None

        config_file = (
            client.config_path
            if client.config_path
            else f"./wireguard/configs/{name}.conf"
        )

        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                return f.read()
        return None

    def list_clients(self) -> List[Dict]:
        """Gets list of all clients with connection information"""
        clients = self.db.get_all_clients()
        active_connections = self._get_active_connections()

        result = []
        for client in clients:
            is_connected = client.public_key in active_connections

            if is_connected:
                self.db.update_client_last_seen(client.name, datetime.now())
                client.last_seen = datetime.now()

            result.append(
                {
                    "name": client.name,
                    "ip_address": client.ip_address,
                    "is_active": client.is_active,
                    "is_blocked": client.is_blocked,
                    "is_connected": is_connected,
                    "last_seen": client.last_seen,
                    "created_at": client.created_at,
                }
            )

        return result

    def _generate_private_key(self) -> str:
        """Generates WireGuard private key in base64"""
        private_key = x25519.X25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return base64.b64encode(private_bytes).decode("utf-8")

    def _generate_public_key(self, private_key_base64: str) -> str:
        """Generates public key from private key in base64"""
        private_key_bytes = base64.b64decode(private_key_base64)
        private_key = x25519.X25519PrivateKey.from_private_bytes(private_key_bytes)
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
        )
        return base64.b64encode(public_bytes).decode("utf-8")

    def _get_next_ip(self) -> str:
        """Gets next available IP address"""
        server_config = self.db.get_server_config()
        if not server_config:
            network = ipaddress.IPv4Network("10.0.0.0/24")
        else:
            server_network = ipaddress.IPv4Network(server_config.address, strict=False)
            network = ipaddress.IPv4Network(
                f"{server_network.network_address}/{server_network.prefixlen}"
            )

        existing_ips = set()
        for client in self.db.get_all_clients():
            existing_ips.add(client.ip_address)

        if server_config:
            server_ip = server_config.address.split("/")[0]
            existing_ips.add(server_ip)

        for ip in network.hosts():
            ip_str = str(ip)
            if ip_str not in existing_ips:
                return ip_str

        raise Exception("No free IP addresses in network")

    def _update_server_config(self, restart: bool = False) -> bool:
        """Updates server configuration"""
        server_config = self.db.get_server_config()
        if not server_config:
            print("Server configuration not found")
            return False

        clients = [
            c for c in self.db.get_all_clients() if c.is_active and not c.is_blocked
        ]

        config_content = f"""[Interface]
PrivateKey = {server_config.private_key}
Address = {server_config.address}
ListenPort = {server_config.port}
MTU = {server_config.mtu}

"""

        for client in clients:
            config_content += f"""[Peer]
# {client.name}
PublicKey = {client.public_key}
AllowedIPs = {client.ip_address}/32

"""

        config_path = os.path.join(self.config_dir, f"{server_config.interface}.conf")
        with open(config_path, "w") as f:
            f.write(config_content)

        os.chmod(config_path, 0o600)

        if restart:
            if not self._restart_wireguard(server_config.interface):
                print("✗ Error restarting WireGuard server")
                return False
        return True

    def _create_client_config(self, client: Client) -> str:
        """Creates client configuration file and returns file path"""
        server_config = self.db.get_server_config()
        if not server_config:
            print("Server configuration not found")
            return ""

        if not server_config.external_ip:
            print("Error: server external IP not set")
            print("Use command: fastwg sethost <ip:port>")
            return ""

        server_ip = server_config.external_ip

        private_key_file = f"./wireguard/keys/{client.name}_private.key"
        with open(private_key_file, "w") as f:
            f.write(client.private_key)
        os.chmod(private_key_file, 0o600)

        public_key_file = f"./wireguard/keys/{client.name}_public.key"
        with open(public_key_file, "w") as f:
            f.write(client.public_key)
        os.chmod(public_key_file, 0o644)

        if not server_config.public_key:
            print("Error: server public key not found")
            return ""

        config_content = f"""[Interface]
PrivateKey = {client.private_key}
Address = {client.ip_address}/24
DNS = {server_config.dns}
#
[Peer]
PublicKey = {server_config.public_key}
Endpoint = {server_ip}:{server_config.port}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 15
"""

        config_file = f"./wireguard/configs/{client.name}.conf"
        with open(config_file, "w") as f:
            f.write(config_content)

        os.chmod(config_file, 0o600)

        return config_file

    def _remove_peer_from_wg(self, public_key: str):
        """Removes peer from WireGuard interface"""
        try:
            result = subprocess.run(["wg", "show"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                current_interface = None

                for line in lines:
                    if line.startswith("interface:"):
                        current_interface = line.split(":")[1].strip()
                    elif line.startswith("peer:") and public_key in line:
                        if current_interface:
                            subprocess.run(
                                [
                                    "wg",
                                    "set",
                                    current_interface,
                                    "peer",
                                    public_key,
                                    "remove",
                                ]
                            )
                            break
        except Exception as e:
            print(f"Error removing peer: {e}")

    def _get_active_connections(self) -> set:
        """Gets list of active connections"""
        active_peers = set()
        try:
            result = subprocess.run(["wg", "show"], capture_output=True, text=True)
            if result.returncode == 0:
                active_peers = self._parse_wg_show_output(result.stdout)
        except Exception as e:
            print(f"Error getting active connections: {e}")

        return active_peers

    def _parse_wg_show_output(self, output: str) -> set:
        """Parses wg show output and returns active connections"""
        import re
        from datetime import datetime, timedelta

        active_peers = set()
        lines = output.split("\n")

        current_peer = None
        has_handshake = False
        handshake_time = None

        for line in lines:
            line = line.strip()

            if line.startswith("peer:"):
                if current_peer and self._is_peer_connected(
                    has_handshake, handshake_time
                ):
                    active_peers.add(current_peer)

                current_peer = line.split(":")[1].strip()
                has_handshake = False
                handshake_time = None

            elif line.startswith("latest handshake:") and current_peer:
                has_handshake = True
                time_str = line.split(":", 1)[1].strip()
                handshake_time = self._parse_handshake_time(time_str)

        if current_peer and self._is_peer_connected(has_handshake, handshake_time):
            active_peers.add(current_peer)

        return active_peers

    def _parse_handshake_time(self, time_str: str) -> datetime:
        """Parses handshake time string to datetime"""
        import re
        from datetime import datetime, timedelta

        time_str = time_str.replace(" ago", "")

        now = datetime.now()

        total_seconds = 0

        if "day" in time_str:
            days_match = re.search(r"(\d+)\s+days?", time_str)
            if days_match:
                total_seconds += int(days_match.group(1)) * 24 * 3600

        if "hour" in time_str:
            hours_match = re.search(r"(\d+)\s+hours?", time_str)
            if hours_match:
                total_seconds += int(hours_match.group(1)) * 3600

        if "minute" in time_str:
            minutes_match = re.search(r"(\d+)\s+minutes?", time_str)
            if minutes_match:
                total_seconds += int(minutes_match.group(1)) * 60

        if "second" in time_str:
            seconds_match = re.search(r"(\d+)\s+seconds?", time_str)
            if seconds_match:
                total_seconds += int(seconds_match.group(1))

        return now - timedelta(seconds=total_seconds)

    def _is_peer_connected(
        self, has_handshake: bool, handshake_time: Optional[datetime]
    ) -> bool:
        """Determines if peer is connected according to new logic"""
        from datetime import datetime, timedelta

        if not has_handshake:
            return False

        if handshake_time:
            time_diff = datetime.now() - handshake_time
            if time_diff > timedelta(hours=1):
                return False

        return True

    def start_server(self, interface: str = None) -> bool:
        """Starts WireGuard server"""
        try:
            if not interface:
                server_config = self.db.get_server_config()
                if not server_config:
                    print("Server configuration not found")
                    return False
                interface = server_config.interface

            result = subprocess.run(
                ["wg-quick", "up", interface], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✓ WireGuard server {interface} started")
                return True
            else:
                print(f"✗ Error starting WireGuard server: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error starting WireGuard: {e}")
            return False

    def stop_server(self, interface: str = None) -> bool:
        """Stops WireGuard server"""
        try:
            if not interface:
                server_config = self.db.get_server_config()
                if not server_config:
                    print("Server configuration not found")
                    return False
                interface = server_config.interface

            result = subprocess.run(
                ["wg-quick", "down", interface], capture_output=True, text=True
            )
            if result.returncode == 0:
                print(f"✓ WireGuard server {interface} stopped")
                return True
            else:
                print(f"✗ Error stopping WireGuard server: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error stopping WireGuard: {e}")
            return False

    def restart_server(self, interface: str = None) -> bool:
        """Restarts WireGuard server"""
        try:
            if not interface:
                server_config = self.db.get_server_config()
                if not server_config:
                    print("Server configuration not found")
                    return False
                interface = server_config.interface

            print(f"Restarting WireGuard server {interface}...")

            if not self.stop_server(interface):
                return False

            import time

            time.sleep(1)

            if not self.start_server(interface):
                return False

            print(f"✓ WireGuard server {interface} restarted")
            return True
        except Exception as e:
            print(f"Error restarting WireGuard: {e}")
            return False

    def reload_config(self) -> bool:
        """Reloads server configuration with restart"""
        try:
            server_config = self.db.get_server_config()
            if not server_config:
                print("Server configuration not found")
                return False

            if self._update_server_config(restart=True):
                print("✓ Configuration reloaded successfully")
                return True
            else:
                print("✗ Configuration reload failed")
                return False
        except Exception as e:
            print(f"Error reloading configuration: {e}")
            return False

    def init_server_config(
        self,
        interface: str = "wg0",
        port: int = 51820,
        network: str = "10.42.42.0/24",
        dns: str = "8.8.8.8",
    ) -> bool:
        """Initializes WireGuard server configuration"""
        try:
            existing_config = self.db.get_server_config()
            if existing_config:
                print("Server configuration already exists")
                return False

            private_key = self._generate_private_key()
            public_key = self._generate_public_key(private_key)

            server_config_content = f"""[Interface]
PrivateKey = {private_key}
Address = {network.replace('/24', '/24')}
ListenPort = {port}
DNS = {dns}
"""

            config_path = os.path.join(self.config_dir, f"{interface}.conf")
            with open(config_path, "w") as f:
                f.write(server_config_content)

            os.chmod(config_path, 0o600)

            server = Server(
                id=None,
                interface=interface,
                private_key=private_key,
                public_key=public_key,
                address=network,
                port=port,
                dns=dns,
                mtu=1420,
                config_path=config_path,
                external_ip=None,
            )

            if self.db.save_server_config(server):
                print(f"✓ Server configuration created: {config_path}")
                return True
            else:
                print("✗ Error saving to database")
                return False

        except Exception as e:
            print(f"Error creating server configuration: {e}")
            return False

    def set_host(self, host: str) -> bool:
        """Sets external host (IP:port) of server"""
        try:
            if ":" not in host:
                print("Error: format must be IP:port (e.g., 192.168.1.1:51820)")
                return False

            external_ip, port_str = host.split(":", 1)

            import ipaddress

            try:
                ipaddress.ip_address(external_ip)
            except ValueError:
                print(f"Error: invalid IP address: {external_ip}")
                return False

            try:
                port = int(port_str)
                if port < 1 or port > 65535:
                    raise ValueError("Port out of range")
            except ValueError:
                print(f"Error: invalid port: {port_str}")
                return False

            server_config = self.db.get_server_config()
            if not server_config:
                print("Server configuration not found")
                return False

            server_config.external_ip = external_ip
            server_config.port = port
            if self.db.save_server_config(server_config):
                print(f"✓ Server external host set: {external_ip}:{port}")
                return True
            else:
                print("✗ Error saving external host")
                return False
        except Exception as e:
            print(f"Error setting external host: {e}")
            return False

    def _restart_wireguard(self, interface: str) -> bool:
        """Restarts WireGuard interface (internal method)"""
        try:
            result_down = subprocess.run(
                ["wg-quick", "down", interface], capture_output=True, text=True
            )
            if result_down.returncode != 0 and "is not a WireGuard interface" not in result_down.stderr:
                print(f"Warning when stopping interface: {result_down.stderr}")

            result_up = subprocess.run(
                ["wg-quick", "up", interface], capture_output=True, text=True
            )
            if result_up.returncode == 0:
                return True
            else:
                print(f"✗ Error starting WireGuard interface: {result_up.stderr}")
                return False
        except Exception as e:
            print(f"Error restarting WireGuard: {e}")
            return False
