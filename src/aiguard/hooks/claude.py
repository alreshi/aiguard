"""
Claude Code — PreToolUse hook installer.

Config is JSON at ~/.claude/settings.json. Install merges (never
clobbers existing hooks or settings), refuses on malformed config,
and backs up before writing.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path

from .base import HookInstaller

HOOK_COMMAND = "aiguard-evaluate"


class ClaudeHookInstaller(HookInstaller):
    name = "claude"
    display_name = "Claude Code"

    def get_config_path(self) -> Path:
        return Path.home() / ".claude" / "settings.json"

    def is_installed(self) -> bool:
        return shutil.which("claude") is not None

    def _backup(self, config_path: Path) -> None:
        if config_path.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = config_path.with_suffix(f".json.backup-{stamp}")
            shutil.copy(config_path, backup)
            print(f"✅ Backed up existing config to {backup}")

    def _load(self, config_path: Path) -> dict:
        if not config_path.exists():
            return {}
        try:
            return json.loads(config_path.read_text())
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Malformed settings.json, refusing to modify: {e}")

    def install_hook(self) -> None:
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = self._load(config_path)

        for group in config.get("hooks", {}).get("PreToolUse", []):
            for hook in group.get("hooks", []):
                if hook.get("command", "").startswith("aiguard"):
                    print("⚠️  AIGuard hook already installed. Skipping.")
                    return

        self._backup(config_path)
        config.setdefault("hooks", {}).setdefault("PreToolUse", []).append({
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": HOOK_COMMAND}],
        })
        config_path.write_text(json.dumps(config, indent=2))
        print(f"✅ Installed AIGuard hook into {config_path}")

    def uninstall_hook(self) -> None:
        config_path = self.get_config_path()
        if not config_path.exists():
            return

        config = self._load(config_path)
        groups = config.get("hooks", {}).get("PreToolUse")
        if not groups:
            print("⚠️  AIGuard hook not found.")
            return

        kept = [
            group for group in groups
            if not any(
                hook.get("command", "").startswith("aiguard")
                for hook in group.get("hooks", [])
            )
        ]
        if len(kept) == len(groups):
            print("⚠️  AIGuard hook not found.")
            return

        self._backup(config_path)
        config["hooks"]["PreToolUse"] = kept
        config_path.write_text(json.dumps(config, indent=2))
        print(f"✅ Removed AIGuard hook from {config_path}")
