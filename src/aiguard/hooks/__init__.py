"""Hook installers for supported assistants."""

from .base import HookInstaller
from .claude import ClaudeHookInstaller
from .kimi import KimiHookInstaller

__all__ = ["HookInstaller", "ClaudeHookInstaller", "KimiHookInstaller"]
