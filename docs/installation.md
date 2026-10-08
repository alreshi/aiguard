# Installation and Setup

> **Beta software** — for evaluation and testing only. Read
> [risk-disclosures.md](risk-disclosures.md) before installing.

## Requirements

| Platform | Support | Authentication |
|----------|---------|----------------|
| macOS (Apple Silicon / Intel) | Primary | Touch ID via PyObjC LocalAuthentication |
| Linux | Secondary | TOTP (any RFC 6238 authenticator app) |

- Python **3.11 or newer**
- One of the supported assistants: **Kimi Code CLI** or **Claude Code**
- [pipx](https://pipx.pypa.io/) (recommended) or pip

## Install

```bash
pipx install aiguard-cli
```

### macOS: Touch ID support

```bash
pipx inject aiguard-cli pyobjc-framework-LocalAuthentication
```

Without this package, approvals on macOS fall back to TOTP.

## Setup

### 1. Enroll TOTP

```bash
aiguard setup
```

This prints a provisioning URI and a base32 secret. Add it to your
authenticator app, then enter the current 6-digit code to confirm. The secret
is stored in the system keyring, or — on headless systems without a keyring
backend — in `~/.aiguard/totp-secret` (0600) with a warning.

TOTP is **required on Linux** and serves as the **fallback on macOS** when
Touch ID is unavailable.

### 2. Install the assistant hook

```bash
aiguard install kimi     # Kimi Code CLI
aiguard install claude   # Claude Code
```

This registers `aiguard-evaluate` as a PreToolUse hook in the assistant's own
configuration. To remove it: `aiguard uninstall kimi` (or `claude`).

### 3. Optional: desktop notifications

```bash
aiguard daemon-install   # macOS LaunchAgent
```

The daemon watches for new challenges and raises a desktop notification so you
notice approval requests immediately. It is informational only — approval
works without it.

## Verify the installation

```bash
aiguard --version        # 6.1.0b1
echo '{"tool_input": {"command": "ls"}}' | aiguard-evaluate; echo "exit=$?"
# exit=0 (allowed)

echo '{"tool_input": {"command": "sudo rm -rf /var/tmp/x"}}' | aiguard-evaluate; echo "exit=$?"
# exit=2, stderr contains AIGUARD_CHALLENGE:<token>
```

## Custom policy (optional)

Create `~/.aiguard/policy.toml`:

```toml
block = ["npm publish", "kubectl delete"]
ask = ["^docker "]
allow = ["^make test$"]
```

User rules are regular expressions matched against the full command string.
User `allow` rules can never override a built-in Absolute Block.

## Upgrading

```bash
pipx upgrade aiguard-cli
```

State in `~/.aiguard/` (TOTP secret, policy, audit log) is preserved across
upgrades. Hooks may need reinstalling if the hook format changes between
versions — check the [CHANGELOG](../CHANGELOG.md).

## Uninstalling

```bash
aiguard uninstall kimi      # remove hooks (repeat for claude if installed)
pipx uninstall aiguard-cli
rm -rf ~/.aiguard           # optional: removes TOTP secret, policy, audit log
```

> ⚠️ `~/.aiguard/audit.jsonl` may contain commands with secrets. Delete it
> securely if that is a concern.

## Development install

See [CONTRIBUTING.md](../CONTRIBUTING.md).
