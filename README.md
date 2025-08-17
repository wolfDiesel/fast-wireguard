# Fast WireGuard

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

1. Клонируйте репозиторий:
```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите утилиту:
```bash
pip install -e .
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

### Примеры использования

```bash
# Создание клиента
sudo fastwg create john
# ✓ Клиент 'john' успешно создан
#   IP адрес: 10.0.0.2
#   Конфигурация: ./wireguard/configs/john.conf

# Просмотр списка клиентов
sudo fastwg list
# +--------+------------+----------------------+----------------------+----------------------+
# | Имя    | IP адрес   | Статус               | Последнее подключение| Создан              |
# +--------+------------+----------------------+----------------------+----------------------+
# | john   | 10.0.0.2   | Активен, Подключен   | 2024-01-15 14:30:25 | 2024-01-15 14:25:10 |
# +--------+------------+----------------------+----------------------+----------------------+

# Просмотр конфигурации клиента
sudo fastwg cat john
# [Interface]
# PrivateKey = abc123...
# Address = 10.0.0.2
# DNS = 8.8.8.8
# MTU = 1420
# 
# [Peer]
# PublicKey = xyz789...
# Endpoint = :51820
# AllowedIPs = 0.0.0.0/0
# PersistentKeepalive = 25
```

## Структура проекта

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
│   ├── keys/
│   └── configs/
├── fastwg.py
├── setup.py
├── requirements.txt
└── README.md
```

## Требования

- Python 3.8+
- WireGuard установленный в системе
- Root привилегии для работы с WireGuard

## Лицензия

MIT License
