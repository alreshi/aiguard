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

## Deploy to GitHub Pages

GitHub Pages' "deploy from branch" option only serves `/` or `/docs`, so
publishing this `site/` folder needs a tiny Actions workflow (no secrets —
`GITHUB_TOKEN` only). The workflow lives at
[../.github/workflows/site.yml](../.github/workflows/site.yml):

```yaml
name: Deploy site

on:
  push:
    branches: [main]
    paths: ['site/**']
  workflow_dispatch:

permissions:
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site
      - id: deployment
        uses: actions/deploy-pages@v4
```

Then: repo **Settings → Pages → Source: GitHub Actions**. The site lands at
`https://alreshi.github.io/aiguard/` (the URL already used in the canonical /
OG meta tags). Note: the deploy job fails until Pages is enabled — enable it
before pushing, or re-run the failed workflow afterwards.

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
