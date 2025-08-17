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

# Проверка WireGuard
check_wireguard() {
    print_info "Проверка WireGuard..."
    
    if ! command -v wg &> /dev/null; then
        print_warning "WireGuard не найден в системе"
        print_info "FastWG требует установленный WireGuard для работы"
        
        read -p "Установить WireGuard? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Установка WireGuard..."
            
            case $OS in
                *"Ubuntu"*|*"Debian"*)
                    apt update
                    apt install -y wireguard wireguard-tools
                    ;;
                *"Fedora"*|*"Red Hat"*|*"CentOS"*)
                    dnf install -y wireguard-tools
                    ;;
                *"Arch"*)
                    pacman -S --noconfirm wireguard-tools
                    ;;
                *)
                    print_error "Неизвестный дистрибутив: $OS"
                    print_info "Установите WireGuard вручную:"
                    print_info "  Ubuntu/Debian: apt install wireguard wireguard-tools"
                    print_info "  Fedora/RHEL: dnf install wireguard-tools"
                    print_info "  Arch: pacman -S wireguard-tools"
                    exit 1
                    ;;
            esac
            
            print_success "WireGuard установлен"
        else
            print_error "WireGuard не установлен. FastWG не может работать без WireGuard"
            exit 1
        fi
    else
        print_success "WireGuard найден"
        
        # Проверяем wg-quick
        if ! command -v wg-quick &> /dev/null; then
            print_warning "wg-quick не найден"
            print_info "Установка wireguard-tools..."
            
            case $OS in
                *"Ubuntu"*|*"Debian"*)
                    apt install -y wireguard-tools
                    ;;
                *"Fedora"*|*"Red Hat"*|*"CentOS"*)
                    dnf install -y wireguard-tools
                    ;;
                *"Arch"*)
                    pacman -S --noconfirm wireguard-tools
                    ;;
            esac
            
            print_success "wireguard-tools установлен"
        else
            print_success "wg-quick найден"
        fi
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
    check_wireguard
    clone_repo
    install_python_deps
    install_fastwg
    verify_installation
    
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
        

        
        # Удаляем только файлы FastWG (не трогаем WireGuard)
        print_info "Удаление файлов FastWG..."
        rm -rf ./wireguard
        
        # Удаляем базу данных
        print_info "Удаление базы данных..."
        rm -f ./wireguard.db
        rm -f /var/lib/fastwg/wireguard.db 2>/dev/null || true
        
        # Удаляем пустую директорию /var/lib/fastwg
        if [[ -d "/var/lib/fastwg" ]] && [[ -z "$(ls -A /var/lib/fastwg)" ]]; then
            rmdir /var/lib/fastwg
        fi
        

        
        print_success "FastWG полностью удален"
        exit 0
        ;;
    *)
        main
        ;;
esac
