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

### Способ 2: Установка через setup.py

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
sudo python setup.py install
```

### Способ 3: Создание пакета и установка

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
