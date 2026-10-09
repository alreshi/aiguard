# AIGuard public website

Static site for [AIGuard](https://github.com/alreshi/aiguard). No build step,
no dependencies, no trackers — plain HTML, one CSS file, one deferred
vanilla-JS file (~6 KB). See [DESIGN.md](DESIGN.md) for the design rationale.

## Structure

```
site/
├── index.html            # Landing
├── security.html         # Security & trust (threat model, reporting)
├── 404.html
├── docs/                 # Docs layout (sidebar, admonitions, tables)
│   ├── index.html        #   Overview
│   ├── installation.html
│   ├── architecture.html
│   ├── releases.html
│   ├── risk-disclosures.html
│   ├── security.html
│   └── contributing.html
├── css/site.css          # Design tokens + all components (dark default, light theme)
├── js/main.js            # Theme toggle, copy buttons, terminal demo, docs nav
├── assets/               # favicon.svg, og-image.svg (placeholder — see TODOs)
└── DESIGN.md             # One-page design rationale
```

## Serve locally

Any static server works; there is nothing to compile:

```bash
cd site
python3 -m http.server 8000
# → http://localhost:8000
```

Every page also opens directly from `file://` (all paths are relative,
the JS degrades gracefully when `navigator.clipboard` is unavailable).

## Deploy to Cloudflare Pages

The site is deployed by **Cloudflare Pages** via Git integration and served
at `https://aiguard-gate.dev` (the URL used in the canonical / OG meta tags).

- **Production branch:** `main` — every push auto-deploys; pull requests get
  preview deployments.
- **Build settings:** framework preset *None*, no build command, output
  directory `site`.
- **Custom domain:** `aiguard-gate.dev` is attached in the Pages project;
  DNS is managed automatically because the zone lives on Cloudflare.

There is no deploy workflow in this repository — Cloudflare builds on push.
Do not reintroduce a GitHub Pages deploy for `site/`; the canonical public
URL is the custom domain only.

## Editing conventions

- Header, footer, beta banner, and docs sidebar markup are duplicated across
  HTML files by design (no build step). If you change chrome, change it in
  every file. Shared behavior lives in `css/site.css` and `js/main.js` only.
- Content claims must match the repository's `README.md`, `SECURITY.md`,
  `GLOSSARY.md`, and `docs/risk-disclosures.md`. AIGuard is a **guardrail** —
  never write copy that implies it makes agents safe.
- Keep total JS under 50 KB and add no CDN/runtime dependencies.

## Known placeholders (TODO in markup)

- `assets/og-image.png` — real 1200×630 social card to replace the SVG
  placeholder; update the `og:image` / `twitter:image` meta tags when it lands.
- The hero terminal transcript is illustrative (labeled as such) — swap in a
  captured real session if desired.
