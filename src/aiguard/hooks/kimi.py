"""
Kimi Code CLI — PreToolUse hook installer.

Config is TOML at ~/.kimi-code/config.toml. Install is append-only text
(never rewrites the file, preserving comments/formatting); uninstall
removes the marker-delimited block. Both back up before writing.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

from .base import HookInstaller

HOOK_BLOCK = '''
# Added by AIGuard
[[hooks]]
event = "PreToolUse"
matcher = "Bash"
command = "aiguard-evaluate"
timeout = 10
'''

HOOK_BLOCK_RE = re.compile(
    r'\n# Added by AIGuard\n\[\[hooks\]\]\nevent = "PreToolUse"\n'
    r'matcher = "Bash"\ncommand = "aiguard-evaluate"\ntimeout = 10\n'
)


class KimiHookInstaller(HookInstaller):
    name = "kimi"
    display_name = "Kimi Code CLI"

    def get_config_path(self) -> Path:
        return Path.home() / ".kimi-code" / "config.toml"

    def is_installed(self) -> bool:
        return shutil.which("kimi") is not None

    def _backup(self, config_path: Path) -> None:
        if config_path.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = config_path.with_suffix(f".toml.backup-{stamp}")
            shutil.copy(config_path, backup)
            print(f"✅ Backed up existing config to {backup}")

    def install_hook(self) -> None:
        config_path = self.get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        content = config_path.read_text() if config_path.exists() else ""
        if 'command = "aiguard-evaluate"' in content:
            print("⚠️  AIGuard hook already installed. Skipping.")
            return

        self._backup(config_path)
        with open(config_path, "a") as f:
            f.write(HOOK_BLOCK)
        print(f"✅ Installed AIGuard hook into {config_path}")

    def uninstall_hook(self) -> None:
        config_path = self.get_config_path()
        if not config_path.exists():
            return

        content = config_path.read_text()
        new_content = HOOK_BLOCK_RE.sub("\n", content)
        if new_content == content:
            print("⚠️  AIGuard hook not found.")
            return

        self._backup(config_path)
        config_path.write_text(new_content)
        print(f"✅ Removed AIGuard hook from {config_path}")
