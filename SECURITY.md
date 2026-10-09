# Security Policy

> AIGuard is a **Beta release** for evaluation and testing only. See
> [docs/risk-disclosures.md](docs/risk-disclosures.md) for the full risk
> statement.

## Scope

AIGuard is an **Execution-Layer Security (ELS)** tool — it secures the point
where an AI agent's decisions become executed commands. It is a **guardrail**,
not a sandbox. Its threat model is the
honest-but-fallible AI assistant: it adds friction, authentication, and an
audit trail around dangerous shell commands. It does not defend against a
deliberately adversarial agent, and it does not gate file writes or network
access performed without spawning a command.

## Architecture guarantees (and their limits)

- **AIGuard fails closed.** Any internal error in `aiguard-evaluate` blocks
  the command (exit 2).
- **The platforms fail open.** Both Kimi Code CLI and Claude Code allow a
  command when a hook times out or crashes. This is documented platform
  behavior and outside AIGuard's control.
- **Approvals** are single-use, bound to the exact command string
  (SHA-256, truncated to 12 hex chars), and expire after 5 minutes.
- **Absolute Blocks** (`rm -rf /` and equivalents, writes to `~/.aiguard/`)
  cannot be overridden by any approval or user policy.
- **State permissions**: `~/.aiguard/` is 0700; challenge, approval, audit,
  and TOTP files are 0600.
- **TOTP secrets** are stored in the system keyring where available, with a
  0600-file fallback (`~/.aiguard/totp-secret`) on headless systems.
- **Audit log** (`~/.aiguard/audit.jsonl`) records every command VERBATIM.
  Commands may contain secrets; treat the file as sensitive.

## Known limitations

- **Regex-based policy.** Obfuscated, encoded, or novel dangerous commands
  may evade the built-in patterns. The default action for unrecognized
  commands is `ask`, but `SAFE_PREFIXES` auto-allows a small set of common
  prefixes.
- **No protection within an approved command.** A command is approved as a
  whole; what a script or program then does is not constrained.
- **Presence, not judgment.** Touch ID/TOTP confirm an authorized human is
  present; they cannot confirm the human read the command.
- **Notification leakage.** The daemon shows the first 50 characters of a
  challenged command in a desktop notification.
- **Keyring fallback.** On headless systems the TOTP secret lives in a 0600
  file; anyone who can read it can approve commands.
- **Single-user design.** State in `~/.aiguard/` assumes a single user
  account and single-machine use. Shared accounts and multi-machine sync are
  unsupported.
- **Beta quality.** Defects may exist in exactly the components meant to
  protect you. AIGuard must not be your only safeguard; maintain independent
  backups and do not rely on it in yolo/auto-approve assistant modes.

## Reporting a vulnerability

If you find a security issue in AIGuard, please report it **privately** via a
GitHub Security Advisory on this repository rather than a public issue.

Please include: the affected version, platform, assistant (Kimi/Claude) and
its version, steps to reproduce, and whether the issue lets a command bypass
policy evaluation or approval.

## Response timeline

We commit to the following response SLAs for privately reported
vulnerabilities:

| Severity | Initial response | Fix target |
|----------|------------------|------------|
| Critical (policy bypass, approval bypass) | 3 days | 7 days |
| High | 7 days | 30 days |
| Medium | 14 days | 90 days |
| Low | 14 days | 180 days |

If a fix cannot ship within the fix target, we will publish a mitigation note
in the advisory and, where warranted, in `docs/risk-disclosures.md`.

## Supported versions

| Version | Supported |
|---------|-----------|
| 6.1.0bx (Beta) | ✅ latest pre-release only |
| < 6.1   | ❌        |
