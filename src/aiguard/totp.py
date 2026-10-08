"""
TOTP — RFC 6238 (SHA-1, 6 digits, 30s period, verify window ±1).

Secret storage: system keyring via `keyring`; on platforms without a
backend (e.g. headless Linux) falls back to a 0600 file with a warning.
Rate limiting: 3 failed attempts -> 5-minute lockout, tracked on disk.
"""

import json
import os
import time
from pathlib import Path

import keyring
import pyotp
from keyring.errors import KeyringLocked, NoKeyringError
from rich.console import Console
from rich.prompt import Prompt

console = Console()
SERVICE_NAME = "aiguard-cli"
USERNAME = "totp-secret"
MAX_ATTEMPTS = 3
LOCKOUT_DURATION = 300  # seconds


def _fallback_path() -> Path:
    return Path.home() / ".aiguard" / "totp-secret"


def _lockout_path() -> Path:
    return Path.home() / ".aiguard" / "totp-lockout"


def _load_secret() -> str | None:
    try:
        secret = keyring.get_password(SERVICE_NAME, USERNAME)
        if secret:
            return secret
    except (NoKeyringError, KeyringLocked):
        pass
    except Exception:
        pass
    path = _fallback_path()
    if path.exists():
        return path.read_text().strip()
    return None


def _save_secret(secret: str) -> None:
    try:
        keyring.set_password(SERVICE_NAME, USERNAME, secret)
        console.print("[green]✅ Secret stored in system keyring.[/green]")
        return
    except (NoKeyringError, KeyringLocked):
        pass
    except Exception:
        pass
    path = _fallback_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(secret)
    os.chmod(path, 0o600)
    console.print(
        "[yellow]⚠️ No usable system keyring. Secret stored in "
        "~/.aiguard/totp-secret (0600).[/yellow]"
    )


def setup_totp() -> None:
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret, digits=6, interval=30)

    console.print("\n📱 Add this to your authenticator app:")
    console.print(f"[cyan]{totp.provisioning_uri(name='aiguard', issuer_name='AIGuard')}[/cyan]\n")
    console.print(f"📝 Or enter manually: [yellow]{secret}[/yellow]\n")

    code = Prompt.ask("🔍 Enter the current 6-digit code to verify")
    if not totp.verify(code, valid_window=1):
        console.print("[bold red]❌ Verification failed. Secret not saved.[/bold red]")
        raise SystemExit(1)

    _save_secret(secret)
    console.print("[bold green]✅ TOTP configured successfully![/bold green]")


def get_totp_engine() -> pyotp.TOTP | None:
    secret = _load_secret()
    if not secret:
        return None
    return pyotp.TOTP(secret, digits=6, interval=30)


def _check_lockout() -> bool:
    path = _lockout_path()
    if path.exists():
        try:
            data = json.loads(path.read_text())
            if time.time() < data.get("locked_until", 0):
                return False
        except Exception:
            pass
    return True


def _record_failure() -> None:
    path = _lockout_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    attempts = 1
    if path.exists():
        try:
            attempts = json.loads(path.read_text()).get("attempts", 0) + 1
        except Exception:
            pass

    if attempts >= MAX_ATTEMPTS:
        data = {"attempts": 0, "locked_until": time.time() + LOCKOUT_DURATION}
        console.print("[red]🔒 Too many failed attempts. Locked for 5 minutes.[/red]")
    else:
        data = {"attempts": attempts, "locked_until": 0}

    path.write_text(json.dumps(data))
    os.chmod(path, 0o600)


def verify_totp_interactive() -> bool:
    if not _check_lockout():
        console.print("[red]🔒 TOTP is locked out. Try again later.[/red]")
        return False

    engine = get_totp_engine()
    if not engine:
        console.print("[red]❌ TOTP not configured. Run 'aiguard setup' first.[/red]")
        return False

    code = Prompt.ask("🔑 Enter 6-digit TOTP code")
    if engine.verify(code, valid_window=1):
        path = _lockout_path()
        if path.exists():
            path.unlink()
        return True

    _record_failure()
    return False
