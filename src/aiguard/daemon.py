"""
Daemon — watches for new challenges and raises desktop notifications.

Notification state follows the filesystem: a challenge is (re)notified
whenever its file appears or changes, so a re-challenged command always
re-notifies. Informational only — approval happens via `aiguard approve`.
"""

import json
import os
import subprocess
import time

from .crypto import base_dir, challenges_dir


def notify_macos(token: str, command: str) -> None:
    # Injection-safe: dynamic text is passed as argv, never interpolated
    # into AppleScript source.
    script = (
        "on run argv\n"
        'display notification "Run: aiguard approve " & (item 1 of argv) '
        'with title "🛡️ AIGuard: Approval Required" subtitle (item 2 of argv)\n'
        "end run"
    )
    subprocess.run(
        ["osascript", "-e", script, token, command[:50]],
        capture_output=True,
    )


def notify_linux(token: str, command: str) -> None:
    subprocess.run(
        [
            "notify-send", "-u", "critical",
            "🛡️ AIGuard: Approval Required",
            f"Run: aiguard approve {token}\n{command[:50]}",
        ],
        capture_output=True,
    )


def main() -> None:
    base_dir().mkdir(parents=True, exist_ok=True)
    active_challenges: dict[str, float] = {}

    print("🛡️ AIGuard Daemon started. Monitoring for challenges...")
    while True:
        try:
            directory = challenges_dir()
            current_files = (
                {f.stem: f.stat().st_mtime for f in directory.glob("*.json")}
                if directory.exists()
                else {}
            )

            for token, mtime in current_files.items():
                if active_challenges.get(token) != mtime:
                    active_challenges[token] = mtime
                    with open(directory / f"{token}.json") as f:
                        data = json.load(f)
                    command = data.get("command", "Unknown command")
                    if os.uname().sysname == "Darwin":
                        notify_macos(token, command)
                    else:
                        notify_linux(token, command)

            for token in list(active_challenges):
                if token not in current_files:
                    del active_challenges[token]
        except Exception:
            pass  # the daemon must never crash

        time.sleep(2)


if __name__ == "__main__":
    main()
