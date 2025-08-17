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

После установки команда `fastwg` будет доступна глобально.

### Способ 3: Установка через setup.py

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
sudo python setup.py install
```

### Способ 4: Создание пакета и установка

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# Создаем дистрибутив
python setup.py sdist bdist_wheel

# Устанавливаем созданный пакет
sudo pip install dist/fastwg-1.0.0.tar.gz
```

### Проверка установки

```bash
# Проверяем что команда доступна
fastwg --version

# Проверяем справку
fastwg --help

# Проверяем где установлен
which fastwg
```

## Использование

**Важно:** Все команды требуют root привилегий (sudo).

### Первоначальная настройка

После установки нужно либо просканировать существующие конфигурации, либо создать новый сервер с нуля:

#### Вариант 1: Сканирование существующих конфигураций WireGuard
Если у вас уже есть конфигурации WireGuard сервера:

```bash
# Сканировать и импортировать существующие конфигурации
sudo fastwg scan
```

#### Вариант 2: Создание сервера с нуля
Если вы хотите настроить новый WireGuard сервер:

```bash
# Инициализировать конфигурацию сервера
sudo fastwg init-server

# Установить внешний хост (публичный IP вашего сервера и порт)
sudo fastwg sethost ВАШ_ПУБЛИЧНЫЙ_IP:51820

# Запустить сервер
sudo fastwg start
```

### Основные команды

```bash
# Инициализировать конфигурацию сервера (создать с нуля)
sudo fastwg init-server

# Установить внешний хост (IP:порт)
sudo fastwg sethost IP:ПОРТ

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

# Список всех клиентов (включая неактивных/заблокированных)
sudo fastwg list --all

# Статус WireGuard сервера
sudo fastwg status

# Запустить WireGuard сервер
sudo fastwg start

# Остановить WireGuard сервер
sudo fastwg stop

# Перезапустить WireGuard сервер
sudo fastwg restart

# Перезагрузить конфигурацию сервера
sudo fastwg reload
```

### Примеры использования

#### Настройка нового сервера с нуля

```bash
# Инициализировать конфигурацию сервера
sudo fastwg init-server
# ✓ Конфигурация сервера успешно инициализирована
#   Интерфейс: wg0
#   Порт: 51820
#   Сеть: 10.42.42.0/24
#   DNS: 8.8.8.8
#
# Следующие шаги:
#   1. Установить внешний хост: fastwg sethost <ваш_ip>:<порт>
#   2. Запустить сервер: fastwg start
#   3. Создать клиентов: fastwg create <имя_клиента>

# Установить внешний хост
sudo fastwg sethost 203.0.113.1:51820
# ✓ Хост успешно установлен

# Запустить сервер
sudo fastwg start
# ✓ Сервер успешно запущен
```

#### Создание и управление клиентами

```bash
# Создание клиента
sudo fastwg create john
# ✓ Клиент 'john' успешно создан
#   IP адрес: 10.42.42.2
#   Конфигурация: ./wireguard/configs/john.conf

# Просмотр списка клиентов
sudo fastwg list
# +--------+------------+----------------------+----------------------+----------------------+
# | Имя    | IP адрес   | Статус               | Последнее подключение| Создан              |
# +--------+------------+----------------------+----------------------+----------------------+
# | john   | 10.42.42.2 | Активен, Подключен   | 2024-01-15 14:30:25 | 2024-01-15 14:25:10 |
# +--------+------------+----------------------+----------------------+----------------------+

# Просмотр конфигурации клиента
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

#### Управление сервером

```bash
# Проверить статус сервера
sudo fastwg status
# ✓ WireGuard активен
# Активные интерфейсы:
# interface: wg0
#   public key: xyz789...
#   private key: (hidden)
#   listening port: 51820

# Перезапустить сервер
sudo fastwg restart
# ✓ Сервер успешно перезапущен

# Перезагрузить конфигурацию
sudo fastwg reload
# ✓ Конфигурация успешно перезагружена
```

## Расположение файлов

### Конфигурации и ключи клиентов
Все конфигурации и ключи клиентов сохраняются в директории проекта:

- **Конфигурации клиентов**: `./wireguard/configs/` (например, `./wireguard/configs/john.conf`)
- **Приватные ключи клиентов**: `./wireguard/keys/` (например, `./wireguard/keys/john_private.key`)
- **Публичные ключи клиентов**: `./wireguard/keys/` (например, `./wireguard/keys/john_public.key`)

**Важно:** Файлы клиентов НЕ разбросаны по системе - они все организованы в директории проекта для удобного управления и резервного копирования.

### Конфигурация сервера
- **Конфигурация сервера**: `/etc/wireguard/wg0.conf` (стандартное расположение WireGuard)
- **База данных**: `./wireguard.db` (SQLite база данных с информацией о клиентах и сервере)

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
│   ├── keys/           # Приватные и публичные ключи клиентов
│   └── configs/        # Конфигурационные файлы клиентов
├── wireguard.db        # SQLite база данных
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

## Лицензия

MIT License
