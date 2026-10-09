"""
Crypto/state — challenge tokens, approvals, and opportunistic GC.

Paths are computed lazily from Path.home() so tests can isolate home.
"""

import hashlib
import json
import os
import time
from pathlib import Path

APPROVAL_TTL_SECONDS = 300  # approvals expire 5 minutes after approval
CHALLENGE_TTL_SECONDS = 3600  # unapproved challenges are pruned after 1 hour


def base_dir() -> Path:
    return Path.home() / ".aiguard"


def challenges_dir() -> Path:
    return base_dir() / "challenges"


def approved_dir() -> Path:
    return base_dir() / "approved"


def init_dirs() -> None:
    for d in (base_dir(), challenges_dir(), approved_dir()):
        d.mkdir(parents=True, exist_ok=True)
        os.chmod(d, 0o700)


def hash_command(command: str) -> str:
    """12-character deterministic token for an exact command string."""
    return hashlib.sha256(command.encode("utf-8")).hexdigest()[:12]


def create_challenge(command: str, risk: str, warning: str) -> str:
    init_dirs()
    token = hash_command(command)
    challenge = {
        "command": command,
        "risk": risk,
        "warning": warning,
        "created_at": time.time(),
    }
    challenge_path = challenges_dir() / f"{token}.json"
    fd = os.open(challenge_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(challenge, f)
    return token


def prune_expired() -> None:
    """Opportunistic GC: remove stale challenges and expired approvals."""
    now = time.time()
    for directory, field, ttl in (
        (challenges_dir(), "created_at", CHALLENGE_TTL_SECONDS),
        (approved_dir(), "expires_at", None),
    ):
        if not directory.exists():
            continue
        for file in directory.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                if ttl is not None:
                    if now - data.get(field, 0) > ttl:
                        file.unlink()
                elif now > data.get(field, 0):
                    file.unlink()
            except Exception:
                pass


def consume_approval(token: str) -> bool:
    """Return True once if a valid approval exists; single-use consumption."""
    approved_path = approved_dir() / f"{token}.json"
    if not approved_path.exists():
        return False
    try:
        with open(approved_path) as f:
            data = json.load(f)
        if time.time() > data.get("expires_at", 0):
            approved_path.unlink()
            return False
        approved_path.unlink()
        return True
    except Exception:
        return False
