# Risk Disclosures and Operational Warnings

**AIGuard is a Beta release, provided for evaluation, testing, and feedback
purposes only.** By installing or using it you accept the following, without
limitation.

## No warranty

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT (see the
[Apache-2.0 License](../LICENSE), sections 7–8). Specifically, no guarantees
are provided regarding:

- **reliability** — the software may contain defects or incomplete features;
- **availability** — the hook, daemon, or approval flow may fail or hang;
- **performance** — evaluation adds latency to every assistant command;
- **suitability for production use** — it is not.

You evaluate and use this software **at your own discretion and risk**.

## AIGuard is a guardrail, not a security boundary

- **Not a sandbox.** AIGuard does not isolate the filesystem, network, or
  memory. An approved (or ungated) command runs with your full privileges.
- **Honest-but-fallible threat model only.** A deliberately adversarial or
  prompt-injected assistant that crafts evasive commands is **out of scope**
  and may bypass the policy engine.
- **Commands only.** File writes and network access performed without
  spawning a shell command are not gated.
- **Pattern matching has blind spots.** The policy is regex-based. Novel or
  obfuscated dangerous commands may be classified `allow` or `ask` instead
  of `block`. Treat `ask` as the normal case, not as an alarm.

## Fail-open platforms

Per Kimi Code CLI and Claude Code documentation, a hook that **times out or
crashes allows the command to run**. AIGuard itself always fails closed, but
the platforms do not. Consequences:

- Do not run an assistant in `yolo`/auto-approve mode and rely on AIGuard as
  your only barrier — platform fail-open behavior can combine with
  auto-approval to bypass everything.
- Keep hook timeouts in mind on slow or heavily loaded machines.

## You are the approval

Every approval is a human security decision:

- **Read the command before approving.** The whole point is that you, not
  the assistant, judge the risk. Approving reflexively defeats the system.
- Approvals are bound to the **exact command string** and are single-use —
  but a command you approve runs with your privileges. One careless approval
  can destroy data.
- Touch ID and TOTP prove *presence*, not *judgment*.

## Data sensitivity

- `~/.aiguard/audit.jsonl` records **every evaluated command verbatim**,
  including any secrets passed as CLI arguments. The file is 0600 — keep it
  that way, handle it as sensitive, and delete it securely when retiring the
  tool.
- On headless systems without a keyring backend, the TOTP secret is stored
  as a 0600 file. Anyone who reads it can approve commands. Prefer keyring
  storage; protect backups of your home directory accordingly.
- Desktop notifications (daemon) display the first 50 characters of the
  challenged command on screen.

## Operational warnings

- **Breaking changes during Beta.** Policy rules, state file formats, and
  CLI behavior may change between pre-releases without a deprecation period.
- **Assistant updates may break hooks.** AIGuard depends on the documented
  PreToolUse mechanisms of Kimi Code CLI and Claude Code; an assistant update
  can silently change hook behavior. Re-verify after upgrading an assistant.
- **Daemon is informational.** If it is not running, you get no
  notifications — check for `AIGUARD_CHALLENGE:` messages from the assistant.
- **Do not weaken `~/.aiguard/` permissions.** The 0700/0600 modes are part
  of the security model.

## If something goes wrong

1. Stop the assistant session.
2. Remove the hooks: `aiguard uninstall kimi` / `aiguard uninstall claude`.
3. Report the problem — security issues privately per
   [SECURITY.md](../SECURITY.md), everything else as a GitHub issue.
