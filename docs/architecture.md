# Architecture Overview

AIGuard is an **Execution-Layer Security (ELS)** tool for AI agents: it
operates at the execution layer, where an agent's decisions turn into real
processes on the host — independent of the model, prompt, or agent framework
that produced them.

## Repository structure

```text
AIGuard/
├── src/aiguard/              # Python package (src layout)
│   ├── __init__.py           # Package version
│   ├── cli.py                # `aiguard` command group (click)
│   ├── evaluate.py           # `aiguard-evaluate` — the PreToolUse hook target
│   ├── policy.py             # Policy engine: command → Decision
│   ├── crypto.py             # Challenge/approval state, tokens, GC
│   ├── approve.py            # `aiguard approve` — out-of-band approval
│   ├── totp.py               # RFC 6238 TOTP enrollment and verification
│   ├── audit.py              # Append-only audit log
│   ├── daemon.py             # Optional notification watcher
│   └── hooks/                # Per-assistant hook installers
│       ├── base.py           # HookInstaller interface
│       ├── kimi.py           # Kimi Code CLI integration
│       └── claude.py         # Claude Code integration
├── tests/
│   └── test_aiguard.py       # Hermetic pytest suite (isolated HOME)
├── docs/
│   ├── architecture.md       # This file
│   ├── installation.md       # Installation and setup
│   ├── releases.md           # Release and versioning strategy
│   ├── risk-disclosures.md   # Risk disclosures and operational warnings
│   ├── design/               # Design documents
│   └── adr/                  # Architecture Decision Records
├── README.md                 # Project overview and quick start
├── CONTRIBUTING.md           # Development workflow and contribution rules
├── SECURITY.md               # Security policy and known limitations
├── CHANGELOG.md              # Release history
├── GLOSSARY.md               # Domain vocabulary
├── LICENSE                   # Apache-2.0
└── pyproject.toml            # Build metadata (hatchling)
```

## System architecture

AIGuard is a local, file-based system with no network component. All state
lives in `~/.aiguard/` (0700), with individual state files at 0600.

```text
┌─────────────────┐   PreToolUse hook (JSON on stdin)
│  AI Assistant   │──────────────────────────────┐
│ (Kimi / Claude) │                              ▼
└─────────────────┘                    ┌───────────────────┐
        ▲                              │ aiguard-evaluate  │
        │ exit 0: run                  │  (evaluate.py)    │
        │ exit 2: blocked,             └─────────┬─────────┘
        │   relay challenge token                │ Decision
        ▼                                        ▼
┌─────────────────┐                    ┌───────────────────┐
│  User terminal  │  approve <token>   │    policy.py      │
│ aiguard approve │───────────────────▶│ allow / ask /     │
└─────────────────┘                    │ block (+ risk,    │
        │ Touch ID (macOS)             │ warning)          │
        │ or TOTP (Linux/fallback)     └───────────────────┘
        ▼                                        │
┌─────────────────┐   ~/.aiguard/                ▼
│  approve.py     │──────────────▶ challenges/  approvals/  audit.jsonl
└─────────────────┘                              ▲
        ▲                                        │ watches
        │ notification                 ┌─────────┴─────────┐
        └──────────────────────────────│ daemon.py         │
                                       └───────────────────┘
```

### Evaluation flow (`evaluate.py`)

1. Prune expired challenges/approvals (opportunistic GC).
2. Parse the hook payload (`tool_input.command`) from stdin.
3. `policy.evaluate_command()` returns a Decision
   (`{"action", "risk", "warning"}`).
4. `allow` → audit, exit 0. `block` → audit, exit 2 with the warning.
5. `ask` → if a matching approval exists for the exact command hash, consume
   it (single-use), audit, exit 0. Otherwise create a challenge file, audit,
   exit 2 with `AIGUARD_CHALLENGE:<token>` on stderr.
6. Any internal error → exit 2 (fail closed).

### Policy engine (`policy.py`)

Ordered evaluation, first match wins:

1. **Absolute Block** — recursive+force delete of protected targets
   (`/`, `~`, `$HOME`, …) and any write/delete/cp/mv/ln into `~/.aiguard/`.
   Cannot be overridden by anything.
2. **User Policy** (`~/.aiguard/policy.toml`) — user `block`, `ask`, `allow`
   regex patterns.
3. **Built-in high-risk patterns** — `curl|bash`, `sudo`, `dd of=/dev/`,
   `mkfs.*`, `chmod 777`, `git push --force`, `git reset --hard`, etc. → `ask`.
4. **Shell metacharacters** (`;|&<>`$()` and newlines) → `ask`.
5. **Safe prefixes** (`ls`, `pwd`, `git status`, `cat `, …) → `allow`.
6. **Default** → `ask`.

Risk tiers (`low`/`medium`/`high`/`critical`) are informational and never
change the action on their own.

### Approval flow (`approve.py`, `crypto.py`)

- A challenge token is `sha256(command)[:12]` — deterministic per exact
  command string, so any edit to the command requires re-approval.
- Approval authenticates the user (Touch ID on macOS via PyObjC
  LocalAuthentication; TOTP elsewhere or with `--totp`), moves the challenge
  file from `challenges/` to `approved/`, and stamps `expires_at = now + 300`.
- On retry, `evaluate.py` consumes the approval file (single-use). Approvals
  expire after 5 minutes; unapproved challenges are pruned after 1 hour.

### TOTP (`totp.py`)

RFC 6238, SHA-1, 6 digits, 30-second period, verification window ±1 step.
Secrets are stored in the system keyring via `keyring`, falling back to a
0600 file (`~/.aiguard/totp-secret`) on headless systems. Three failed
verification attempts trigger a 5-minute lockout.

### Daemon (`daemon.py`)

Optional. Polls `~/.aiguard/challenges/` every 2 seconds and raises a desktop
notification (osascript on macOS — argv-passed, injection-safe; `notify-send`
on Linux). Informational only: approval works without it. Installed as a
macOS LaunchAgent via `aiguard daemon-install`.

### Hook installers (`hooks/`)

Each assistant implements the `HookInstaller` interface
(`is_installed`, `install_hook`, `uninstall_hook`) to register
`aiguard-evaluate` in the assistant's own PreToolUse configuration.

## Design decisions

Significant decisions are recorded as ADRs in [docs/adr/](adr/):

- [0001 — PreToolUse hooks over native instrumentation](adr/0001-pretooluse-hooks-over-native-instrumentation.md)
- [0002 — Out-of-band challenge-response](adr/0002-out-of-band-challenge-response.md)

The full original design document is in
[docs/design/out-of-band-approval.md](design/out-of-band-approval.md).

## Terminology

Code and documentation use the vocabulary defined in
[GLOSSARY.md](../GLOSSARY.md) — e.g. *Decision*, *Action*, *Absolute Block*,
*Challenge*, *Approval*, *Fail-Open*.
