#!/bin/bash

# FastWG Installer Script
# Автоматическая установка FastWG

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка root привилегий
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Этот скрипт должен быть запущен с root привилегиями"
        print_info "Используйте: sudo $0"
        exit 1
    fi
}

# Определение дистрибутива
detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "Не удалось определить дистрибутив"
        exit 1
    fi
}

# Установка зависимостей
install_dependencies() {
    print_info "Установка системных зависимостей..."
    
    case $OS in
        *"Ubuntu"*|*"Debian"*)
            apt update
            apt install -y python3 python3-pip git wireguard wireguard-tools
            ;;
        *"Fedora"*|*"Red Hat"*|*"CentOS"*)
            dnf install -y python3 python3-pip git wireguard-tools
            ;;
        *"Arch"*)
            pacman -S --noconfirm python python-pip git wireguard-tools
            ;;
        *)
            print_warning "Неизвестный дистрибутив: $OS"
            print_info "Убедитесь что установлены: python3, pip, git, wireguard-tools"
            ;;
    esac
    
    print_success "Системные зависимости установлены"
}

# Проверка Python
check_python() {
    print_info "Проверка Python..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 не найден"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION найден"
    
    # Проверка версии Python
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_success "Версия Python подходящая (>= 3.8)"
    else
        print_error "Требуется Python 3.8 или выше"
        exit 1
    fi
}

# Клонирование репозитория
clone_repo() {
    print_info "Клонирование репозитория..."
    
    if [[ -d "fast-wireguard" ]]; then
        print_warning "Директория fast-wireguard уже существует"
        read -p "Удалить существующую директорию? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf fast-wireguard
        else
            print_info "Используем существующую директорию"
            return
        fi
    fi
    
    git clone https://github.com/wolfDiesel/fast-wireguard.git
    print_success "Репозиторий клонирован"
}

# Установка Python зависимостей
install_python_deps() {
    print_info "Установка Python зависимостей..."
    
    cd fast-wireguard
    
    if [[ -f "requirements.txt" ]]; then
        pip3 install -r requirements.txt
        print_success "Python зависимости установлены"
    else
        print_error "Файл requirements.txt не найден"
        exit 1
    fi
}

# Установка FastWG
install_fastwg() {
    print_info "Установка FastWG..."
    
    pip3 install -e .
    
    # Создание папок для конфигов и ключей
    print_info "Создание папок для конфигураций..."
    mkdir -p /tmp/fastwg/wireguard/configs
    mkdir -p /tmp/fastwg/wireguard/keys
    chmod 700 /tmp/fastwg/wireguard/configs
    chmod 700 /tmp/fastwg/wireguard/keys
    
    print_success "FastWG установлен"
}

# Проверка установки
verify_installation() {
    print_info "Проверка установки..."
    
    if command -v fastwg &> /dev/null; then
        print_success "Команда fastwg доступна"
        fastwg --version
    else
        print_error "Команда fastwg не найдена"
        exit 1
    fi
}

# Создание алиаса
create_alias() {
    print_info "Создание алиаса..."
    
    ALIAS_LINE='alias wg="sudo fastwg"'
    
    if [[ -f ~/.bashrc ]]; then
        if ! grep -q "$ALIAS_LINE" ~/.bashrc; then
            echo "$ALIAS_LINE" >> ~/.bashrc
            print_success "Алиас добавлен в ~/.bashrc"
        else
            print_info "Алиас уже существует"
        fi
    fi
    
    if [[ -f ~/.zshrc ]]; then
        if ! grep -q "$ALIAS_LINE" ~/.zshrc; then
            echo "$ALIAS_LINE" >> ~/.zshrc
            print_success "Алиас добавлен в ~/.zshrc"
        fi
    fi
}

# Создание systemd сервиса
create_systemd_service() {
    print_info "Создание systemd сервиса..."
    
    read -p "Создать systemd сервис? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cat > /etc/systemd/system/fastwg.service << EOF
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
        
        systemctl daemon-reload
        systemctl enable fastwg.service
        print_success "Systemd сервис создан и включен"
    fi
}

# Автоматический скан после установки
auto_scan_after_install() {
    print_info "Автоматическое сканирование существующих конфигураций..."
    
    if command -v fastwg &> /dev/null; then
        print_info "Выполняется скан WireGuard конфигураций..."
        if fastwg scan; then
            print_success "Скан завершен успешно"
        else
            print_warning "Скан завершен с предупреждениями (это нормально для новой установки)"
        fi
    else
        print_warning "FastWG не найден в PATH, скан пропущен"
    fi
}

# Основная функция
main() {
    echo "=========================================="
    echo "FastWG Installer"
    echo "=========================================="
    
    check_root
    detect_distro
    print_info "Дистрибутив: $OS $VER"
    
    install_dependencies
    check_python
    clone_repo
    install_python_deps
    install_fastwg
    verify_installation
    create_alias
    create_systemd_service
    
    # Автоматический скан после установки
    auto_scan_after_install
    
    echo "=========================================="
    print_success "Установка завершена!"
    echo "=========================================="
    print_info "Использование:"
    print_info "  fastwg --help          # Справка"
    print_info "  fastwg scan            # Сканирование конфигураций"
    print_info "  fastwg create client   # Создание клиента"
    print_info "  fastwg list            # Список клиентов"
    print_info ""
    print_info "Или используйте алиас:"
    print_info "  wg --help"
    print_info "  wg create client"
    print_info ""
    print_warning "Не забудьте перезагрузить shell или выполнить:"
    print_info "  source ~/.bashrc"
}

# Обработка аргументов
case "${1:-}" in
    --help|-h)
        echo "FastWG Installer"
        echo "Использование: $0 [опции]"
        echo ""
        echo "Опции:"
        echo "  --help, -h    Показать эту справку"
        echo "  --uninstall   Удалить FastWG"
        exit 0
        ;;
    --uninstall)
        print_info "Удаление FastWG..."
        
        # Удаляем Python пакет
        pip3 uninstall -y fastwg
        
        # Удаляем исполняемые файлы
        rm -f /usr/local/bin/fastwg
        rm -f /usr/bin/fastwg
        
        # Удаляем systemd сервис
        systemctl disable fastwg.service 2>/dev/null || true
        rm -f /etc/systemd/system/fastwg.service
        systemctl daemon-reload
        
        # Удаляем конфигурационные файлы
        print_info "Удаление конфигурационных файлов..."
        rm -rf /etc/wireguard
        rm -rf ./wireguard
        
        # Удаляем базу данных
        print_info "Удаление базы данных..."
        rm -f ./wireguard.db
        rm -f /var/lib/fastwg/wireguard.db 2>/dev/null || true
        
        # Удаляем пустую директорию /var/lib/fastwg
        if [[ -d "/var/lib/fastwg" ]] && [[ -z "$(ls -A /var/lib/fastwg)" ]]; then
            rmdir /var/lib/fastwg
        fi
        
        # Удаляем алиас
        sed -i '/alias wg=fastwg/d' ~/.bashrc 2>/dev/null || true
        
        print_success "FastWG полностью удален"
        exit 0
        ;;
    *)
        main
        ;;
esac
