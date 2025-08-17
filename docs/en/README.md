# Fast WireGuard

Fast and simple WireGuard server management through CLI interface.

## Features

- 🚀 Quick creation and management of WireGuard configurations
- 📱 Generation of client configuration files
- 🔐 Secure key storage in SQLite database
- 🔍 Scanning and importing existing configurations
- 📊 Monitoring of active connections
- 🔄 Automatic server configuration updates
- 🛡️ Client blocking/unblocking
- 📋 Convenient CLI interface with colored output

## Installation

### Method 1: Automatic installation (recommended)

```bash
# Download and run the installer
curl -sSL https://raw.githubusercontent.com/wolfDiesel/fast-wireguard/main/install.sh | sudo bash
```

### Method 2: Manual installation via pip

1. Clone the repository:
```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the utility system-wide:
```bash
sudo pip install -e .
```

After installation, the `fastwg` command will be available globally.

### Method 3: Installation via setup.py

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
sudo python setup.py install
```

### Method 4: Package creation and installation

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# Create distribution
python setup.py sdist bdist_wheel

# Install the created package
sudo pip install dist/fastwg-1.0.0.tar.gz
```

### Installation verification

```bash
# Check if command is available
fastwg --version

# Check help
fastwg --help

# Check installation location
which fastwg
```

## Usage

**Important:** All commands require root privileges (sudo).

### First-time setup

After installation, you need to either scan existing configurations or create a new server from scratch:

#### Option 1: Scan existing WireGuard configurations
If you already have WireGuard server configurations:

```bash
# Scan and import existing configurations
sudo fastwg scan
```

#### Option 2: Create server from scratch
If you want to set up a new WireGuard server:

```bash
# Initialize server configuration
sudo fastwg init-server

# Set external host (your server's public IP and port)
sudo fastwg sethost YOUR_PUBLIC_IP:51820

# Start the server
sudo fastwg start
```

### Basic commands

```bash
# Initialize server configuration (create from scratch)
sudo fastwg init-server

# Set external host (IP:port)
sudo fastwg sethost IP:PORT

# Scan existing configurations
sudo fastwg scan

# Create new client
sudo fastwg create client_name

# Delete client
sudo fastwg delete client_name

# Disable client
sudo fastwg disable client_name

# Enable client
sudo fastwg enable client_name

# Show client configuration
sudo fastwg cat client_name

# List all clients
sudo fastwg list

# List all clients (including inactive/blocked)
sudo fastwg list --all

# WireGuard server status
sudo fastwg status

# Start WireGuard server
sudo fastwg start

# Stop WireGuard server
sudo fastwg stop

# Restart WireGuard server
sudo fastwg restart

# Reload server configuration
sudo fastwg reload
```

### Usage examples

#### Setting up a new server from scratch

```bash
# Initialize server configuration
sudo fastwg init-server
# ✓ Server configuration initialized successfully
#   Interface: wg0
#   Port: 51820
#   Network: 10.42.42.0/24
#   DNS: 8.8.8.8
#
# Next steps:
#   1. Set external host: fastwg sethost <your_ip>:<port>
#   2. Start server: fastwg start
#   3. Create clients: fastwg create <client_name>

# Set external host
sudo fastwg sethost 203.0.113.1:51820
# ✓ Host set successfully

# Start the server
sudo fastwg start
# ✓ Server started successfully
```

#### Creating and managing clients

```bash
# Creating a client
sudo fastwg create john
# ✓ Client 'john' successfully created
#   IP address: 10.42.42.2
#   Configuration: ./wireguard/configs/john.conf

# Viewing client list
sudo fastwg list
# +--------+------------+----------------------+----------------------+----------------------+
# | Name   | IP Address | Status               | Last Connection     | Created             |
# +--------+------------+----------------------+----------------------+----------------------+
# | john   | 10.42.42.2 | Active, Connected    | 2024-01-15 14:30:25 | 2024-01-15 14:25:10 |
# +--------+------------+----------------------+----------------------+----------------------+

# Viewing client configuration
sudo fastwg cat john
# [Interface]
# PrivateKey = abc123...
# Address = 10.42.42.2/24
# DNS = 8.8.8.8
# 
# [Peer]
# PublicKey = xyz789...
# Endpoint = 203.0.113.1:51820
# AllowedIPs = 0.0.0.0/0
# PersistentKeepalive = 15
```

#### Server management

```bash
# Check server status
sudo fastwg status
# ✓ WireGuard is active
# Active interfaces:
# interface: wg0
#   public key: xyz789...
#   private key: (hidden)
#   listening port: 51820

# Restart server
sudo fastwg restart
# ✓ Server restarted successfully

# Reload configuration
sudo fastwg reload
# ✓ Configuration reloaded successfully
```

## File locations

### Client configurations and keys
All client configurations and keys are stored in the project directory:

- **Client configurations**: `./wireguard/configs/` (e.g., `./wireguard/configs/john.conf`)
- **Client private keys**: `./wireguard/keys/` (e.g., `./wireguard/keys/john_private.key`)
- **Client public keys**: `./wireguard/keys/` (e.g., `./wireguard/keys/john_public.key`)

**Important:** Client files are NOT scattered across the system - they are all organized in the project directory for easy management and backup.

### Server configuration
- **Server configuration**: `/etc/wireguard/wg0.conf` (standard WireGuard location)
- **Database**: `./wireguard.db` (SQLite database with client and server information)

## Project structure

```
fast-wireguard/
├── fastwg/
│   ├── __init__.py
│   ├── cli.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── wireguard.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── server.py
│   └── utils/
├── wireguard/
│   ├── keys/           # Client private and public keys
│   └── configs/        # Client configuration files
├── wireguard.db        # SQLite database
├── fastwg.py
├── setup.py
├── requirements.txt
└── README.md
```

## Удаление

### Способ 1: Удаление через pip

```bash
# Удаляем пакет
sudo pip uninstall fastwg

# Проверяем что удалилось
which fastwg
```

### Способ 2: Удаление вручную

```bash
# Находим где установлен fastwg
which fastwg

# Удаляем исполняемый файл
sudo rm /usr/local/bin/fastwg  # или /usr/bin/fastwg

# Удаляем пакет из Python
sudo pip uninstall fastwg
```

### Способ 3: Полная очистка

```bash
# Удаляем пакет
sudo pip uninstall fastwg

# Удаляем данные (если нужно)
sudo rm -rf /etc/wireguard/fastwg*
sudo rm -rf ~/.fastwg
sudo rm -f wireguard.db
```

## Обновление

```bash
# Переходим в директорию проекта
cd fast-wireguard

# Обновляем код
git pull

# Переустанавливаем
sudo pip install -e . --force-reinstall
```

## Резервное копирование

Перед удалением рекомендуется сделать резервную копию:

```bash
# Создаем резервную копию
sudo cp -r /etc/wireguard /etc/wireguard.backup
sudo cp wireguard.db wireguard.db.backup

# Восстановление (если нужно)
sudo cp -r /etc/wireguard.backup/* /etc/wireguard/
cp wireguard.db.backup wireguard.db
```

## Requirements

- Python 3.8+
- WireGuard installed on the system
- Root privileges for WireGuard operations
- Linux system

## Troubleshooting

### Error "Root privileges required"
```bash
# Run commands with sudo
sudo fastwg create client_name
```

### Error "WireGuard not installed"
```bash
# Install WireGuard
sudo apt install wireguard  # Ubuntu/Debian
sudo dnf install wireguard-tools  # Fedora/RHEL
```

### Error "fastwg command not found"
```bash
# Check installation
pip list | grep fastwg

# Reinstall
sudo pip install -e . --force-reinstall
```

### Permission issues
```bash
# Check configuration file permissions
ls -la /etc/wireguard/

# Fix permissions if needed
sudo chmod 600 /etc/wireguard/*.conf
```

## License

MIT License

---

# Fast WireGuard (Русский)

Быстрое и простое управление WireGuard сервером через CLI интерфейс.

## Возможности

- 🚀 Быстрое создание и управление WireGuard конфигурациями
- 📱 Генерация конфигурационных файлов для клиентов
- 🔐 Безопасное хранение ключей в SQLite базе данных
- 🔍 Сканирование и импорт существующих конфигураций
- 📊 Мониторинг активных подключений
- 🔄 Автоматическое обновление конфигураций сервера
- 🛡️ Блокировка/разблокировка клиентов
- 📋 Удобный CLI интерфейс с цветным выводом

## Установка

### Способ 1: Автоматическая установка (рекомендуемый)

```bash
# Скачиваем и запускаем установщик
curl -sSL https://raw.githubusercontent.com/wolfDiesel/fast-wireguard/main/install.sh | sudo bash
```

### Способ 2: Ручная установка через pip

1. Клонируйте репозиторий:
```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите утилиту в систему:
```bash
sudo pip install -e .
```

## Использование

**Важно:** Все команды требуют root привилегий (sudo).

### Основные команды

```bash
# Сканировать существующие конфигурации
sudo fastwg scan

# Создать нового клиента
sudo fastwg create client_name

# Удалить клиента
sudo fastwg delete client_name

# Блокировать клиента
sudo fastwg disable client_name

# Разблокировать клиента
sudo fastwg enable client_name

# Показать конфигурацию клиента
sudo fastwg cat client_name

# Список всех клиентов
sudo fastwg list

# Статус WireGuard сервера
sudo fastwg status
```

## Требования

- Python 3.8+
- WireGuard установленный в системе
- Root привилегии для работы с WireGuard
- Linux система

## Устранение неполадок

### Ошибка "Требуются root привилегии"
```bash
# Запускайте команды с sudo
sudo fastwg create client_name
```

### Ошибка "WireGuard не установлен"
```bash
# Установите WireGuard
sudo apt install wireguard  # Ubuntu/Debian
sudo dnf install wireguard-tools  # Fedora/RHEL
```

### Ошибка "Команда fastwg не найдена"
```bash
# Проверьте установку
pip list | grep fastwg

# Переустановите
sudo pip install -e . --force-reinstall
```

### Проблемы с правами доступа
```bash
# Проверьте права на конфигурационные файлы
ls -la /etc/wireguard/

# Исправьте права если нужно
sudo chmod 600 /etc/wireguard/*.conf
```
