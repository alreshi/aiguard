# Out-of-band challenge-response approval

AIGuard approves dangerous Commands out-of-band: an `ask` Decision blocks the Command (exit 2) and issues a Challenge token (SHA-256 of the exact Command string, truncated to 12 hex chars); the user approves it in a separate terminal via `aiguard approve <token>` (Touch ID on macOS, TOTP on Linux); the Assistant retries and the single-use Approval is consumed. Interactive approval inside the Hook is architecturally impossible (Claude Code hooks have no controlling terminal; Kimi honors only `deny`), and assistant-native approval UIs are absent in yolo/auto modes — so approval had to move out of the Hook entirely.

## Considered Options

- **Native approval only (v5.3)** — kept as the fallback behavior but insufficient alone: no user interaction at all in Kimi yolo/auto modes.
- **Clickable desktop notifications (e.g. terminal-notifier)** — rejected for v6.1: the notification is informational only; the Touch ID/TOTP prompt is the real approval dialog. osascript notifications cannot be actionable.
- **`security authorize` for Touch ID** — rejected: verified broken for this purpose (`-p` is "partial rights", requires a pre-registered authorization right); PyObjC LocalAuthentication with a `threading.Event`-bridged reply block is the working path.

## Consequences

- Approvals are single-use and expire after 5 minutes; any change to the Command string requires a new Challenge (bait-and-switch protection).
- Absolute Blocks issue no Challenge — they remain final.
- `~/.aiguard/` is policy-protected: Commands referencing it are at least ask-tier; write/delete attempts are Absolute Blocks.
- The TOTP secret lives in the system keyring with a 0600-file fallback on headless Linux; TOTP failures lock out after 3 attempts for 5 minutes (on-disk counter).
- The Daemon is optional and purely informational; approval works without it.
