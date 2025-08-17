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
    """Основной класс для управления WireGuard сервером"""

    def __init__(self, config_dir: str = "/etc/wireguard", keys_dir: str = "./wireguard/keys"):
        self.config_dir = config_dir
        self.keys_dir = keys_dir
        self.db = Database()

        # Создаем директории если не существуют
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.keys_dir, exist_ok=True)
        os.makedirs("./wireguard/configs", exist_ok=True)

    def check_root_privileges(self) -> bool:
        """Проверяет наличие root привилегий"""
        return os.geteuid() == 0

    def scan_existing_configs(self) -> List[Dict]:
        """Сканирует существующие конфигурации WireGuard"""
        existing_configs = []

        # Сканируем /etc/wireguard
        if os.path.exists(self.config_dir):
            for filename in os.listdir(self.config_dir):
                if filename.endswith(".conf"):
                    config_path = os.path.join(self.config_dir, filename)
                    try:
                        with open(config_path, "r") as f:
                            content = f.read()
                            existing_configs.append({"path": config_path, "content": content, "filename": filename})
                    except Exception as e:
                        print(f"Ошибка чтения {config_path}: {e}")

        return existing_configs

    def import_existing_config(self, config_path: str) -> bool:
        """Импортирует существующую конфигурацию"""
        try:
            with open(config_path, "r") as f:
                content = f.read()

            # Парсим конфигурацию сервера
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
                    # Сохраняем комментарии как потенциальные имена клиентов
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

            # Сохраняем конфигурацию сервера
            if server_config:
                server = Server(
                    id=None,
                    interface=os.path.basename(config_path).replace(".conf", ""),
                    private_key=server_config.get("PrivateKey", ""),
                    public_key=server_config.get("PublicKey", ""),
                    address=server_config.get("Address", ""),
                    port=int(server_config.get("ListenPort", 51820)),
                    dns=server_config.get("DNS", "8.8.8.8"),
                    mtu=int(server_config.get("MTU", 1420)),
                    config_path=config_path,
                )
                self.db.save_server_config(server)

            # Импортируем клиентов
            for i, client_data in enumerate(clients, 1):
                if "PublicKey" in client_data:
                    # Генерируем уникальное имя клиента
                    client_name = client_data.get("Name", f"imported_{i}")

                    # Проверяем, не существует ли уже клиент с таким именем
                    existing_client = self.db.get_client(client_name)
                    if existing_client:
                        # Если клиент существует, пропускаем его
                        continue

                    # Генерируем приватный ключ если нет
                    if "PrivateKey" not in client_data:
                        private_key = self._generate_private_key()
                    else:
                        private_key = client_data["PrivateKey"]

                    # Определяем IP адрес
                    allowed_ips = client_data.get("AllowedIPs", "")
                    ip_address = allowed_ips.split("/")[0] if allowed_ips else self._get_next_ip()

                    client = Client(
                        id=None,
                        name=client_name,
                        public_key=client_data["PublicKey"],
                        private_key=private_key,
                        ip_address=ip_address,
                        created_at=datetime.now(),
                        is_active=True,
                        is_blocked=False,
                        last_seen=None,
                        config_path=None,  # Для импортированных клиентов пока None
                    )

                    self.db.add_client(client)

            return True
        except Exception as e:
            print(f"Ошибка импорта конфигурации: {e}")
            return False

    def create_client(self, name: str) -> Optional[Client]:
        """Создает нового клиента"""
        # Проверяем что клиент не существует
        if self.db.get_client(name):
            print(f"Клиент {name} уже существует")
            return None

        # Генерируем ключи
        private_key = self._generate_private_key()
        public_key = self._generate_public_key(private_key)

        # Получаем следующий свободный IP
        ip_address = self._get_next_ip()

        # Создаем конфигурационный файл клиента
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
                config_path=None,  # Временно None
            )
        )

        if not config_path:
            print(f"Ошибка создания конфигурации для клиента {name}")
            return None

        # Создаем клиента с путем к конфигу
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

        # Сохраняем в базу
        if self.db.add_client(client):
            # Обновляем конфигурацию сервера (без перезапуска)
            self._update_server_config(restart=False)
            return client
        else:
            print(f"Ошибка создания клиента {name}")
            return None

    def delete_client(self, name: str) -> bool:
        """Удаляет клиента"""
        client = self.db.get_client(name)
        if not client:
            print(f"Клиент {name} не найден")
            return False

        # Удаляем из WireGuard
        self._remove_peer_from_wg(client.public_key)

        # Удаляем из базы данных
        if self.db.delete_client(name):
            # Удаляем конфигурационный файл
            config_file = f"./wireguard/configs/{name}.conf"
            if os.path.exists(config_file):
                os.remove(config_file)

            # Обновляем конфигурацию сервера
            self._update_server_config()
            return True
        return False

    def disable_client(self, name: str) -> bool:
        """Блокирует клиента"""
        client = self.db.get_client(name)
        if not client:
            print(f"Клиент {name} не найден")
            return False

        # Удаляем из WireGuard
        self._remove_peer_from_wg(client.public_key)

        # Обновляем статус в базе
        return self.db.update_client_status(name, is_active=False, is_blocked=True)

    def enable_client(self, name: str) -> bool:
        """Разблокирует клиента"""
        client = self.db.get_client(name)
        if not client:
            print(f"Клиент {name} не найден")
            return False

        # Обновляем статус в базе
        if self.db.update_client_status(name, is_active=True, is_blocked=False):
            # Обновляем конфигурацию сервера (без перезапуска)
            self._update_server_config(restart=False)
            return True
        return False

    def get_client_config(self, name: str) -> Optional[str]:
        """Получает конфигурацию клиента"""
        client = self.db.get_client(name)
        if not client:
            return None

        # Используем путь из БД, если есть
        config_file = client.config_path if client.config_path else f"./wireguard/configs/{name}.conf"

        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                return f.read()
        return None

    def list_clients(self) -> List[Dict]:
        """Получает список всех клиентов с информацией о подключениях"""
        clients = self.db.get_all_clients()
        active_connections = self._get_active_connections()

        result = []
        for client in clients:
            is_connected = client.public_key in active_connections

            # Обновляем last_seen для подключенных клиентов
            if is_connected:
                self.db.update_client_last_seen(client.name, datetime.now())
                # Обновляем объект клиента для отображения
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
        """Генерирует приватный ключ WireGuard"""
        private_key = x25519.X25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return str(private_bytes.hex())

    def _generate_public_key(self, private_key_hex: str) -> str:
        """Генерирует публичный ключ из приватного"""
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key = x25519.X25519PrivateKey.from_private_bytes(private_key_bytes)
        public_key = private_key.public_key()
        public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
        return str(public_bytes.hex())

    def _get_next_ip(self) -> str:
        """Получает следующий свободный IP адрес"""
        server_config = self.db.get_server_config()
        if not server_config:
            # Если нет сервера, используем дефолтную сеть
            network = ipaddress.IPv4Network("10.0.0.0/24")
        else:
            # Создаем сеть из адреса сервера, убирая host bits
            server_network = ipaddress.IPv4Network(server_config.address, strict=False)
            network = ipaddress.IPv4Network(f"{server_network.network_address}/{server_network.prefixlen}")

        # Получаем все существующие IP
        existing_ips = set()
        for client in self.db.get_all_clients():
            existing_ips.add(client.ip_address)

        # Добавляем IP сервера в исключения
        if server_config:
            server_ip = server_config.address.split("/")[0]  # Убираем маску
            existing_ips.add(server_ip)

        # Ищем свободный IP
        for ip in network.hosts():
            ip_str = str(ip)
            if ip_str not in existing_ips:
                return ip_str

        raise Exception("Нет свободных IP адресов в сети")

    def _update_server_config(self, restart: bool = False):
        """Обновляет конфигурацию сервера"""
        server_config = self.db.get_server_config()
        if not server_config:
            print("Конфигурация сервера не найдена")
            return

        # Получаем активных клиентов
        clients = [c for c in self.db.get_all_clients() if c.is_active and not c.is_blocked]

        # Формируем конфигурацию
        config_content = f"""[Interface]
PrivateKey = {server_config.private_key}
Address = {server_config.address}
ListenPort = {server_config.port}
MTU = {server_config.mtu}

"""

        # Добавляем клиентов
        for client in clients:
            config_content += f"""[Peer]
# {client.name}
PublicKey = {client.public_key}
AllowedIPs = {client.ip_address}/32

"""

        # Записываем конфигурацию
        config_path = os.path.join(self.config_dir, f"{server_config.interface}.conf")
        with open(config_path, "w") as f:
            f.write(config_content)

        # Устанавливаем правильные права
        os.chmod(config_path, 0o600)

        # Перезапускаем WireGuard только если явно запрошено
        if restart:
            self._restart_wireguard(server_config.interface)

    def _create_client_config(self, client: Client) -> str:
        """Создает конфигурационный файл для клиента и возвращает путь к файлу"""
        server_config = self.db.get_server_config()
        if not server_config:
            print("Конфигурация сервера не найдена")
            return ""

        # Получаем IP сервера
        server_ip = server_config.address.split("/")[0]  # Убираем маску

        # Сохраняем приватный ключ клиента
        private_key_file = f"./wireguard/keys/{client.name}_private.key"
        with open(private_key_file, "w") as f:
            f.write(client.private_key)
        os.chmod(private_key_file, 0o600)

        # Сохраняем публичный ключ клиента
        public_key_file = f"./wireguard/keys/{client.name}_public.key"
        with open(public_key_file, "w") as f:
            f.write(client.public_key)
        os.chmod(public_key_file, 0o644)

        # Создаем конфигурацию клиента
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

        # Устанавливаем правильные права
        os.chmod(config_file, 0o600)

        return config_file

    def _remove_peer_from_wg(self, public_key: str):
        """Удаляет peer из WireGuard интерфейса"""
        try:
            # Получаем список peers
            result = subprocess.run(["wg", "show"], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                current_interface = None

                for line in lines:
                    if line.startswith("interface:"):
                        current_interface = line.split(":")[1].strip()
                    elif line.startswith("peer:") and public_key in line:
                        if current_interface:
                            # Удаляем peer
                            subprocess.run(["wg", "set", current_interface, "peer", public_key, "remove"])
                            break
        except Exception as e:
            print(f"Ошибка удаления peer: {e}")

    def _get_active_connections(self) -> set:
        """Получает список активных подключений"""
        active_peers = set()
        try:
            result = subprocess.run(["wg", "show"], capture_output=True, text=True)
            if result.returncode == 0:
                active_peers = self._parse_wg_show_output(result.stdout)
        except Exception as e:
            print(f"Ошибка получения активных подключений: {e}")

        return active_peers

    def _parse_wg_show_output(self, output: str) -> set:
        """Парсит вывод wg show и возвращает активные подключения"""
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
                # Проверяем предыдущий peer
                if current_peer and self._is_peer_connected(has_handshake, handshake_time):
                    active_peers.add(current_peer)

                # Начинаем новый peer
                current_peer = line.split(":")[1].strip()
                has_handshake = False
                handshake_time = None

            elif line.startswith("latest handshake:") and current_peer:
                has_handshake = True
                time_str = line.split(":", 1)[1].strip()
                handshake_time = self._parse_handshake_time(time_str)

        # Проверяем последний peer
        if current_peer and self._is_peer_connected(has_handshake, handshake_time):
            active_peers.add(current_peer)

        return active_peers

    def _parse_handshake_time(self, time_str: str) -> datetime:
        """Парсит строку времени handshake в datetime"""
        import re
        from datetime import datetime, timedelta

        # Убираем " ago" в конце
        time_str = time_str.replace(" ago", "")

        # Получаем текущее время
        now = datetime.now()

        # Парсим компоненты времени
        total_seconds = 0

        # Дни
        if "day" in time_str:
            days_match = re.search(r"(\d+)\s+days?", time_str)
            if days_match:
                total_seconds += int(days_match.group(1)) * 24 * 3600

        # Часы
        if "hour" in time_str:
            hours_match = re.search(r"(\d+)\s+hours?", time_str)
            if hours_match:
                total_seconds += int(hours_match.group(1)) * 3600

        # Минуты
        if "minute" in time_str:
            minutes_match = re.search(r"(\d+)\s+minutes?", time_str)
            if minutes_match:
                total_seconds += int(minutes_match.group(1)) * 60

        # Секунды
        if "second" in time_str:
            seconds_match = re.search(r"(\d+)\s+seconds?", time_str)
            if seconds_match:
                total_seconds += int(seconds_match.group(1))

        return now - timedelta(seconds=total_seconds)

    def _is_peer_connected(self, has_handshake: bool, handshake_time: Optional[datetime]) -> bool:
        """Определяет, подключен ли peer согласно новой логике"""
        from datetime import datetime, timedelta

        # 1. Если не было handshake - не подключен
        if not has_handshake:
            return False

        # 2. Если handshake больше часа назад - не активен
        if handshake_time:
            time_diff = datetime.now() - handshake_time
            if time_diff > timedelta(hours=1):
                return False

        # 3. В остальных случаях - активен
        return True

    def start_server(self, interface: str = None) -> bool:
        """Запускает WireGuard сервер"""
        try:
            if not interface:
                server_config = self.db.get_server_config()
                if not server_config:
                    print("Конфигурация сервера не найдена")
                    return False
                interface = server_config.interface

            result = subprocess.run(["wg-quick", "up", interface], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ WireGuard сервер {interface} запущен")
                return True
            else:
                print(f"✗ Ошибка запуска WireGuard сервера: {result.stderr}")
                return False
        except Exception as e:
            print(f"Ошибка запуска WireGuard: {e}")
            return False

    def stop_server(self, interface: str = None) -> bool:
        """Останавливает WireGuard сервер"""
        try:
            if not interface:
                server_config = self.db.get_server_config()
                if not server_config:
                    print("Конфигурация сервера не найдена")
                    return False
                interface = server_config.interface

            result = subprocess.run(["wg-quick", "down", interface], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ WireGuard сервер {interface} остановлен")
                return True
            else:
                print(f"✗ Ошибка остановки WireGuard сервера: {result.stderr}")
                return False
        except Exception as e:
            print(f"Ошибка остановки WireGuard: {e}")
            return False

    def restart_server(self, interface: str = None) -> bool:
        """Перезапускает WireGuard сервер"""
        try:
            if not interface:
                server_config = self.db.get_server_config()
                if not server_config:
                    print("Конфигурация сервера не найдена")
                    return False
                interface = server_config.interface

            print(f"Перезапуск WireGuard сервера {interface}...")

            # Останавливаем сервер
            if not self.stop_server(interface):
                return False

            # Небольшая пауза
            import time

            time.sleep(1)

            # Запускаем сервер
            if not self.start_server(interface):
                return False

            print(f"✓ WireGuard сервер {interface} перезапущен")
            return True
        except Exception as e:
            print(f"Ошибка перезапуска WireGuard: {e}")
            return False

    def reload_config(self) -> bool:
        """Перезагружает конфигурацию сервера с перезапуском"""
        try:
            server_config = self.db.get_server_config()
            if not server_config:
                print("Конфигурация сервера не найдена")
                return False

            # Обновляем конфигурацию с перезапуском
            self._update_server_config(restart=True)
            return True
        except Exception as e:
            print(f"Ошибка перезагрузки конфигурации: {e}")
            return False

    def _restart_wireguard(self, interface: str) -> None:
        """Перезапускает WireGuard интерфейс (внутренний метод)"""
        try:
            # Останавливаем интерфейс
            subprocess.run(["wg-quick", "down", interface], check=False)
            # Запускаем интерфейс
            subprocess.run(["wg-quick", "up", interface], check=False)
        except Exception as e:
            print(f"Ошибка перезапуска WireGuard: {e}")
