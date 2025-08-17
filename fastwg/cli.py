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
    """Create new client"""
    click.echo(f"{Fore.YELLOW}{_('Creating client {}...').format(name)}{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    client = wg.create_client(name)
    
    if client:
        click.echo(f"{Fore.GREEN}{_('✓ Client {} successfully created').format(name)}{Style.RESET_ALL}")
        click.echo(f"  {_('IP address')}: {client.ip_address}")
        click.echo(f"  {_('Configuration')}: ./wireguard/configs/{name}.conf")
    else:
        click.echo(f"{Fore.RED}{_('✗ Error creating client {}').format(name)}{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def delete(name):
    """Delete client"""
    if not click.confirm(_("Delete client '{}'?").format(name)):
        return
    
    click.echo(f"{Fore.YELLOW}{_('Deleting client {}...').format(name)}{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    if wg.delete_client(name):
        click.echo(f"{Fore.GREEN}{_('✓ Client {} successfully deleted').format(name)}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}{_('✗ Error deleting client {}').format(name)}{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def disable(name):
    """Disable client"""
    click.echo(f"{Fore.YELLOW}{_('Disabling client {}...').format(name)}{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    if wg.disable_client(name):
        click.echo(f"{Fore.GREEN}{_('✓ Client {} disabled').format(name)}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}{_('✗ Error disabling client {}').format(name)}{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def enable(name):
    """Enable client"""
    click.echo(f"{Fore.YELLOW}{_('Enabling client {}...').format(name)}{Style.RESET_ALL}")
    
    wg = WireGuardManager()
    if wg.enable_client(name):
        click.echo(f"{Fore.GREEN}{_('✓ Client {} enabled').format(name)}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}{_('✗ Error enabling client {}').format(name)}{Style.RESET_ALL}")


@cli.command()
@click.argument('name')
def cat(name):
    """Show client configuration"""
    wg = WireGuardManager()
    config = wg.get_client_config(name)
    
    if config:
        click.echo(f"{Fore.CYAN}{_('Client {} configuration:').format(name)}{Style.RESET_ALL}")
        click.echo("=" * 50)
        click.echo(config)
    else:
        click.echo(f"{Fore.RED}{_('Client {} not found or configuration missing').format(name)}{Style.RESET_ALL}")


@cli.command()
def list():
    """Show list of all clients"""
    wg = WireGuardManager()
    clients = wg.list_clients()
    
    if not clients:
        click.echo(f"{Fore.YELLOW}{_('No clients found')}{Style.RESET_ALL}")
        return
    
    # Prepare table data
    table_data = []
    for client in clients:
        status = []
        if client['is_active']:
            status.append(f"{Fore.GREEN}{_('Active')}{Style.RESET_ALL}")
        else:
            status.append(f"{Fore.RED}{_('Inactive')}{Style.RESET_ALL}")
        
        if client['is_blocked']:
            status.append(f"{Fore.RED}{_('Blocked')}{Style.RESET_ALL}")
        
        if client['is_connected']:
            status.append(f"{Fore.GREEN}{_('Connected')}{Style.RESET_ALL}")
        else:
            status.append(f"{Fore.YELLOW}{_('Disconnected')}{Style.RESET_ALL}")
        
        status_str = ", ".join(status)
        
        last_seen = client['last_seen'].strftime('%Y-%m-%d %H:%M:%S') if client['last_seen'] else _('Never')
        created_at = client['created_at'].strftime('%Y-%m-%d %H:%M:%S') if client['created_at'] else _('Unknown')
        
        table_data.append([
            client['name'],
            client['ip_address'],
            status_str,
            last_seen,
            created_at
        ])
    
    headers = [_('Name'), _('IP Address'), _('Status'), _('Last Connection'), _('Created')]
    click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))


@cli.command()
def status():
    """Show WireGuard server status"""
    wg = WireGuardManager()
    
    # Check WireGuard status
    try:
        import subprocess
        result = subprocess.run(['wg', 'show'], capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo(f"{Fore.GREEN}{_('✓ WireGuard is active')}{Style.RESET_ALL}")
            click.echo(f"\n{_('Active interfaces')}:")
            click.echo(result.stdout)
        else:
            click.echo(f"{Fore.RED}{_('✗ WireGuard is not active')}{Style.RESET_ALL}")
    except FileNotFoundError:
        click.echo(f"{Fore.RED}{_('✗ WireGuard is not installed')}{Style.RESET_ALL}")


if __name__ == '__main__':
    cli()
