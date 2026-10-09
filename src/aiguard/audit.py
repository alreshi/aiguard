"""
Audit Logger — appends every Decision to ~/.aiguard/audit.jsonl.

Commands are logged VERBATIM and may contain secrets. The log is always
kept at 0600, including when it already exists with looser permissions.
"""

import json
import os
import time
from pathlib import Path


def audit_path() -> Path:
    return Path.home() / ".aiguard" / "audit.jsonl"


def log_decision(command: str, decision: dict) -> None:
    path = audit_path()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    entry = {
        "timestamp": time.time(),
        "command": command,
        "action": decision["action"],
        "risk": decision["risk"],
        "warning": decision["warning"],
    }
    # 0600 from creation (no umask window); chmod repairs a pre-existing
    # file with looser permissions.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    with os.fdopen(fd, "a") as f:
        f.write(json.dumps(entry) + "\n")
    os.chmod(path, 0o600)
