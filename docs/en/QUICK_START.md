# FastWG Quick Start

## One-command installation

```bash
curl -sSL https://raw.githubusercontent.com/wolfDiesel/fast-wireguard/main/install.sh | sudo bash
```

## First steps

1. **Scan existing configurations:**
```bash
sudo fastwg scan
```

2. **Create first client:**
```bash
sudo fastwg create myclient
```

3. **View client list:**
```bash
sudo fastwg list
```

4. **View client configuration:**
```bash
sudo fastwg cat myclient
```

## Basic commands

| Command | Description |
|---------|-------------|
| `fastwg scan` | Scan existing configurations |
| `fastwg create <name>` | Create new client |
| `fastwg delete <name>` | Delete client |
| `fastwg disable <name>` | Disable client |
| `fastwg enable <name>` | Enable client |
| `fastwg cat <name>` | View configuration |
| `fastwg list` | List all clients |
| `fastwg status` | WireGuard server status |

## Usage examples

### Creating multiple clients
```bash
sudo fastwg create alice
sudo fastwg create bob
sudo fastwg create charlie
```

### Client management
```bash
# View all clients
sudo fastwg list

# Disable problematic client
sudo fastwg disable bob

# View configuration
sudo fastwg cat alice

# Delete inactive client
sudo fastwg delete charlie
```

### Using alias
After installation, the `wg` alias is available:
```bash
wg create client
wg list
wg cat client
```

## File structure

```
wireguard/
├── configs/          # Client configurations
│   ├── alice.conf
│   ├── bob.conf
│   └── charlie.conf
└── wireguard.db      # Database
```

## Uninstallation

```bash
# Uninstall via installer
sudo ./install.sh --uninstall

# Or manually
sudo pip uninstall fastwg
```

## Full documentation

- [README.md](README.md) - Full documentation
- [INSTALL.md](INSTALL.md) - Detailed installation instructions
- [DEMO.md](DEMO.md) - Usage demonstration

---

# Быстрый старт FastWG (Русский)

## Установка одной командой

```bash
curl -sSL https://raw.githubusercontent.com/wolfDiesel/fast-wireguard/main/install.sh | sudo bash
```

## Первые шаги

1. **Сканирование существующих конфигураций:**
```bash
sudo fastwg scan
```

2. **Создание первого клиента:**
```bash
sudo fastwg create myclient
```

3. **Просмотр списка клиентов:**
```bash
sudo fastwg list
```

4. **Просмотр конфигурации клиента:**
```bash
sudo fastwg cat myclient
```

## Основные команды

| Команда | Описание |
|---------|----------|
| `fastwg scan` | Сканирование существующих конфигураций |
| `fastwg create <name>` | Создание нового клиента |
| `fastwg delete <name>` | Удаление клиента |
| `fastwg disable <name>` | Блокировка клиента |
| `fastwg enable <name>` | Разблокировка клиента |
| `fastwg cat <name>` | Просмотр конфигурации |
| `fastwg list` | Список всех клиентов |
| `fastwg status` | Статус WireGuard сервера |

## Примеры использования

### Создание нескольких клиентов
```bash
sudo fastwg create alice
sudo fastwg create bob
sudo fastwg create charlie
```

### Управление клиентами
```bash
# Просмотр всех клиентов
sudo fastwg list

# Блокировка проблемного клиента
sudo fastwg disable bob

# Просмотр конфигурации
sudo fastwg cat alice

# Удаление неактивного клиента
sudo fastwg delete charlie
```

### Использование алиаса
После установки доступен алиас `wg`:
```bash
wg create client
wg list
wg cat client
```

## Структура файлов

```
wireguard/
├── configs/          # Конфигурации клиентов
│   ├── alice.conf
│   ├── bob.conf
│   └── charlie.conf
└── wireguard.db      # База данных
```

## Удаление

```bash
# Удаление через установщик
sudo ./install.sh --uninstall

# Или вручную
sudo pip uninstall fastwg
```
