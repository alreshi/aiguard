# 🛡️ AIGuard

> **⚠️ BETA RELEASE — v6.1.0b1**
> AIGuard is currently a **Beta release intended for evaluation, testing, and
> feedback purposes only**. It may contain defects, incomplete features,
> security vulnerabilities, or operational limitations. **No guarantees are
> provided regarding reliability, availability, performance, or suitability
> for production use.** Evaluate and use this software **at your own
> discretion and risk**. See [Risk Disclosures](docs/risk-disclosures.md).

Out-of-band command approval for AI coding assistants. AIGuard intercepts the
shell commands an assistant tries to run, evaluates them against a policy, and
gates dangerous ones behind real, platform-native human authentication.

**AIGuard is an Execution-Layer Security (ELS) tool for AI agents.** ELS
secures the layer where an agent's decisions become real actions — process
and command execution on your machine. It complements model-level and
prompt-level defenses, which cannot prevent a compromised or fallible agent
from *executing* something dangerous.

- **macOS**: Touch ID (via PyObjC LocalAuthentication)
- **Linux**: 6-digit TOTP (RFC 6238, works with any authenticator app)

Supported assistants: **Kimi Code CLI** and **Claude Code** (via their official
PreToolUse hook mechanisms).

## Quick start

```bash
pipx install aiguard-gate

# macOS Touch ID support:
pipx inject aiguard-gate pyobjc-framework-LocalAuthentication
```

```bash
aiguard setup            # TOTP enrollment (required on Linux, fallback on macOS)
aiguard install kimi     # or: aiguard install claude
aiguard daemon-install   # optional: desktop notifications (macOS LaunchAgent)
```

Full instructions: [docs/installation.md](docs/installation.md).

## How it works

1. The assistant tries to run a command. Its PreToolUse hook calls
   `aiguard-evaluate` with the command as JSON on stdin.
2. AIGuard's policy returns a **Decision**:
   - `allow` — safe commands (`git status`, `ls`, …) proceed instantly.
   - `block` — catastrophic commands (`rm -rf /`, writes to `~/.aiguard/`)
     are refused. **No override exists.**
   - `ask` — everything else is blocked with a challenge token:
     `AIGUARD_CHALLENGE:<token>`.
3. The assistant relays the token to you. You run, in any terminal:

   ```bash
   aiguard approve <token>          # Touch ID on macOS
   aiguard approve --totp <token>   # force TOTP
   ```

4. You tell the assistant to retry. The approval is **single-use**, bound to
   the **exact command string**, and expires after **5 minutes**.

## Custom policy

Add your own rules to `~/.aiguard/policy.toml`:

```toml
block = ["npm publish", "kubectl delete"]
ask = ["^docker "]
allow = ["^make test$"]
```

User `allow` rules can never override a built-in Absolute Block.

## Documentation

| Document | Contents |
|----------|----------|
| [docs/architecture.md](docs/architecture.md) | Repository structure and architecture overview |
| [docs/installation.md](docs/installation.md) | Installation and setup instructions |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development workflow and contribution guidelines |
| [SECURITY.md](SECURITY.md) | Security policy, considerations, and known limitations |
| [docs/risk-disclosures.md](docs/risk-disclosures.md) | Risk disclosures and operational warnings |
| [docs/releases.md](docs/releases.md) | Release and versioning strategy |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
| [GLOSSARY.md](GLOSSARY.md) | Domain vocabulary used across code and docs |
| [docs/design/out-of-band-approval.md](docs/design/out-of-band-approval.md) | Original design document |
| [docs/adr/](docs/adr/) | Architecture Decision Records |

## What AIGuard does NOT do

- **Not a sandbox.** It does not isolate filesystem, network, or memory.
- **Not adversarial-proof.** It is a guardrail against honest-but-fallible
  agents. A deliberately evasive agent is out of scope (see `GLOSSARY.md`).
- **Does not gate file writes or network access** — only spawned commands.
- **Fail-open platforms.** Per Kimi/Claude docs, a hook *timeout or crash*
  allows the command (AIGuard itself always fails closed). Do not use Kimi in
  yolo/auto mode if you rely on AIGuard. AIGuard should not be your sole
  security barrier.
- **The audit log is verbatim.** `~/.aiguard/audit.jsonl` (0600) records every
  command, which may include secrets passed as CLI arguments.

## Disclaimer

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND. AIGuard is a
Beta release: it may fail to block dangerous commands, may block legitimate
work, and may behave incorrectly on untested platforms or assistant versions.
It is a defense-in-depth guardrail, **not** a security boundary. You are
responsible for reviewing every command you approve and for maintaining
independent backups and safeguards. See
[docs/risk-disclosures.md](docs/risk-disclosures.md) and the
[Apache-2.0 License](LICENSE).

## Development

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e '.[dev]'
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

## License

[Apache-2.0](LICENSE)
