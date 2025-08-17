# Fast WireGuard

Fast and simple WireGuard server management through CLI interface.

## 🌍 Documentation

📚 **Full documentation is available in multiple languages:**

- [🇺🇸 English](docs/en/README.md) - Complete documentation
- [🇷🇺 Русский](docs/ru/README.md) - Полная документация
- [📖 Documentation Index](docs/README.md) - Choose your language

## 🚀 Quick Start

### One-command installation

```bash
curl -sSL https://raw.githubusercontent.com/wolfDiesel/fast-wireguard/main/install.sh | sudo bash
```

### Basic usage

```bash
# Scan existing configurations
sudo fastwg scan

# Create a new client
sudo fastwg create myclient

# List all clients
sudo fastwg list

# View client configuration
sudo fastwg cat myclient
```

## ✨ Features

- 🚀 Fast WireGuard configuration management
- 📱 Client configuration file generation
- 🔐 Secure key storage in SQLite database
- 🔍 Scan and import existing configurations
- 📊 Active connection monitoring
- 🔄 Automatic server configuration updates
- 🛡️ Client blocking/unblocking
- 📋 Convenient CLI interface with colored output
- 🌍 Multi-language support (English, Russian)

## 📋 Main Commands

| Command | Description |
|---------|-------------|
| `fastwg scan` | Scan existing WireGuard configurations |
| `fastwg create <name>` | Create new client |
| `fastwg delete <name>` | Delete client |
| `fastwg disable <name>` | Disable client |
| `fastwg enable <name>` | Enable client |
| `fastwg cat <name>` | Show client configuration |
| `fastwg list` | List all clients |
| `fastwg status` | Show WireGuard server status |

## 🔗 Quick Links

- [📖 Full Documentation](docs/README.md)
- [⚡ Quick Start Guide](docs/en/QUICK_START.md)
- [🔧 Installation Guide](docs/en/INSTALL.md)
- [🎯 Usage Demo](docs/en/DEMO.md)
- [🌐 Internationalization](docs/i18n/README.md)
- [💻 Development Guide](docs/en/development.md)
- [📦 GitHub Repository](https://github.com/wolfDiesel/fast-wireguard)
- [🐛 Issues](https://github.com/wolfDiesel/fast-wireguard/issues)

## 📦 Installation

### Automatic (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/wolfDiesel/fast-wireguard/main/install.sh | sudo bash
```

### Manual

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
sudo pip install -e .
```

## 🌍 Language Support

FastWG supports multiple languages:

- **🇺🇸 English** (default)
- **🇷🇺 Russian** (русский)

Set language via environment variable:
```bash
export FASTWG_LANG=ru
fastwg --help
```

## 📁 Project Structure

```
fast-wireguard/
├── fastwg/                 # Main package
│   ├── cli.py             # CLI interface
│   ├── core/              # Core functionality
│   ├── models/            # Data models
│   ├── utils/             # Utilities (i18n)
│   └── locale/            # Translation files
├── docs/                  # Documentation
│   ├── en/               # English docs
│   ├── ru/               # Russian docs
│   └── i18n/             # Translation docs
├── wireguard/            # WireGuard configs
├── fastwg.py             # Entry point
├── setup.py              # Package setup
└── install.sh            # Installer script
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## ⚠️ Requirements

- Python 3.8+
- WireGuard installed on the system
- Root privileges for WireGuard operations
- Linux system

---

**FastWG** - Making WireGuard server management fast and simple! 🚀
