"""
Approve — out-of-band approval of a challenged command.

macOS: Touch ID via PyObjC LocalAuthentication (async reply block,
       bridged to synchronous with threading.Event).
Linux / fallback / --totp: interactive TOTP.
"""

import json
import os
import sys
import threading
import time

from rich.console import Console

from .crypto import approved_dir, challenges_dir, APPROVAL_TTL_SECONDS

console = Console()


def authenticate_macos() -> bool:
    try:
        from LocalAuthentication import LAContext, LAPolicyDeviceOwnerAuthentication
    except ImportError:
        console.print("[yellow]⚠️ PyObjC LocalAuthentication not installed. "
                      "(pipx inject aiguard-gate 'aiguard-gate[macos]')[/yellow]")
        return False

    try:
        context = LAContext.alloc().init()
        can_eval, _ = context.canEvaluatePolicy_error_(LAPolicyDeviceOwnerAuthentication, None)
        if not can_eval:
            return False

        done = threading.Event()
        result = {"success": False}

        def reply(success, error):
            result["success"] = bool(success)
            done.set()

        context.evaluatePolicy_localizedReason_reply_(
            LAPolicyDeviceOwnerAuthentication, "AIGuard Command Approval", reply
        )
        done.wait(timeout=60)
        return result["success"]
    except Exception:
        return False


def authenticate(force_totp: bool = False) -> bool:
    if not force_totp and sys.platform == "darwin":
        if authenticate_macos():
            return True
        console.print("[yellow]⚠️ Touch ID unavailable. Falling back to TOTP.[/yellow]")

    from .totp import verify_totp_interactive
    return verify_totp_interactive()


def approve_command(token: str, force_totp: bool = False) -> None:
    challenge_path = challenges_dir() / f"{token}.json"
    if not challenge_path.exists():
        console.print(f"[red]❌ Challenge '{token}' not found or already resolved.[/red]")
        sys.exit(1)

    with open(challenge_path, "r") as f:
        challenge = json.load(f)

    console.print("\n[bold cyan]🛡️ AIGuard Approval Request[/bold cyan]")
    console.print(f"Command: [bold white]{challenge['command']}[/bold white]")
    console.print(f"Risk: [bold yellow]{challenge['risk'].upper()}[/bold yellow]")
    console.print(f"Reason: {challenge['warning']}\n")

    if not authenticate(force_totp=force_totp):
        console.print("[bold red]❌ Authentication failed. Command remains blocked.[/bold red]")
        sys.exit(1)

    challenge["approved_at"] = time.time()
    challenge["expires_at"] = challenge["approved_at"] + APPROVAL_TTL_SECONDS

    approved_path = approved_dir() / f"{token}.json"
    fd = os.open(approved_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(challenge, f)
    challenge_path.unlink()

    console.print("[bold green]✅ Approved. The AI can now retry this exact command.[/bold green]")
