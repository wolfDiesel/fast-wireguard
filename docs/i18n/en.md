# FastWG Internationalization (i18n)

FastWG supports multiple languages through a built-in internationalization system.

## Supported Languages

- 🇺🇸 **English** (default)
- 🇷🇺 **Russian** (русский)

## How to Use

### Automatic Language Detection

The system automatically detects the language based on:

1. **Environment variable** `FASTWG_LANG`
2. **System locale** (`LANG` environment variable)

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

## Translation Files Structure

```
fastwg/
├── locale/
│   ├── fastwg.pot          # Translation template
│   └── ru/
│       └── LC_MESSAGES/
│           ├── fastwg.po   # Russian translations (source)
│           └── fastwg.mo   # Compiled translations (binary)
```

## Adding New Languages

### 1. Create Translation Directory

```bash
mkdir -p fastwg/locale/es/LC_MESSAGES
```

### 2. Create Translation File

```bash
# Copy template
cp fastwg/locale/fastwg.pot fastwg/locale/es/LC_MESSAGES/fastwg.po
```

### 3. Edit Translation File

Edit `fastwg/locale/es/LC_MESSAGES/fastwg.po`:

```po
msgid "Error: Root privileges required for WireGuard operations"
msgstr "Error: Se requieren privilegios de root para operaciones de WireGuard"
```

### 4. Compile Translation

```bash
cd fastwg/locale/es/LC_MESSAGES
msgfmt fastwg.po -o fastwg.mo
```

### 5. Update i18n.py

Add Spanish support to `fastwg/utils/i18n.py`:

```python
if language == 'es':
    self._translation = gettext_module.translation(
        'fastwg',
        self.locale_dir,
        languages=['es'],
        fallback=True
    )
```

## Translation Keys

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

## Development

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

## Best Practices

1. **Always use the `_()` function** for user-facing strings
2. **Keep translations up to date** when adding new features
3. **Test translations** in different languages
4. **Use descriptive message IDs** that are clear in context
5. **Handle plural forms** when needed using `ngettext()`

## Example Usage

```python
from fastwg.utils.i18n import gettext as _, ngettext

# Simple translation
error_msg = _("Error: Root privileges required for WireGuard operations")

# Plural forms
count = 5
msg = ngettext("Found {} configuration", "Found {} configurations", count).format(count)
```

## Troubleshooting

### Translation Not Working

1. **Check file permissions**:
```bash
ls -la fastwg/locale/ru/LC_MESSAGES/fastwg.mo
```

2. **Verify compilation**:
```bash
msgfmt --check fastwg/locale/ru/LC_MESSAGES/fastwg.po
```

3. **Check environment**:
```bash
echo $FASTWG_LANG
echo $LANG
```

### Missing Translations

If a message appears in English instead of the target language:

1. **Check if the string is in the .po file**
2. **Verify the message ID matches exactly**
3. **Recompile the .mo file**
4. **Restart the application**

## Contributing Translations

To contribute translations:

1. Fork the repository
2. Create translation files for your language
3. Test the translations thoroughly
4. Submit a pull request

Please ensure:
- All strings are translated
- Grammar and spelling are correct
- Technical terms are appropriate for the target language
- The translation maintains the original meaning
