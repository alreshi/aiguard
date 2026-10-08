# AIGuard public site — design rationale

One page. Decisions first, tokens second.

## Stack decision

**Plain HTML/CSS/vanilla JS, no build step, no generator.**
Justification: the site is three page types (landing, docs, security) with
near-identical chrome; a generator would add a toolchain (and CI secrets
risk) to save duplicating ~40 lines of header/footer per page. No-build
means GitHub Pages can serve the folder as-is, `file://` review works
offline, and the JS budget (<50 KB) is met trivially (~7 KB gzipped total,
one file, deferred). Trade-off accepted and documented: header/footer/sidebar
markup is duplicated across pages — any chrome edit must be applied to all
HTML files (they share one CSS and one JS file, so behavior stays in sync).

## Layout system

- 8 pt spacing grid: `--sp-1..12` = 4, 8, 16, 24, 32, 40, 48, 64, 80, 96 px.
- Max content width 1120 px; prose column 68 ch; docs sidebar 260 px,
  collapses to a toggle button below 900 px.
- Landing: banner → header → hero (copy left, terminal right; stacks on
  mobile) → 4-step row → decision trio → feature grid → "does NOT do"
  → install → footer.
- All pages share: persistent Beta banner, header, footer. First paint is
  dark; theme is set by a 200-byte inline script before CSS to avoid flash.

## Component inventory

| Component | Purpose |
|---|---|
| Beta banner | Persistent, every page, links to risk disclosures |
| Header/nav | Wordmark + shield mark, Docs / Security / GitHub, theme toggle |
| Terminal | The hero artifact. HTML/CSS/JS transcript of allow → ask → approve → retry → block. Real text, selectable, replayable; static under `prefers-reduced-motion` or no-JS |
| Decision cards | allow / ask / block with semantic colors |
| Step cards | How-it-works, numbered 1–4 |
| Feature cards | 6-up grid |
| Limits list | "What AIGuard does NOT do" — visually prominent, not buried |
| Code block + copy | Install/setup commands; clipboard API with `execCommand` fallback (works on `file://`) |
| Docs sidebar | Left nav, `aria-current`, mobile toggle |
| Admonitions | note / warning / danger |
| Badge | Action (allow/ask/block) and Risk Tier (low/medium/high/critical) |
| Heading anchors | Auto-appended by JS in docs content |

## Color tokens

Dark is the default; light is a full secondary theme (`data-theme="light"`).

| Token | Dark | Light | Use |
|---|---|---|---|
| `--bg` | `#0c1116` | `#fbfcfd` | page |
| `--surface` | `#151e27` | `#ffffff` | cards, code |
| `--border` | `#26313d` | `#d9e2e9` | hairlines |
| `--text` | `#e3ebf2` | `#16202a` | body |
| `--text-muted` | `#93a3b1` | `#4c5c6b` | secondary (≥4.5:1 both themes) |
| `--primary` | `#34d0a4` | `#0c7a5e` | shield/brand, links, focus |
| `--safe` | `#4ade80` | `#0f7a3d` | allow, risk low |
| `--caution` | `#f5b942` | `#9a6200` | ask, risk medium |
| `--high` | `#fb923c` | `#b45309` | risk high |
| `--refused` | `#f26d6d` | `#c22430` | block, risk critical, danger admonition |

Semantic colors are reserved for verdicts/risk — the brand itself stays
teal/emerald so "block red" never reads as brand aggression. All body-text
pairs meet WCAG 2.1 AA (≥4.5:1); muted text was chosen against both
backgrounds to keep Accessibility at 100.

## Typography

- Prose/UI: system stack (`-apple-system, "Segoe UI", Roboto, …`) — zero
  webfont downloads, nothing render-blocking.
- Code/terminal: `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`.
- Scale (1.25): 12 / 14 / 16–17 / 20 / 24 / 32 / clamp(32→44) hero.
- Terminal body 13–14 px, line-height 1.6 for scanability.

## Motion

Subtle only: 150 ms ease color/opacity transitions, terminal typing effect.
`prefers-reduced-motion: reduce` kills all animation (CSS `!important` sweep
+ JS renders the full transcript instantly). Demo starts on scroll-into-view,
never loops unprompted; replay is a user action.

## Voice

Concise, factual, second person only in instructions. No "blazingly", no
"secure your agents" — the strongest claim allowed is "guardrail". The
limitations section is a peer of the feature grid, not a footnote.

## Known placeholders (TODO in markup)

- `og:image` — SVG placeholder shipped; real 1200×630 PNG of the shield
  mark to drop in at `site/assets/og-image.png` before launch.
- Terminal demo transcript is illustrative (labeled as such); swap in a
  captured real session if desired.
- Docs pages are seeded summaries; long-form content ports from `docs/*.md`.
