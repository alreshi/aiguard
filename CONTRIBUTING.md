# Contributing to AIGuard

> AIGuard is currently a **public Beta** — see the risk statement in
> [README.md](README.md). The workflow below applies to all contributions.

## Development setup

Requires Python 3.11+.

```bash
git clone https://github.com/alreshi/aiguard.git
cd aiguard
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
```

On macOS, for Touch ID code paths:

```bash
pip install -e '.[dev,macos]'
```

## Running tests

```bash
pytest
```

The suite is hermetic: every test runs against an isolated `Path.home()`
(via `tmp_path`), so tests never touch your real `~/.aiguard/` or keyring.
Preserve this property — new tests that touch global state must isolate it
the same way.

Useful smoke check for the hook entry point:

```bash
echo '{"tool_input": {"command": "git status"}}' | aiguard-evaluate; echo $?
```

## Project layout

See [docs/architecture.md](docs/architecture.md). Source lives in
`src/aiguard/` (src layout); tests in `tests/`.

## Workflow

1. **Branch** from `main`: `git checkout -b feat/short-description`
   (or `fix/…`, `docs/…`).
2. **Make the change.** Keep commits small and focused.
3. **Run the tests.** All tests must pass before opening a PR.
4. **Update docs** in the same commit when behavior changes: README,
   `docs/`, `CHANGELOG.md` (under *Unreleased*), and `GLOSSARY.md` if you
   introduce or repurpose a domain term.
5. **Open a pull request** against `main`. Describe *what* and *why*, and
   note any security implications explicitly.

## Rules that protect the security model

AIGuard is a guardrail; these invariants are load-bearing. Do not weaken them
without an ADR ([docs/adr/](docs/adr/)) and maintainer sign-off:

- **Fail closed.** `aiguard-evaluate` must exit 2 on any internal error.
- **Absolute Blocks are absolute.** No approval and no user policy may
  override them.
- **Approvals stay single-use** and bound to the exact command string.
- **State permissions.** Everything under `~/.aiguard/` stays 0700/0600.
- **No injection.** Never interpolate command text into AppleScript, shell
  strings, or notification commands — pass it as argv (see `daemon.py`).
- **The daemon must never crash** (broad `except` is intentional there —
  and only there).

## Style and vocabulary

- Match the surrounding code: standard library first, explicit error
  handling, no unnecessary dependencies. New runtime dependencies need
  justification in the PR and are governed by
  [docs/dependency-management.md](docs/dependency-management.md).
- Use the domain vocabulary in [GLOSSARY.md](GLOSSARY.md) (*Decision*,
  *Action*, *Challenge*, *Approval*, …) in code, comments, and docs. Avoid
  the terms the glossary marks as deprecated.
- Comments should explain *why*, not restate *what*.

## Commit and PR conventions

- Commit messages: imperative mood, e.g. `Add lockout after failed TOTP
  attempts`. Reference issues/ADRs where relevant.
- PRs must pass `pytest` and include doc updates for behavior changes.
- Releases are cut by the maintainer only — see
  [docs/releases.md](docs/releases.md).

## Reporting security issues

Do **not** open a public issue. See [SECURITY.md](SECURITY.md).
