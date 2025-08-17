# FastWG Internationalization (i18n)

FastWG supports multiple languages through a built-in internationalization system.

## 🌍 Supported Languages

- 🇺🇸 **English** (default)
- 🇷🇺 **Russian** (русский)

## 📚 Documentation

- [🇺🇸 English](en.md) - Translation documentation in English
- [🇷🇺 Русский](ru.md) - Документация по переводам на русском

## 🚀 Quick Start

### Automatic Language Detection

```bash
# Set language via environment variable
export FASTWG_LANG=ru
fastwg --help

# Or set system locale
export LANG=ru_RU.UTF-8
fastwg --help
```

### Programmatic Language Setting

```python
from fastwg.utils.i18n import set_language, gettext as _

# Set language
set_language('ru')

# Use translations
print(_("Error: Root privileges required for WireGuard operations"))
# Output: Ошибка: Требуются root привилегии для работы с WireGuard
```

## 📁 Translation Files Structure

```
fastwg/
├── locale/
│   ├── fastwg.pot          # Translation template
│   └── ru/
│       └── LC_MESSAGES/
│           ├── fastwg.po   # Russian translations (source)
│           └── fastwg.mo   # Compiled translations (binary)
```

## 🔧 Adding New Languages

See the language-specific documentation for detailed instructions:

- [🇺🇸 English Guide](en.md#adding-new-languages)
- [🇷🇺 Русское руководство](ru.md#добавление-новых-языков)

## 📖 Translation Keys

### CLI Messages

| English | Russian |
|---------|---------|
| `Error: Root privileges required for WireGuard operations` | `Ошибка: Требуются root привилегии для работы с WireGuard` |
| `Run the command with sudo` | `Запустите команду с sudo` |
| `Scanning existing configurations...` | `Сканирование существующих конфигураций...` |
| `✓ Client successfully created` | `✓ Клиент успешно создан` |
| `✗ Error creating client` | `✗ Ошибка создания клиента` |

### Command Descriptions

| English | Russian |
|---------|---------|
| `Scan existing WireGuard configurations` | `Сканирует существующие конфигурации WireGuard` |
| `Create new client` | `Создает нового клиента` |
| `Delete client` | `Удаляет клиента` |
| `Disable client` | `Блокирует клиента` |
| `Enable client` | `Разблокирует клиента` |

## 🛠️ Development

### Extracting New Strings

When adding new translatable strings:

1. **Use the `_()` function**:
```python
from fastwg.utils.i18n import gettext as _

print(_("New message to translate"))
```

2. **Update the template**:
```bash
cd fastwg/locale
xgettext -o fastwg.pot --from-code=UTF-8 ../fastwg/**/*.py
```

3. **Update existing translations**:
```bash
cd fastwg/locale/ru/LC_MESSAGES
msgmerge --update fastwg.po ../fastwg.pot
```

4. **Compile translations**:
```bash
msgfmt fastwg.po -o fastwg.mo
```

### Testing Translations

```bash
# Test with different languages
FASTWG_LANG=en fastwg --help
FASTWG_LANG=ru fastwg --help
```

## 📋 Best Practices

1. **Always use the `_()` function** for user-facing strings
2. **Keep translations up to date** when adding new features
3. **Test translations** in different languages
4. **Use descriptive message IDs** that are clear in context
5. **Handle plural forms** when needed using `ngettext()`

## 🔗 Related Links

- [Main Documentation](../README.md)
- [English Documentation](../en/README.md)
- [Russian Documentation](../ru/README.md)
- [GitHub Repository](https://github.com/wolfDiesel/fast-wireguard)
