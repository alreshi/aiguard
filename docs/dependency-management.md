# Dependency Management and Review Policy

AIGuard is a security tool. Its dependency tree is part of its attack
surface, so dependency changes are treated as code changes: reviewed by a
human, gated by CI, and never merged automatically.

## Scope

This policy covers:

- **Runtime dependencies** — `[project] dependencies` and
  `[project.optional-dependencies]` in `pyproject.toml`.
- **Development dependencies** — the `dev` extra (pytest, ruff, pip-audit).
- **CI/CD dependencies** — GitHub Actions referenced in
  `.github/workflows/`.

## Sources of updates

| Source | Cadence | What it covers |
|--------|---------|----------------|
| Dependabot (`.github/dependabot.yml`) | Weekly | pip (all extras), GitHub Actions (grouped into one PR) |
| pip-audit | Every CI run and every release | Known CVEs in the installed tree; **blocks CI and releases** |
| Dependency Review action | Every PR | New dependencies introduced by a PR; fails on HIGH+ severity |
| Manual review | Ad hoc | Maintainer-initiated upgrades |

## Pinning policy

- **Runtime dependencies** use lower-bound ranges (`click>=8.1.0`). AIGuard
  is a library-like CLI installed via pipx; exact pins would conflict with
  user environments. Lower bounds exist to guarantee required APIs.
- **GitHub Actions** are pinned to a full-length commit SHA with a version
  comment (`# vX.Y.Z`). Moving tags (`@v4`, `@main`) are not permitted for
  third-party actions. Dependabot proposes SHA bumps; the version comment
  must be updated in the same PR.
- **No lockfile** is shipped; reproducibility for releases is provided by
  SLSA provenance and the SBOM instead (see below).

## Review process for dependency PRs

Dependency PRs are **never auto-merged**. For each Dependabot or manual
dependency PR, the maintainer MUST:

1. **Wait for full CI**: tests (Ubuntu + macOS, Python 3.11–3.13), ruff,
   pip-audit, and the Dependency Review check must all pass. A green build
   is necessary but not sufficient.
2. **Read the upstream changelog / release notes** for every bumped
   package or action. For actions, diff the tag between the old and new
   SHA if the release notes are thin.
3. **Check for red flags**: new maintainers, ownership transfer, sudden
   scope expansion (new network calls, new permissions requested by an
   action), or a release published within the last 48 hours (aged releases
   have had time for the community to catch compromised versions).
4. **Verify the blast radius**: a change to `pyotp`, `keyring`, or
   `click` touches authentication and CLI paths — smoke-test
   `aiguard setup` / `aiguard approve` locally before merging. A GitHub
   Actions bump in `release.yml` must be rehearsed via the TestPyPI path
   before the next real release.
5. **Approve and merge** with a merge commit or squash; the Dependabot
   metadata (`Dependabot: ...` trailer) stays intact for traceability.

Only the maintainer merges dependency PRs. During Beta there is no
delegation.

## Security updates (fast track)

When pip-audit, a GitHub Security Advisory, or Dependabot's security
stream reports a **known-exploited or high/critical** vulnerability in the
dependency tree:

| Severity of the CVE | Target to merge the fix |
|---------------------|--------------------------|
| Critical / known-exploited | 7 days (aligned with SECURITY.md SLA) |
| High | 30 days |

Fast-track PRs still run full CI and get changelog review, but skip the
48-hour aging rule — the risk of the known CVE outweighs the risk of a
young release. If the CVE is in AIGuard's **runtime** path (any of the
four runtime deps), a PATCH release follows the merge immediately, per
[docs/releases.md](releases.md).

## Testing requirements

- Every dependency PR must pass the full CI matrix unchanged — no test
  exemptions for dependency updates.
- If a dependency bump changes behavior (deprecation warnings, output
  format changes), the PR author updates tests and docs in the same PR,
  per [CONTRIBUTING.md](../CONTRIBUTING.md).
- Release-blocking: `pip-audit` runs in `release.yml`; a release cannot
  ship with a known-vulnerable dependency tree.

## Release and verification

Every release publishes the evidence needed to audit the dependency tree:

- **SLSA build provenance** — attestations for the sdist and wheel,
  verifiable with
  `gh attestation verify <artifact> --repo alreshi/aiguard`.
- **SBOM** (`sbom.spdx.json`) attached to the GitHub Release — the exact
  dependency inventory of that release.

Consumers and reviewers should verify both before deploying a new version.
See the *Verifying a release* section of [docs/releases.md](releases.md).

## Exceptions

Any deviation from this policy (e.g., temporarily ignoring a pip-audit
finding with `--ignore-vuln`) requires:

1. A written justification in the commit message and CHANGELOG,
2. An expiry date or upstream-issue link for the exception,
3. A follow-up issue to remove the exception.

Exceptions are time-boxed; an expired exception fails the next review.
