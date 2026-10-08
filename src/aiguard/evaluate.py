"""
Evaluate — the PreToolUse hook target (`aiguard-evaluate`).

Reads the hook payload as JSON on stdin. Exits 0 (allow) or 2 (block/
challenge). Always fails closed: any internal error exits 2.
"""

import json
import sys

from .audit import log_decision
from .crypto import consume_approval, create_challenge, hash_command, prune_expired
from .policy import evaluate_command


def main() -> None:
    try:
        prune_expired()

        stdin_data = sys.stdin.read().strip()
        if not stdin_data:
            sys.exit(2)

        data = json.loads(stdin_data)
        command = data.get("tool_input", {}).get("command", "")
        if not command:
            sys.exit(2)

        decision = evaluate_command(command)
        action = decision["action"]

        # Retry path: an outstanding approval for this exact command is
        # consumed (single-use) and the command proceeds.
        if action == "ask":
            token = hash_command(command)
            if consume_approval(token):
                log_decision(command, {
                    "action": "allow",
                    "risk": decision["risk"],
                    "warning": "Approved via out-of-band challenge",
                })
                sys.exit(0)

        log_decision(command, decision)

        if action == "allow":
            sys.exit(0)
        elif action == "block":
            print(f"AIGuard blocked: {decision['warning']}", file=sys.stderr)
            sys.exit(2)
        elif action == "ask":
            token = create_challenge(command, decision["risk"], decision["warning"])
            print(
                f"AIGUARD_CHALLENGE:{token} | Command blocked pending approval. "
                f"Risk: {decision['risk'].upper()}. "
                f"Please run: aiguard approve {token}",
                file=sys.stderr,
            )
            sys.exit(2)
        else:
            sys.exit(2)
    except SystemExit:
        raise
    except Exception as e:
        print(f"AIGuard internal error — blocking for safety: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
