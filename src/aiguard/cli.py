"""
AIGuard v6.1 CLI — out-of-band command approval for AI coding assistants.
"""

import os
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .hooks.claude import ClaudeHookInstaller
from .hooks.kimi import KimiHookInstaller

console = Console()

HOOK_INSTALLERS = {
    "kimi": KimiHookInstaller(),
    "claude": ClaudeHookInstaller(),
}

PLIST_LABEL = "com.aiguard.daemon"


@click.group()
@click.version_option(version=__version__, prog_name="aiguard")
def cli():
    """🛡️ AIGuard v6.1 — Out-of-band approval for AI coding assistants"""
    pass


@cli.command()
def setup():
    """Configure TOTP (required on Linux, fallback on macOS)."""
    from .totp import setup_totp
    setup_totp()


@cli.command()
@click.argument("assistant_name")
def install(assistant_name: str):
    """Install AIGuard hooks into an AI assistant (kimi, claude)."""
    installer = HOOK_INSTALLERS.get(assistant_name)
    if not installer:
        console.print(f"[red]❌ Unknown assistant: {assistant_name}[/red]")
        console.print(f"Supported: {', '.join(HOOK_INSTALLERS)}")
        sys.exit(1)
    if not installer.is_installed():
        console.print(f"[red]❌ {installer.display_name} is not installed[/red]")
        sys.exit(1)

    try:
        installer.install_hook()
    except Exception as e:
        console.print(f"[red]❌ Installation failed: {e}[/red]")
        sys.exit(1)

    console.print(f"\n[bold green]✅ AIGuard is now protecting {installer.display_name}[/bold green]")
    console.print("[dim]💡 Run 'aiguard setup' (TOTP) and 'aiguard daemon-install' "
                  "(notifications) if you haven't.[/dim]")


@cli.command()
@click.argument("assistant_name")
def uninstall(assistant_name: str):
    """Remove AIGuard hooks from an AI assistant."""
    installer = HOOK_INSTALLERS.get(assistant_name)
    if not installer:
        console.print(f"[red]❌ Unknown assistant: {assistant_name}[/red]")
        sys.exit(1)
    installer.uninstall_hook()


@cli.command("list")
def list_assistants():
    """List supported assistants and their hook status."""
    console.print("[bold cyan]📋 Supported AI Assistants:[/bold cyan]\n")
    for name, installer in HOOK_INSTALLERS.items():
        status = "✅" if installer.is_installed() else "❌"
        console.print(f"  {status} [bold]{installer.display_name}[/bold] ({name})")
        if installer.is_installed():
            config = installer.get_config_path()
            hooked = config.exists() and "aiguard" in config.read_text()
            console.print(f"     {'🛡️ Hooked' if hooked else '⚪ Not hooked'}")


@cli.command()
@click.argument("token")
@click.option("--totp", is_flag=True, help="Force TOTP (skip Touch ID)")
def approve(token: str, totp: bool):
    """Approve a challenged command out-of-band."""
    from .approve import approve_command
    approve_command(token, force_totp=totp)


@cli.command("daemon-start")
def daemon_start():
    """Run the notification daemon in the foreground (Ctrl+C to stop)."""
    from .daemon import main
    main()


def _plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{PLIST_LABEL}.plist"


@cli.command("daemon-install")
def daemon_install():
    """Install the notification daemon as a macOS LaunchAgent."""
    if sys.platform != "darwin":
        console.print("[yellow]⚠️ Auto-install is macOS-only. On Linux, "
                      "run 'aiguard daemon-start' under systemd.[/yellow]")
        sys.exit(1)

    plist_path = _plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    plist_path.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>-m</string>
        <string>aiguard.daemon</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{Path.home()}/.aiguard/daemon.log</string>
    <key>StandardErrorPath</key>
    <string>{Path.home()}/.aiguard/daemon.log</string>
</dict>
</plist>
""")
    result = subprocess.run(
        ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        console.print(f"[red]❌ launchctl bootstrap failed: {result.stderr.strip()}[/red]")
        sys.exit(1)
    console.print("[bold green]✅ Daemon installed and started.[/bold green]")


@cli.command("daemon-uninstall")
def daemon_uninstall():
    """Remove the notification daemon LaunchAgent."""
    if sys.platform != "darwin":
        console.print("[yellow]⚠️ Auto-uninstall is macOS-only.[/yellow]")
        sys.exit(1)

    plist_path = _plist_path()
    if not plist_path.exists():
        console.print("[yellow]⚠️ Daemon is not installed.[/yellow]")
        return
    subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}/{PLIST_LABEL}"],
        capture_output=True,
    )
    plist_path.unlink()
    console.print("[bold green]✅ Daemon uninstalled.[/bold green]")


@cli.command("daemon-status")
def daemon_status():
    """Check whether the notification daemon is running."""
    result = subprocess.run(["pgrep", "-f", "aiguard.daemon"], capture_output=True)
    if result.returncode == 0:
        console.print("[bold green]✅ AIGuard daemon is running.[/bold green]")
    else:
        console.print("[bold yellow]⚠️ Daemon is NOT running — notifications will "
                      "not appear, but 'aiguard approve <token>' still works.[/bold yellow]")


if __name__ == "__main__":
    cli()
