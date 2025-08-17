# Интернационализация FastWG (i18n)

FastWG поддерживает несколько языков через встроенную систему интернационализации.

## Поддерживаемые языки

- 🇺🇸 **English** (по умолчанию)
- 🇷🇺 **Russian** (русский)

## Как использовать

### Автоматическое определение языка

Система автоматически определяет язык на основе:

1. **Переменной окружения** `FASTWG_LANG`
2. **Системной локали** (переменная окружения `LANG`)

```bash
# Установка языка через переменную окружения
export FASTWG_LANG=ru
fastwg --help

# Или установка системной локали
export LANG=ru_RU.UTF-8
fastwg --help
```

### Программное переключение языка

```python
from fastwg.utils.i18n import set_language, gettext as _

# Установка языка
set_language('ru')

# Использование переводов
print(_("Error: Root privileges required for WireGuard operations"))
# Вывод: Ошибка: Требуются root привилегии для работы с WireGuard
```

## Структура файлов переводов

```
fastwg/
├── locale/
│   ├── fastwg.pot          # Шаблон переводов
│   └── ru/
│       └── LC_MESSAGES/
│           ├── fastwg.po   # Русские переводы (исходник)
│           └── fastwg.mo   # Скомпилированные переводы (бинарный)
```

## Добавление новых языков

### 1. Создание директории переводов

```bash
mkdir -p fastwg/locale/es/LC_MESSAGES
```

### 2. Создание файла переводов

```bash
# Копирование шаблона
cp fastwg/locale/fastwg.pot fastwg/locale/es/LC_MESSAGES/fastwg.po
```

### 3. Редактирование файла переводов

Редактируйте `fastwg/locale/es/LC_MESSAGES/fastwg.po`:

```po
msgid "Error: Root privileges required for WireGuard operations"
msgstr "Error: Se requieren privilegios de root para operaciones de WireGuard"
```

### 4. Компиляция переводов

```bash
cd fastwg/locale/es/LC_MESSAGES
msgfmt fastwg.po -o fastwg.mo
```

### 5. Обновление i18n.py

Добавьте поддержку испанского в `fastwg/utils/i18n.py`:

```python
if language == 'es':
    self._translation = gettext_module.translation(
        'fastwg',
        self.locale_dir,
        languages=['es'],
        fallback=True
    )
```

## Ключи переводов

### Сообщения CLI

| English | Russian |
|---------|---------|
| `Error: Root privileges required for WireGuard operations` | `Ошибка: Требуются root привилегии для работы с WireGuard` |
| `Run the command with sudo` | `Запустите команду с sudo` |
| `Scanning existing configurations...` | `Сканирование существующих конфигураций...` |
| `✓ Client successfully created` | `✓ Клиент успешно создан` |
| `✗ Error creating client` | `✗ Ошибка создания клиента` |

### Описания команд

| English | Russian |
|---------|---------|
| `Scan existing WireGuard configurations` | `Сканирует существующие конфигурации WireGuard` |
| `Create new client` | `Создает нового клиента` |
| `Delete client` | `Удаляет клиента` |
| `Disable client` | `Блокирует клиента` |
| `Enable client` | `Разблокирует клиента` |

## Разработка

### Извлечение новых строк

При добавлении новых переводимых строк:

1. **Используйте функцию `_()`**:
```python
from fastwg.utils.i18n import gettext as _

print(_("New message to translate"))
```

2. **Обновите шаблон**:
```bash
cd fastwg/locale
xgettext -o fastwg.pot --from-code=UTF-8 ../fastwg/**/*.py
```

3. **Обновите существующие переводы**:
```bash
cd fastwg/locale/ru/LC_MESSAGES
msgmerge --update fastwg.po ../fastwg.pot
```

4. **Скомпилируйте переводы**:
```bash
msgfmt fastwg.po -o fastwg.mo
```

### Тестирование переводов

```bash
# Тест с разными языками
FASTWG_LANG=en fastwg --help
FASTWG_LANG=ru fastwg --help
```

## Лучшие практики

1. **Всегда используйте функцию `_()`** для строк, видимых пользователю
2. **Поддерживайте переводы в актуальном состоянии** при добавлении новых функций
3. **Тестируйте переводы** на разных языках
4. **Используйте описательные ID сообщений**, которые понятны в контексте
5. **Обрабатывайте множественные формы** при необходимости с помощью `ngettext()`

## Примеры использования

```python
from fastwg.utils.i18n import gettext as _, ngettext

# Простой перевод
error_msg = _("Error: Root privileges required for WireGuard operations")

# Множественные формы
count = 5
msg = ngettext("Found {} configuration", "Found {} configurations", count).format(count)
```

## Устранение неполадок

### Переводы не работают

1. **Проверьте права доступа к файлам**:
```bash
ls -la fastwg/locale/ru/LC_MESSAGES/fastwg.mo
```

2. **Проверьте компиляцию**:
```bash
msgfmt --check fastwg/locale/ru/LC_MESSAGES/fastwg.po
```

3. **Проверьте переменные окружения**:
```bash
echo $FASTWG_LANG
echo $LANG
```

### Отсутствующие переводы

Если сообщение отображается на английском вместо целевого языка:

1. **Проверьте, есть ли строка в .po файле**
2. **Убедитесь, что ID сообщения точно совпадает**
3. **Перекомпилируйте .mo файл**
4. **Перезапустите приложение**

## Вклад в переводы

Чтобы внести вклад в переводы:

1. Форкните репозиторий
2. Создайте файлы переводов для вашего языка
3. Тщательно протестируйте переводы
4. Отправьте pull request

Убедитесь, что:
- Все строки переведены
- Грамматика и орфография корректны
- Технические термины подходят для целевого языка
- Перевод сохраняет исходный смысл

## Связанные ссылки

- [Основная документация](../README.md)
- [Английская документация](../en/README.md)
- [Русская документация](../ru/README.md)
- [Репозиторий GitHub](https://github.com/wolfDiesel/fast-wireguard)
