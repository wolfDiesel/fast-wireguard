#!/usr/bin/env python3

import click
import sys
import os
from colorama import init, Fore, Style
from tabulate import tabulate
from datetime import datetime
from .core.wireguard import WireGuardManager
from .utils.i18n import gettext as _

# Инициализация colorama для цветного вывода
init(autoreset=True)


def check_root_privileges():
    """Check for root privileges"""
    if os.geteuid() != 0:
        click.echo(f"{Fore.RED}{_('Error: Root privileges required for WireGuard operations')}{Style.RESET_ALL}")
        click.echo(_("Run the command with sudo"))
        sys.exit(1)


@click.group()
@click.version_option(version="1.0.0", prog_name="fastwg")
def cli():
    """FastWG - Fast WireGuard server management"""
    check_root_privileges()


@cli.command()
@click.option('--config-dir', default='/etc/wireguard', help='WireGuard configuration directory')
def scan(config_dir):
    """Scan existing WireGuard configurations"""
    click.echo(f"{Fore.YELLOW}{_('Scanning existing configurations...')}{Style.RESET_ALL}")
    
    wg = WireGuardManager(config_dir)
    existing_configs = wg.scan_existing_configs()
    
    if not existing_configs:
        click.echo(f"{Fore.GREEN}{_('No existing configurations found')}{Style.RESET_ALL}")
        return
    
    click.echo(f"{Fore.GREEN}{_('Found configurations: {}').format(len(existing_configs))}{Style.RESET_ALL}")
    
    for config in existing_configs:
        click.echo(f"  - {config['filename']} ({config['path']})")
    
    if click.confirm(_("Import found configurations?")):
        for config in existing_configs:
            if wg.import_existing_config(config['path']):
                click.echo(f"{Fore.GREEN}{_('✓ Imported: {}').format(config['filename'])}{Style.RESET_ALL}")
            else:
                click.echo(f"{Fore.RED}{_('✗ Import error: {}').format(config['filename'])}{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def create(name):
    """Создает нового клиента"""
    click.echo(f"{Fore.YELLOW}Создание клиента '{name}'...{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    client = wg.create_client(name)
    
    if client:
        click.echo(f"{Fore.GREEN}✓ Клиент '{name}' успешно создан{Style.RESET_ALL}")
        click.echo(f"  IP адрес: {client.ip_address}")
        click.echo(f"  Конфигурация: ./wireguard/configs/{name}.conf")
    else:
        click.echo(f"{Fore.RED}✗ Ошибка создания клиента '{name}'{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def delete(name):
    """Удаляет клиента"""
    if not click.confirm(f"Удалить клиента '{name}'?"):
        return
    
    click.echo(f"{Fore.YELLOW}Удаление клиента '{name}'...{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    if wg.delete_client(name):
        click.echo(f"{Fore.GREEN}✓ Клиент '{name}' успешно удален{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}✗ Ошибка удаления клиента '{name}'{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def disable(name):
    """Блокирует клиента"""
    click.echo(f"{Fore.YELLOW}Блокировка клиента '{name}'...{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    if wg.disable_client(name):
        click.echo(f"{Fore.GREEN}✓ Клиент '{name}' заблокирован{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}✗ Ошибка блокировки клиента '{name}'{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def enable(name):
    """Разблокирует клиента"""
    click.echo(f"{Fore.YELLOW}Разблокировка клиента '{name}'...{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    if wg.enable_client(name):
        click.echo(f"{Fore.GREEN}✓ Клиент '{name}' разблокирован{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}✗ Ошибка разблокировки клиента '{name}'{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def cat(name):
    """Показывает конфигурацию клиента"""
    wg = WireGuardManager()
    config = wg.get_client_config(name)
    
    if config:
        click.echo(f"{Fore.CYAN}Конфигурация клиента '{name}':{Style.RESET_ALL}")
        click.echo("=" * 50)
        click.echo(config)
    else:
        click.echo(f"{Fore.RED}Клиент '{name}' не найден или конфигурация отсутствует{Style.RESET_ALL}")


@cli.command()
def list():
    """Показывает список всех клиентов"""
    wg = WireGuardManager()
    clients = wg.list_clients()
    
    if not clients:
        click.echo(f"{Fore.YELLOW}Клиенты не найдены{Style.RESET_ALL}")
        return
    
    # Подготавливаем данные для таблицы
    table_data = []
    for client in clients:
        status = []
        if client['is_active']:
            status.append(f"{Fore.GREEN}Активен{Style.RESET_ALL}")
        else:
            status.append(f"{Fore.RED}Неактивен{Style.RESET_ALL}")
        
        if client['is_blocked']:
            status.append(f"{Fore.RED}Заблокирован{Style.RESET_ALL}")
        
        if client['is_connected']:
            status.append(f"{Fore.GREEN}Подключен{Style.RESET_ALL}")
        else:
            status.append(f"{Fore.YELLOW}Отключен{Style.RESET_ALL}")
        
        status_str = ", ".join(status)
        
        last_seen = client['last_seen'].strftime('%Y-%m-%d %H:%M:%S') if client['last_seen'] else 'Никогда'
        created_at = client['created_at'].strftime('%Y-%m-%d %H:%M:%S') if client['created_at'] else 'Неизвестно'
        
        table_data.append([
            client['name'],
            client['ip_address'],
            status_str,
            last_seen,
            created_at
        ])
    
    headers = ['Имя', 'IP адрес', 'Статус', 'Последнее подключение', 'Создан']
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@cli.command()
def status():
    """Показывает статус WireGuard сервера"""
    wg = WireGuardManager()
    
    # Проверяем статус WireGuard
    try:
        import subprocess
        result = subprocess.run(['wg', 'show'], capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo(f"{Fore.GREEN}✓ WireGuard активен{Style.RESET_ALL}")
            click.echo("\nАктивные интерфейсы:")
            click.echo(result.stdout)
        else:
            click.echo(f"{Fore.RED}✗ WireGuard не активен{Style.RESET_ALL}")
    except FileNotFoundError:
        click.echo(f"{Fore.RED}✗ WireGuard не установлен{Style.RESET_ALL}")


if __name__ == '__main__':
    cli()
