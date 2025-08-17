# GitHub Actions

Этот проект использует GitHub Actions для автоматизации разработки и тестирования.

## Workflows

### 1. Tests (`tests.yml`)

**Триггеры:**
- Push в ветки `main` и `develop`
- Pull Request в ветку `main`

**Что делает:**
- Запускает тесты на Python 3.8-3.12
- Устанавливает системные зависимости (wireguard-tools)
- Запускает тесты с покрытием кода
- Загружает отчет о покрытии в Codecov

### 2. Lint (`lint.yml`)

**Триггеры:**
- Push в ветки `main` и `develop`
- Pull Request в ветку `main`

**Что делает:**
- Проверяет качество кода с помощью:
  - `flake8` - проверка стиля кода
  - `black` - форматирование кода
  - `isort` - сортировка импортов
  - `mypy` - статическая типизация

### 3. Release (`release.yml`)

**Триггеры:**
- Push тега с префиксом `v*` (например, `v1.0.0`)

**Что делает:**
- Запускает тесты
- Собирает пакет
- Создает GitHub Release
- Загружает артефакты релиза

## Использование

### Локальный запуск тестов

```bash
# Установка зависимостей
pip install -r requirements.txt
pip install coverage

# Запуск тестов
python run_tests.py

# Запуск с покрытием
coverage run --source=fastwg run_tests.py
coverage report --show-missing
```

### Локальная проверка качества кода

```bash
# Установка инструментов
pip install flake8 black isort mypy

# Проверка стиля
flake8 fastwg/ tests/

# Форматирование
black fastwg/ tests/

# Сортировка импортов
isort fastwg/ tests/

# Проверка типов
mypy fastwg/
```

### Создание релиза

```bash
# Создание тега
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions автоматически создаст релиз
```

## Настройки

### Coverage

Настройки покрытия кода находятся в файле `.coveragerc`:
- Исключает тестовые файлы и кэш
- Настраивает исключения для отчета

### Линтеры

Настройки линтеров находятся в `pyproject.toml`:
- `black`: длина строки 127 символов
- `isort`: профиль совместимый с black
- `mypy`: строгие проверки типов

## Статус

![Tests](https://github.com/wolfDiesel/fast-wireguard/workflows/Tests/badge.svg)
![Lint](https://github.com/wolfDiesel/fast-wireguard/workflows/Lint/badge.svg)
![Release](https://github.com/wolfDiesel/fast-wireguard/workflows/Release/badge.svg)
