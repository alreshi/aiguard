# PreToolUse hooks over native instrumentation

AIGuard enforces its Policy exclusively through the Assistants' official PreToolUse Hook mechanisms, routing `ask` Decisions to each Assistant's Native Approval UI. The original design (v5) used Frida to hook process-creation syscalls (`system()`, `CreateProcessW`) and prompted for a 6-digit TOTP inside the hook. This was abandoned after verification against primary sources showed it could not work: hooking `system()` never sees Node/libuv child processes (they use `posix_spawn`, a direct syscall on macOS); SIP and Hardened Runtime block Frida attachment to signed binaries like Claude Code; and both Assistants architecturally prevent interactive prompting inside a Hook — Claude Code (v2.1.132+) runs hooks without a controlling terminal (no `/dev/tty`, stdout invisible), and Kimi's hook protocol honors only `deny`, with a 30-second fail-open timeout.

## Considered Options

- **Frida native hooks with in-hook TOTP prompt (v5/v5.1)** — rejected: catches nothing from Node-based Assistants, blocked by SIP, and interactive prompts inside hooks are impossible on both platforms.
- **OPA/Rego policy engine** — rejected: the assumed Python bindings don't exist as designed, and Rego's complete-rule conflict semantics bit twice; a ~10-rule priority list is a plain Python module with the same decision contract (`{"action", "risk", "warning"}`), leaving OPA migration open.
- **Out-of-band approval daemon (TOTP/Touch ID via desktop notification)** — deferred to v6: the only way strong approval can survive, but heavier than needed for v5.3.

## Consequences

- AIGuard is a Guardrail, not a sandbox: both Assistants fail open on hook timeout/crash, so AIGuard can never be a hard gate. `aiguard-evaluate` itself always fails closed (exit 2 on any internal error).
- In Kimi's yolo/auto modes, an `ask` Decision runs without any user interaction — a documented gap ("do not use Kimi in yolo/auto mode with AIGuard"), accepted because the hook payload cannot reveal the permission mode.
- Absolute Blocks (token-exact targets like `/`, `~`, `$HOME`) are enforced by AIGuard's own Policy and cannot be overridden by the User Policy.
- Aider and Cursor have no PreToolUse hooks and are unsupported until v6.
