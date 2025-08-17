import os
import subprocess
import ipaddress
from typing import List, Optional, Dict
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.backends import default_backend
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
                if filename.endswith('.conf'):
                    config_path = os.path.join(self.config_dir, filename)
                    try:
                        with open(config_path, 'r') as f:
                            content = f.read()
                            existing_configs.append({
                                'path': config_path,
                                'content': content,
                                'filename': filename
                            })
                    except Exception as e:
                        print(f"Ошибка чтения {config_path}: {e}")
        
        return existing_configs
    
    def import_existing_config(self, config_path: str) -> bool:
        """Импортирует существующую конфигурацию"""
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Парсим конфигурацию сервера
            lines = content.split('\n')
            server_config = {}
            clients = []
            
            current_section = None
            current_client = None
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('[Interface]'):
                    current_section = 'interface'
                    current_client = None
                elif line.startswith('[Peer]'):
                    current_section = 'peer'
                    current_client = {}
                    clients.append(current_client)
                elif current_section == 'interface':
                    if '=' in line:
                        key, value = line.split('=', 1)
                        server_config[key.strip()] = value.strip()
                elif current_section == 'peer' and current_client is not None:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        current_client[key.strip()] = value.strip()
            
            # Сохраняем конфигурацию сервера
            if server_config:
                server = Server(
                    id=None,
                    interface=os.path.basename(config_path).replace('.conf', ''),
                    private_key=server_config.get('PrivateKey', ''),
                    public_key=server_config.get('PublicKey', ''),
                    address=server_config.get('Address', ''),
                    port=int(server_config.get('ListenPort', 51820)),
                    dns=server_config.get('DNS', '8.8.8.8'),
                    mtu=int(server_config.get('MTU', 1420)),
                    config_path=config_path
                )
                self.db.save_server_config(server)
            
            # Импортируем клиентов
            for client_data in clients:
                if 'PublicKey' in client_data:
                    # Генерируем имя клиента если нет
                    client_name = client_data.get('Name', f"imported_{len(clients)}")
                    
                    # Генерируем приватный ключ если нет
                    if 'PrivateKey' not in client_data:
                        private_key = self._generate_private_key()
                    else:
                        private_key = client_data['PrivateKey']
                    
                    # Определяем IP адрес
                    allowed_ips = client_data.get('AllowedIPs', '')
                    ip_address = allowed_ips.split('/')[0] if allowed_ips else self._get_next_ip()
                    
                    client = Client(
                        id=None,
                        name=client_name,
                        public_key=client_data['PublicKey'],
                        private_key=private_key,
                        ip_address=ip_address,
                        created_at=datetime.now(),
                        is_active=True,
                        is_blocked=False,
                        last_seen=None
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
        
        # Создаем клиента
        client = Client(
            id=None,
            name=name,
            public_key=public_key,
            private_key=private_key,
            ip_address=ip_address,
            created_at=datetime.now(),
            is_active=True,
            is_blocked=False,
            last_seen=None
        )
        
        # Сохраняем в базу
        if self.db.add_client(client):
            # Обновляем конфигурацию сервера
            self._update_server_config()
            # Создаем конфигурационный файл клиента
            self._create_client_config(client)
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
            # Обновляем конфигурацию сервера
            self._update_server_config()
            return True
        return False
    
    def get_client_config(self, name: str) -> Optional[str]:
        """Получает конфигурацию клиента"""
        client = self.db.get_client(name)
        if not client:
            return None
        
        config_file = f"./wireguard/configs/{name}.conf"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return f.read()
        return None
    
    def list_clients(self) -> List[Dict]:
        """Получает список всех клиентов с информацией о подключениях"""
        clients = self.db.get_all_clients()
        active_connections = self._get_active_connections()
        
        result = []
        for client in clients:
            is_connected = client.public_key in active_connections
            result.append({
                'name': client.name,
                'ip_address': client.ip_address,
                'is_active': client.is_active,
                'is_blocked': client.is_blocked,
                'is_connected': is_connected,
                'last_seen': client.last_seen,
                'created_at': client.created_at
            })
        
        return result
    
    def _generate_private_key(self) -> str:
        """Генерирует приватный ключ WireGuard"""
        private_key = x25519.X25519PrivateKey.generate()
        return private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        ).hex()
    
    def _generate_public_key(self, private_key_hex: str) -> str:
        """Генерирует публичный ключ из приватного"""
        private_key_bytes = bytes.fromhex(private_key_hex)
        private_key = x25519.X25519PrivateKey.from_private_bytes(private_key_bytes)
        public_key = private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
    
    def _get_next_ip(self) -> str:
        """Получает следующий свободный IP адрес"""
        server_config = self.db.get_server_config()
        if not server_config:
            # Если нет сервера, используем дефолтную сеть
            network = ipaddress.IPv4Network('10.0.0.0/24')
        else:
            network = ipaddress.IPv4Network(server_config.address)
        
        # Получаем все существующие IP
        existing_ips = set()
        for client in self.db.get_all_clients():
            existing_ips.add(client.ip_address)
        
        # Ищем свободный IP
        for ip in network.hosts():
            ip_str = str(ip)
            if ip_str not in existing_ips:
                return ip_str
        
        raise Exception("Нет свободных IP адресов в сети")
    
    def _update_server_config(self):
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
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        # Устанавливаем правильные права
        os.chmod(config_path, 0o600)
        
        # Перезапускаем WireGuard
        self._restart_wireguard(server_config.interface)
    
    def _create_client_config(self, client: Client):
        """Создает конфигурационный файл для клиента"""
        server_config = self.db.get_server_config()
        if not server_config:
            print("Конфигурация сервера не найдена")
            return
        
        config_content = f"""[Interface]
PrivateKey = {client.private_key}
Address = {client.ip_address}
DNS = {server_config.dns}
MTU = {server_config.mtu}

[Peer]
PublicKey = {server_config.public_key}
Endpoint = :{server_config.port}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
        
        config_file = f"./wireguard/configs/{client.name}.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Устанавливаем правильные права
        os.chmod(config_file, 0o600)
    
    def _remove_peer_from_wg(self, public_key: str):
        """Удаляет peer из WireGuard интерфейса"""
        try:
            # Получаем список peers
            result = subprocess.run(['wg', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_interface = None
                
                for line in lines:
                    if line.startswith('interface:'):
                        current_interface = line.split(':')[1].strip()
                    elif line.startswith('peer:') and public_key in line:
                        if current_interface:
                            # Удаляем peer
                            subprocess.run(['wg', 'set', current_interface, 'peer', public_key, 'remove'])
                            break
        except Exception as e:
            print(f"Ошибка удаления peer: {e}")
    
    def _get_active_connections(self) -> set:
        """Получает список активных подключений"""
        active_peers = set()
        try:
            result = subprocess.run(['wg', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.startswith('peer:'):
                        peer_key = line.split(':')[1].strip()
                        active_peers.add(peer_key)
        except Exception as e:
            print(f"Ошибка получения активных подключений: {e}")
        
        return active_peers
    
    def _restart_wireguard(self, interface: str):
        """Перезапускает WireGuard интерфейс"""
        try:
            # Останавливаем интерфейс
            subprocess.run(['wg-quick', 'down', interface], check=False)
            # Запускаем интерфейс
            subprocess.run(['wg-quick', 'up', interface], check=False)
        except Exception as e:
            print(f"Ошибка перезапуска WireGuard: {e}")
