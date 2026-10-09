# Changelog

All notable changes to AIGuard are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project
uses [Semantic Versioning](https://semver.org/) with PEP 440 pre-release
identifiers (see [docs/releases.md](docs/releases.md)).

## [Unreleased]

### Changed

- PyPI package renamed from `aiguard-cli` to `aiguard-gate`: PyPI rejects
  `aiguard-cli` as too similar to the existing, unrelated `aiguard` project.
  The CLI commands (`aiguard`, `aiguard-evaluate`) are unchanged.
- Positioned the project as an Execution-Layer Security (ELS) tool for AI
  agents across README, SECURITY, architecture docs, and the glossary.

### Security

Found by a Cursor Bugbot full-codebase review; all fixed with regression
tests:

- Absolute Block now catches `rm -Rf`, `rm -r -f` (separated flags), and
  trailing-slash protected targets (`rm -rf ~/`, `rm -rf $HOME/`).
- State-store protection now recognizes `${HOME}/` and the expanded absolute
  home path, not just `~/` and `$HOME/`.
- Safe-prefix auto-allow now requires a word boundary — lookalike commands
  like `lsof` and `direnv` no longer inherit the `ls`/`dir` auto-allow.
- State files (challenges, approvals, audit log, TOTP fallback/lockout) are
  created 0600 atomically instead of written-then-chmod'ed, and `~/.aiguard/`
  is created 0700, closing the umask window.
- Removed accidentally committed browser-automation artifacts
  (`.playwright-mcp/`) from tracking; now gitignored.

Two Bugbot findings were verified false positives against the official Kimi
Code docs: the hook config path `~/.kimi-code/config.toml` and the
`PreToolUse` matcher `"Bash"` are both correct as implemented.

## [6.1.0b1] - 2026-10-08

First **Beta** pre-release. Intended for evaluation, testing, and feedback
only — see [docs/risk-disclosures.md](docs/risk-disclosures.md).

### Added

- Out-of-band challenge-response approval: `ask` decisions emit an
  `AIGUARD_CHALLENGE:<token>` and block until approved via `aiguard approve`.
- Touch ID approval on macOS (PyObjC LocalAuthentication), TOTP
  (RFC 6238, 6-digit) on Linux and as fallback, with failed-attempt lockout.
- Single-use approvals bound to the exact command string (SHA-256[:12]),
  5-minute expiry, opportunistic garbage collection.
- Absolute Blocks for filesystem-destroying commands and any write to the
  `~/.aiguard/` state store; not overridable by approvals or user policy.
- User policy file (`~/.aiguard/policy.toml`) with allow/ask/block regex
  rules.
- Verbatim append-only audit log (`~/.aiguard/audit.jsonl`, 0600).
- PreToolUse hook installers for Kimi Code CLI and Claude Code.
- Optional notification daemon (macOS LaunchAgent / Linux `notify-send`),
  injection-safe argv-based notifications.
- Full documentation set: architecture, installation, contributing, security
  policy, risk disclosures, release strategy, ADRs, and glossary.

### Changed

- Repository reorganized to standard src layout (`src/aiguard/`).
- `aiguard --version` now reports the package `__version__`.
