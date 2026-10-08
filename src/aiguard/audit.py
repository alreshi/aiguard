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
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": time.time(),
        "command": command,
        "action": decision["action"],
        "risk": decision["risk"],
        "warning": decision["warning"],
    }
    with open(path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    os.chmod(path, 0o600)
