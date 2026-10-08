# AIGuard

AIGuard is a guardrail for AI coding assistants: it evaluates the shell commands an assistant tries to run and returns a verdict — allow, route to the assistant's own approval UI, or block. It protects against honest-but-fallible agents, not adversarial ones.

## Language

**Execution-Layer Security (ELS)**:
The discipline of securing the layer where an AI agent's decisions become real actions — process and Command execution on the host — as opposed to model-level or prompt-level defenses. AIGuard is an ELS tool: it gates execution regardless of how the Command was generated.

**Assistant**:
A supported AI coding CLI that AIGuard integrates with (Kimi Code CLI, Claude Code).
_Avoid_: agent, AI tool, LLM

**Command**:
A single shell command string an Assistant attempts to execute via its shell tool (e.g. the `Bash` tool).

**Policy**:
The ordered rule set that maps a Command to a Decision. First match wins: block rules, then ask rules, then allow rules, with a default of ask.

**Decision**:
The Policy's verdict for a Command: an Action, a Risk Tier, and a human-readable Warning. The decision contract is `{"action", "risk", "warning"}`.

**Action**:
The outcome of a Decision: `allow` (run without prompting), `ask` (route to Native Approval), or `block` (refuse, reason returned to the Assistant).
_Avoid_: verdict, result

**Risk Tier**:
The severity classification of a Command: `low`, `medium`, `high`, or `critical`. Informational; it never changes the Action on its own.
_Avoid_: risk level, severity

**Warning**:
The plain-English explanation of what a Command does, shown to the user or returned to the Assistant.
_Avoid_: message, reason

**Hook**:
The Assistant's official PreToolUse integration point: a command the Assistant runs before executing a tool call, receiving the Command as JSON on stdin.
_Avoid_: interceptor, plugin

**Native Approval**:
The Assistant's own built-in approval UI (e.g. a y/n prompt). AIGuard routes `ask` Decisions here rather than prompting inside the Hook.
_Avoid_: approval prompt, confirmation dialog

**Fail-Open**:
The documented behavior of both Assistants: if a Hook errors or times out, the Command proceeds. AIGuard cannot be a hard gate.
_Avoid_: fail-safe (ambiguous — v5 used it to mean fail-closed)

**Guardrail**:
AIGuard's threat model: friction and audit against an honest-but-fallible Assistant. Adversarial evasion is explicitly out of scope.
_Avoid_: sandbox, containment

**Absolute Block**:
A Decision (`block` / `critical`) that no approval and no User Policy can override. Reserved for filesystem-destroying Commands (e.g. recursive delete of `/`).
_Avoid_: hard block, permanent ban

**User Policy**:
The user's own allow/ask/block patterns, layered over the built-in Policy. It can add restrictions and widen auto-allow, but cannot override an Absolute Block.
_Avoid_: custom rules, overrides

**Audit Log**:
The append-only record of every Command evaluated and its Decision.
_Avoid_: log file, history

**Out-of-Band Approval**:
The approval channel outside the Hook: a pending Challenge is created on block, the user approves it via a separate local command (Touch ID on macOS, TOTP on Linux), and the Assistant retries the exact Command.
_Avoid_: TOTP prompt, inline approval

**Challenge**:
The pending state of a blocked Command awaiting Out-of-Band Approval, identified by a token derived from the exact Command string. Approving a Challenge grants one Approval.
_Avoid_: ticket, request

**Approval**:
The grant that lets one specific Command (matched by token) proceed. Short-lived and single-use; any change to the Command string requires a new Challenge.
_Avoid_: permit, allowlist entry

**Daemon**:
The optional background process that watches for new Challenges and raises desktop notifications. If it is not running, approval still works — the user approves manually.
_Avoid_: service, watcher
