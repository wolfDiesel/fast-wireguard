# FastWG Demo

## Installation and setup

```bash
# Clone repository
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# Install dependencies
pip install -r requirements.txt

# Install utility
pip install -e .
```

## Basic commands

### 1. Scanning existing configurations
```bash
sudo fastwg scan
```
This command will find all existing WireGuard configurations in `/etc/wireguard` and offer to import them.

### 2. Creating a new client
```bash
sudo fastwg create john
```
Creates a new client named "john", generates keys and configuration file.

### 3. Viewing client list
```bash
sudo fastwg list
```
Shows a table of all clients with their statuses and connection information.

### 4. Viewing client configuration
```bash
sudo fastwg cat john
```
Outputs the client configuration file for copying to the device.

### 5. Disabling client
```bash
sudo fastwg disable john
```
Temporarily disconnects the client from the network.

### 6. Enabling client
```bash
sudo fastwg enable john
```
Returns the client to active state.

### 7. Deleting client
```bash
sudo fastwg delete john
```
Completely removes the client and its configuration.

### 8. Server status
```bash
sudo fastwg status
```
Shows the current state of the WireGuard server.

## Complete workflow example

```bash
# 1. Scan existing configurations
sudo fastwg scan

# 2. Create several clients
sudo fastwg create alice
sudo fastwg create bob
sudo fastwg create charlie

# 3. View the list
sudo fastwg list

# 4. View client configuration
sudo fastwg cat alice

# 5. Disable problematic client
sudo fastwg disable bob

# 6. Check status
sudo fastwg status

# 7. Delete inactive client
sudo fastwg delete charlie
```

## File structure

After running the utility, the following structure is created:

```
wireguard/
├── keys/           # Private keys (if needed)
├── configs/        # Client configuration files
│   ├── alice.conf
│   ├── bob.conf
│   └── charlie.conf
└── wireguard.db    # SQLite database with client information
```

## Features

- **Security**: All configuration files have 600 permissions (owner only)
- **Automatic management**: Server configuration is automatically updated when creating/deleting clients
- **Monitoring**: Real-time tracking of active connections
- **Import**: Ability to import existing configurations
- **Colored output**: Convenient interface with colored status output

## Requirements

- Python 3.8+
- WireGuard installed on the system
- Root privileges for WireGuard operations
- Linux system

---

# Демонстрация FastWG (Русский)

## Установка и настройка

```bash
# Клонирование репозитория
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# Установка зависимостей
pip install -r requirements.txt

# Установка утилиты
pip install -e .
```

## Основные команды

### 1. Сканирование существующих конфигураций
```bash
sudo fastwg scan
```
Эта команда найдет все существующие конфигурации WireGuard в `/etc/wireguard` и предложит их импортировать.

### 2. Создание нового клиента
```bash
sudo fastwg create john
```
Создает нового клиента с именем "john", генерирует ключи и конфигурационный файл.

### 3. Просмотр списка клиентов
```bash
sudo fastwg list
```
Показывает таблицу всех клиентов с их статусами и информацией о подключениях.

### 4. Просмотр конфигурации клиента
```bash
sudo fastwg cat john
```
Выводит конфигурационный файл клиента для копирования на устройство.

### 5. Блокировка клиента
```bash
sudo fastwg disable john
```
Временно отключает клиента от сети.

### 6. Разблокировка клиента
```bash
sudo fastwg enable john
```
Возвращает клиента в активное состояние.

### 7. Удаление клиента
```bash
sudo fastwg delete john
```
Полностью удаляет клиента и его конфигурацию.

### 8. Статус сервера
```bash
sudo fastwg status
```
Показывает текущее состояние WireGuard сервера.

## Пример полного рабочего процесса

```bash
# 1. Сканируем существующие конфигурации
sudo fastwg scan

# 2. Создаем нескольких клиентов
sudo fastwg create alice
sudo fastwg create bob
sudo fastwg create charlie

# 3. Просматриваем список
sudo fastwg list

# 4. Просматриваем конфигурацию клиента
sudo fastwg cat alice

# 5. Блокируем проблемного клиента
sudo fastwg disable bob

# 6. Проверяем статус
sudo fastwg status

# 7. Удаляем неактивного клиента
sudo fastwg delete charlie
```

## Структура файлов

После работы утилиты создается следующая структура:

```
wireguard/
├── keys/           # Приватные ключи (если нужны)
├── configs/        # Конфигурационные файлы клиентов
│   ├── alice.conf
│   ├── bob.conf
│   └── charlie.conf
└── wireguard.db    # SQLite база данных с информацией о клиентах
```

## Особенности

- **Безопасность**: Все конфигурационные файлы имеют права 600 (только для владельца)
- **Автоматическое управление**: При создании/удалении клиентов автоматически обновляется конфигурация сервера
- **Мониторинг**: Отслеживание активных подключений в реальном времени
- **Импорт**: Возможность импорта существующих конфигураций
- **Цветной вывод**: Удобный интерфейс с цветным выводом статусов

## Требования

- Python 3.8+
- WireGuard установленный в системе
- Root привилегии для работы с WireGuard
- Linux система
