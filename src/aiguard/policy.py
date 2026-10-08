"""
Policy Engine — Priority-ordered, user-extensible, fail-safe.

Decision contract: {"action": "allow"|"ask"|"block", "risk": str, "warning": str}
"""

import re
import sys
import tomllib
from pathlib import Path
from typing import Dict, Any, List, Pattern

# Absolute Block: recursive+force delete of token-exact protected targets.
ABSOLUTE_BLOCK_RE = re.compile(
    r"\brm\s+(?:-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|--recursive\s+--force|--force\s+--recursive)\s+"
    r"(?:/|/\*|~|~/\*|\$HOME|--no-preserve-root)(?:\s|$)"
)

# State store protection: write/delete attempts -> Absolute Block.
# Tolerates no-space redirects (>>~/.aiguard) and ~/, $HOME/ prefixes.
STATE_STORE_BLOCK_RE = re.compile(
    r"(?:>>?|tee)\s*(?:~/|\$HOME/)?\.aiguard"
    r"|(?:cp|mv|ln|install)\s+.*(?:~/|\$HOME/)?\.aiguard(?:/|\s|$)"
    r"|(?:rm|unlink)\s+.*(?:~/|\$HOME/)?\.aiguard"
)

# Any reference to the state store is at minimum ask-tier
# (prevents auto-allow of e.g. `cat ~/.aiguard/audit.jsonl`).
STATE_STORE_ASK_RE = re.compile(r"(?:~/|\$HOME/)?\.aiguard(?:/|\s|$)")

HIGH_RISK_PATTERNS: List[tuple[Pattern, str]] = [
    (re.compile(r"\brm\s+.*(?:-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|--recursive|--force)\b"), "Recursive delete command."),
    (re.compile(r"\bcurl\b.*\|\s*(ba)?sh"), "Downloads and executes remote script."),
    (re.compile(r"\bwget\b.*\|\s*(ba)?sh"), "Downloads and executes remote script."),
    (re.compile(r"\bsudo\b"), "Requires elevated privileges."),
    (re.compile(r"\bdd\b.*of=/dev/"), "Direct disk write."),
    (re.compile(r"\bmkfs\."), "Formats a filesystem."),
    (re.compile(r"\bchmod\s+777\b"), "Sets insecure permissions."),
    (re.compile(r"\bgit\s+push\s+.*--force"), "Force push to git remote."),
    (re.compile(r"\bgit\s+reset\s+--hard"), "Hard reset git history."),
    (re.compile(r"\b(shutdown|reboot)\b"), "System power control."),
]

METACHARACTERS = re.compile(r"[;|&<>`$()\n]")
SAFE_PREFIXES = ["ls", "dir", "pwd", "cd ", "git status", "git log", "git diff", "cat ", "echo "]


def load_user_policy() -> Dict[str, List[Pattern]]:
    """Load, validate, and precompile ~/.aiguard/policy.toml.

    Invalid patterns are skipped with a stderr warning; a malformed file
    falls back to an empty policy. Never raises.
    """
    default_policy: Dict[str, List[Pattern]] = {"allow": [], "ask": [], "block": []}
    policy_path = Path.home() / ".aiguard" / "policy.toml"
    if not policy_path.exists():
        return default_policy

    try:
        with open(policy_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        print(f"AIGuard Warning: Failed to parse policy.toml: {e}", file=sys.stderr)
        return default_policy

    for category in ("allow", "ask", "block"):
        patterns = data.get(category, [])
        if not isinstance(patterns, list):
            continue
        for p in patterns:
            if isinstance(p, str):
                try:
                    default_policy[category].append(re.compile(p, re.IGNORECASE))
                except re.error as e:
                    print(f"AIGuard Warning: Invalid regex in policy.toml '{p}': {e}", file=sys.stderr)
    return default_policy


def evaluate_command(command: str) -> Dict[str, Any]:
    user_policy = load_user_policy()

    # Priority 0: State store writes (Absolute Block, no challenge)
    if STATE_STORE_BLOCK_RE.search(command):
        return {"action": "block", "risk": "critical", "warning": "BLOCKED: Cannot modify AIGuard state."}

    # Priority 1: Absolute Blocks (no challenge, final)
    if ABSOLUTE_BLOCK_RE.search(command):
        return {"action": "block", "risk": "critical", "warning": "BLOCKED: Recursive delete on protected target."}

    # Priority 2: User block patterns (no challenge, final)
    for pattern in user_policy["block"]:
        if pattern.search(command):
            return {"action": "block", "risk": "critical", "warning": "BLOCKED by user policy."}

    # Priority 3: Built-in high-risk patterns (challenge)
    for pattern, warning in HIGH_RISK_PATTERNS:
        if pattern.search(command):
            return {"action": "ask", "risk": "high", "warning": f"CRITICAL: {warning}"}

    # Priority 4: State store references (ask)
    if STATE_STORE_ASK_RE.search(command):
        return {"action": "ask", "risk": "medium", "warning": "Accessing AIGuard state requires approval."}

    # Priority 5: User ask patterns (challenge)
    for pattern in user_policy["ask"]:
        if pattern.search(command):
            return {"action": "ask", "risk": "medium", "warning": "Flagged by user policy."}

    # Priority 6: Metacharacters disqualify auto-allow (challenge)
    if METACHARACTERS.search(command):
        return {"action": "ask", "risk": "medium", "warning": "Command contains shell metacharacters. Manual approval required."}

    # Priority 7: User allow patterns (cannot override anything above)
    for pattern in user_policy["allow"]:
        if pattern.search(command):
            return {"action": "allow", "risk": "low", "warning": ""}

    # Priority 8: Built-in auto-allow (simple commands only)
    cmd_lower = command.lower().strip()
    if any(cmd_lower.startswith(prefix) for prefix in SAFE_PREFIXES):
        return {"action": "allow", "risk": "low", "warning": ""}

    # Priority 9: Default ask (challenge)
    return {"action": "ask", "risk": "medium", "warning": "Unrecognized command. Manual approval required."}
