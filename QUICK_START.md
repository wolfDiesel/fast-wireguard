# Быстрый старт FastWG

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

## Полная документация

- [README.md](README.md) - Полная документация
- [INSTALL.md](INSTALL.md) - Подробные инструкции по установке
- [DEMO.md](DEMO.md) - Демонстрация работы
