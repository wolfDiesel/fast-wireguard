#!/usr/bin/env python3

import os
import sys

import click
from colorama import Fore, Style, init
from tabulate import tabulate

from .core.wireguard import WireGuardManager
from .utils.i18n import gettext as _

# Initialize colorama for colored output
init(autoreset=True)


def check_root_privileges() -> None:
    """Check for root privileges"""
    if os.geteuid() != 0:
        click.echo(
            f"{Fore.RED}{_('Error: Root privileges required for WireGuard operations')}{Style.RESET_ALL}"
        )
        click.echo(_("Run the command with sudo"))
        sys.exit(1)


@click.group()
@click.version_option(version="1.0.4", prog_name="fastwg")
def cli():
    """FastWG - Fast WireGuard server management"""
    check_root_privileges()


@cli.command()
@click.option(
    "--config-dir", default="/etc/wireguard", help="WireGuard configuration directory"
)
def scan(config_dir: str) -> None:
    """Scan existing WireGuard configurations"""
    click.echo(
        f"{Fore.YELLOW}{_('Scanning existing configurations...')}{Style.RESET_ALL}"
    )

    wg = WireGuardManager(config_dir)
    existing_configs = wg.scan_existing_configs()

    if not existing_configs:
        click.echo(
            f"{Fore.GREEN}{_('No existing configurations found')}{Style.RESET_ALL}"
        )
        return

    click.echo(
        f"{Fore.GREEN}{_('Found configurations: {}').format(len(existing_configs))}{Style.RESET_ALL}"
    )

    for config in existing_configs:
        click.echo(f"  - {config['filename']} ({config['path']})")

    if click.confirm(_("Import found configurations?")):
        for config in existing_configs:
            if wg.import_existing_config(config["path"]):
                click.echo(
                    f"{Fore.GREEN}{_('✓ Imported: {}').format(config['filename'])}{Style.RESET_ALL}"
                )
            else:
                click.echo(
                    f"{Fore.RED}{_('✗ Import error: {}').format(config['filename'])}{Style.RESET_ALL}"
                )


@cli.command()
@click.argument("name")
def create(name: str) -> None:
    """Create new client"""
    click.echo(
        f"{Fore.YELLOW}{_('Creating client {}...').format(name)}{Style.RESET_ALL}"
    )

    wg = WireGuardManager()
    client = wg.create_client(name)

    if client:
        click.echo(
            f"{Fore.GREEN}{_('✓ Client {} successfully created').format(name)}{Style.RESET_ALL}"
        )
        click.echo(f"  {_('IP address')}: {client.ip_address}")
        click.echo(f"  {_('Configuration')}: ./wireguard/configs/{name}.conf")
    else:
        click.echo(
            f"{Fore.RED}{_('✗ Error creating client {}').format(name)}{Style.RESET_ALL}"
        )


@cli.command()
@click.argument("name")
def delete(name: str) -> None:
    """Delete client"""
    if not click.confirm(_("Delete client '{}'?").format(name)):
        return

    click.echo(
        f"{Fore.YELLOW}{_('Deleting client {}...').format(name)}{Style.RESET_ALL}"
    )

    wg = WireGuardManager()
    if wg.delete_client(name):
        click.echo(
            f"{Fore.GREEN}{_('✓ Client {} successfully deleted').format(name)}{Style.RESET_ALL}"
        )
    else:
        click.echo(
            f"{Fore.RED}{_('✗ Error deleting client {}').format(name)}{Style.RESET_ALL}"
        )


@cli.command()
@click.argument("name")
def disable(name: str) -> None:
    """Disable client"""
    click.echo(
        f"{Fore.YELLOW}{_('Disabling client {}...').format(name)}{Style.RESET_ALL}"
    )

    wg = WireGuardManager()
    if wg.disable_client(name):
        click.echo(
            f"{Fore.GREEN}{_('✓ Client {} disabled').format(name)}{Style.RESET_ALL}"
        )
    else:
        click.echo(
            f"{Fore.RED}{_('✗ Error disabling client {}').format(name)}{Style.RESET_ALL}"
        )


@cli.command()
@click.argument("name")
def enable(name: str) -> None:
    """Enable client"""
    click.echo(
        f"{Fore.YELLOW}{_('Enabling client {}...').format(name)}{Style.RESET_ALL}"
    )

    wg = WireGuardManager()
    if wg.enable_client(name):
        click.echo(
            f"{Fore.GREEN}{_('✓ Client {} enabled').format(name)}{Style.RESET_ALL}"
        )
    else:
        click.echo(
            f"{Fore.RED}{_('✗ Error enabling client {}').format(name)}{Style.RESET_ALL}"
        )


@cli.command()
@click.argument("name")
def cat(name: str) -> None:
    """Show client configuration"""
    wg_manager = WireGuardManager()
    config = wg_manager.get_client_config(name)

    if config:
        click.echo(
            f"{Fore.CYAN}{_('Client {} configuration:').format(name)}{Style.RESET_ALL}"
        )
        click.echo("=" * 50)
        click.echo(config)
    else:
        click.echo(
            f"{Fore.RED}{_('Client {} not found or configuration missing').format(name)}{Style.RESET_ALL}"
        )


@cli.command()
@click.option(
    "--all",
    "-a",
    is_flag=True,
    help=_("Show all clients including inactive and blocked"),
)
def list(all: bool) -> None:
    """Show list of all clients"""
    wg_manager = WireGuardManager()
    clients = wg_manager.list_clients()

    if not clients:
        click.echo(f"{Fore.YELLOW}{_('No clients found')}{Style.RESET_ALL}")
        return

    # Filter clients based on --all flag
    if not all:
        # Show only active and connected clients by default
        filtered_clients = [
            client
            for client in clients
            if client["is_active"] and not client["is_blocked"]
        ]
        if not filtered_clients:
            click.echo(
                f"{Fore.YELLOW}{_('No active clients found. Use --all to show all clients.')}{Style.RESET_ALL}"
            )
            return
    else:
        filtered_clients = clients

    # Prepare table data
    table_data = []
    for client in filtered_clients:
        status = []
        if client["is_active"]:
            status.append(f"{Fore.GREEN}{_('Active')}{Style.RESET_ALL}")
        else:
            status.append(f"{Fore.RED}{_('Inactive')}{Style.RESET_ALL}")

        if client["is_blocked"]:
            status.append(f"{Fore.RED}{_('Blocked')}{Style.RESET_ALL}")

        if client["is_connected"]:
            status.append(f"{Fore.GREEN}{_('Connected')}{Style.RESET_ALL}")
        else:
            status.append(f"{Fore.YELLOW}{_('Disconnected')}{Style.RESET_ALL}")

        status_str = ", ".join(status)

        last_seen = (
            client["last_seen"].strftime("%Y-%m-%d %H:%M:%S")
            if client["last_seen"]
            else _("Never")
        )
        created_at = (
            client["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            if client["created_at"]
            else _("Unknown")
        )

        table_data.append(
            [client["name"], client["ip_address"], status_str, last_seen, created_at]
        )

    headers = [
        _("Name"),
        _("IP Address"),
        _("Status"),
        _("Last Connection"),
        _("Created"),
    ]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))


@cli.command()
def status() -> None:
    """Show WireGuard server status"""

    # Check WireGuard status
    try:
        import subprocess

        result = subprocess.run(["wg", "show"], capture_output=True, text=True)

        if result.returncode == 0:
            click.echo(f"{Fore.GREEN}{_('✓ WireGuard is active')}{Style.RESET_ALL}")
            click.echo(f"\n{_('Active interfaces')}:")
            click.echo(result.stdout)
        else:
            click.echo(f"{Fore.RED}{_('✗ WireGuard is not active')}{Style.RESET_ALL}")
    except FileNotFoundError:
        click.echo(f"{Fore.RED}{_('✗ WireGuard is not installed')}{Style.RESET_ALL}")


@cli.command()
def start() -> None:
    """Start WireGuard server"""
    wg_manager = WireGuardManager()
    if wg_manager.start_server():
        click.echo(f"{Fore.GREEN}{_('✓ Server started successfully')}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}{_('✗ Failed to start server')}{Style.RESET_ALL}")


@cli.command()
def stop() -> None:
    """Stop WireGuard server"""
    wg_manager = WireGuardManager()
    if wg_manager.stop_server():
        click.echo(f"{Fore.GREEN}{_('✓ Server stopped successfully')}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}{_('✗ Failed to stop server')}{Style.RESET_ALL}")


@cli.command()
def restart() -> None:
    """Restart WireGuard server"""
    wg_manager = WireGuardManager()
    if wg_manager.restart_server():
        click.echo(
            f"{Fore.GREEN}{_('✓ Server restarted successfully')}{Style.RESET_ALL}"
        )
    else:
        click.echo(f"{Fore.RED}{_('✗ Failed to restart server')}{Style.RESET_ALL}")


@cli.command()
def reload() -> None:
    """Reload server configuration"""
    wg_manager = WireGuardManager()
    if wg_manager.reload_config():
        click.echo(
            f"{Fore.GREEN}{_('✓ Configuration reloaded successfully')}{Style.RESET_ALL}"
        )
    else:
        click.echo(
            f"{Fore.RED}{_('✗ Failed to reload configuration')}{Style.RESET_ALL}"
        )


@cli.command()
@click.argument("host")
def sethost(host: str) -> None:
    """Set external host (IP:port) for WireGuard server"""
    wg_manager = WireGuardManager()
    if wg_manager.set_host(host):
        click.echo(f"{Fore.GREEN}{_('✓ Host set successfully')}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}{_('✗ Failed to set host')}{Style.RESET_ALL}")


@cli.command()
@click.option("--interface", default="wg0", help="Interface name")
@click.option("--port", default=51820, help="Listen port")
@click.option("--network", default="10.42.42.0/24", help="Network address")
@click.option("--dns", default="8.8.8.8", help="DNS server")
def init_server(interface: str, port: int, network: str, dns: str) -> None:
    """Initialize WireGuard server configuration"""
    click.echo(
        f"{Fore.YELLOW}{_('Initializing WireGuard server configuration...')}{Style.RESET_ALL}"
    )

    wg_manager = WireGuardManager()
    if wg_manager.init_server_config(interface, port, network, dns):
        click.echo(
            f"{Fore.GREEN}{_('✓ Server configuration initialized successfully')}{Style.RESET_ALL}"
        )
        click.echo(f"  {_('Interface')}: {interface}")
        click.echo(f"  {_('Port')}: {port}")
        click.echo(f"  {_('Network')}: {network}")
        click.echo(f"  {_('DNS')}: {dns}")
        click.echo(f"\n{_('Next steps:')}")
        click.echo(f"  1. {_('Set external host')}: fastwg sethost <your_ip>:<port>")
        click.echo(f"  2. {_('Start server')}: fastwg start")
        click.echo(f"  3. {_('Create clients')}: fastwg create <client_name>")
    else:
        click.echo(
            f"{Fore.RED}{_('✗ Failed to initialize server configuration')}{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    cli()
