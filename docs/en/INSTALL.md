# FastWG Installation and Removal Instructions

## Prerequisites

### System requirements
- Linux system (Ubuntu, Debian, Fedora, RHEL, CentOS)
- Python 3.8 or higher
- Git
- Root privileges

### Installing WireGuard

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install wireguard wireguard-tools
```

#### Fedora/RHEL/CentOS:
```bash
sudo dnf install wireguard-tools
# or
sudo yum install wireguard-tools
```

#### Arch Linux:
```bash
sudo pacman -S wireguard-tools
```

### Installing Python dependencies
```bash
# Install pip (if not installed)
sudo apt install python3-pip  # Ubuntu/Debian
sudo dnf install python3-pip  # Fedora/RHEL
```

## Installing FastWG

### Method 1: Installation from source code (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install system-wide
sudo pip install -e .
```

### Method 2: Installation via setup.py

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
sudo python setup.py install
```

### Method 3: Package creation and installation

```bash
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard

# Create distribution
python setup.py sdist bdist_wheel

# Install the created package
sudo pip install dist/fastwg-1.0.0.tar.gz
```

### Method 4: Installation in virtual environment

```bash
# Create virtual environment
python3 -m venv fastwg_env
source fastwg_env/bin/activate

# Clone and install
git clone https://github.com/wolfDiesel/fast-wireguard.git
cd fast-wireguard
pip install -r requirements.txt
pip install -e .

# Activate environment for each use
source fastwg_env/bin/activate
fastwg --help
```

## Installation verification

```bash
# Check version
fastwg --version

# Check help
fastwg --help

# Check installation location
which fastwg

# Check command list
fastwg --help
```

## Removing FastWG

### Method 1: Removal via pip

```bash
# Remove package
sudo pip uninstall fastwg

# Check if removed
which fastwg
```

### Method 2: Manual removal

```bash
# Find where fastwg is installed
which fastwg

# Remove executable file
sudo rm /usr/local/bin/fastwg  # or /usr/bin/fastwg

# Remove package from Python
sudo pip uninstall fastwg
```

### Method 3: Complete cleanup

```bash
# Remove package
sudo pip uninstall fastwg

# Remove data (if needed)
sudo rm -rf /etc/wireguard/fastwg*
sudo rm -rf ~/.fastwg
sudo rm -f wireguard.db

# Remove project directories
rm -rf ~/fast-wireguard
```

### Method 4: Removal from virtual environment

```bash
# Deactivate environment
deactivate

# Remove virtual environment
rm -rf fastwg_env
```

## Updating

### Updating from source code

```bash
# Go to project directory
cd fast-wireguard

# Update code
git pull

# Reinstall
sudo pip install -e . --force-reinstall
```

### Updating via pip

```bash
# If installed via pip
sudo pip install --upgrade fastwg
```

## Backup

### Creating backup

```bash
# Create backup of server configurations
sudo cp -r /etc/wireguard /etc/wireguard.backup

# Create backup of database
sudo cp wireguard.db wireguard.db.backup

# Create backup of client configurations
sudo cp -r ./wireguard/configs ./wireguard/configs.backup
```

### Restoring from backup

```bash
# Restore server configurations
sudo cp -r /etc/wireguard.backup/* /etc/wireguard/

# Restore database
cp wireguard.db.backup wireguard.db

# Restore client configurations
cp -r ./wireguard/configs.backup/* ./wireguard/configs/
```

## Automation (optional)

### Creating systemd service

```bash
# Create service file
sudo tee /etc/systemd/system/fastwg.service << EOF
[Unit]
Description=FastWG WireGuard Manager
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/fastwg status
User=root

[Install]
WantedBy=multi-user.target
EOF

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable fastwg.service
sudo systemctl start fastwg.service
```

### Creating alias

```bash
# Add alias to ~/.bashrc
echo 'alias wg="sudo fastwg"' >> ~/.bashrc
source ~/.bashrc

# Now you can use
wg list
wg create client_name
```

## Troubleshooting

### Error "Root privileges required"
```bash
# Run commands with sudo
sudo fastwg create client_name
```

### Error "WireGuard not installed"
```bash
# Install WireGuard
sudo apt install wireguard wireguard-tools  # Ubuntu/Debian
sudo dnf install wireguard-tools  # Fedora/RHEL
```

### Error "fastwg command not found"
```bash
# Check installation
pip list | grep fastwg

# Reinstall
sudo pip install -e . --force-reinstall

# Check PATH
echo $PATH
```

### Error "Permission denied"
```bash
# Check configuration file permissions
ls -la /etc/wireguard/

# Fix permissions if needed
sudo chmod 600 /etc/wireguard/*.conf
sudo chown root:root /etc/wireguard/*.conf
```

### Error "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python3 --version
```

### Database issues
```bash
# Delete corrupted database
rm wireguard.db

# Restart utility - database will be recreated
fastwg scan
```

## Logs and debugging

### Enabling debug mode
```bash
# Run with verbose output
sudo fastwg --debug list

# View systemd logs
sudo journalctl -u fastwg.service
```

### Checking WireGuard status
```bash
# WireGuard status
sudo wg show

# Interface status
sudo ip link show

# Check configurations
sudo cat /etc/wireguard/wg0.conf
```

## Security

### Security recommendations
1. Always use sudo for fastwg commands
2. Regularly update WireGuard and system
3. Use complex client names
4. Regularly rotate keys
5. Monitor active connections

### Security checks
```bash
# Check file permissions
ls -la /etc/wireguard/
ls -la ./wireguard/configs/

# Check active connections
sudo fastwg list
sudo wg show
```
