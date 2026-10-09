# Release and Versioning Strategy

## Status: public Beta

The repository is **public** and the current release line is **Beta**.
Releases follow the process below; all supply-chain controls in the release
workflow (tests, lint, dependency audit, SLSA provenance, SBOM) are
release-blocking.

## Versioning

AIGuard follows [Semantic Versioning](https://semver.org/) with
[PEP 440](https://peps.python.org/pep-0440/) pre-release identifiers:

- **MAJOR** — incompatible changes to the policy Decision contract, hook
  protocol, state file formats, or CLI.
- **MINOR** — backward-compatible features (new policy rules, new assistant
  integrations, new CLI commands).
- **PATCH** — backward-compatible fixes, especially security fixes.
- **Pre-release suffixes** — `aN` (alpha), `bN` (beta), `rcN` (release
  candidate), e.g. `6.1.0b1`.

The version is declared in exactly two places, which must stay in sync:

- `pyproject.toml` → `[project] version`
- `src/aiguard/__init__.py` → `__version__`

## Release automation

Releases are built and published by [.github/workflows/release.yml](../.github/workflows/release.yml)
using PyPI **Trusted Publishing** (OIDC) — no API tokens are stored anywhere.
The workflow runs the test suite, builds the sdist and wheel, then publishes:

- **Push a tag `vX.Y.Z`** → publish to PyPI and create a GitHub Release
  (marked *pre-release* automatically for `a`/`b`/`rc` versions).
- **Manual run** (Actions → Release → Run workflow) → publish to TestPyPI
  for a rehearsal, or to PyPI without a tag.

Nothing is published unless one of these triggers is fired deliberately.

### One-time setup: register the trusted publisher

**PyPI: done** (2026-10-08). A pending publisher for `aiguard-gate` is
registered: owner `alreshi`, repository `aiguard`, workflow `release.yml`,
environment *(any)*. After the first successful publish it becomes a regular
trusted publisher and the project page is created.

**TestPyPI: pending.** For rehearsal publishes, repeat the same registration
at [test.pypi.org](https://test.pypi.org) (**Account settings → Publishing →
Add a new pending publisher**) with identical values. Note: `aiguard-cli`
could not be used — PyPI rejects it as too similar to the existing,
unrelated `aiguard` project; the package was renamed to `aiguard-gate`.

When the repository becomes public, consider adding a dedicated `pypi`
GitHub Actions environment with protection rules and registering it on the
publisher — this is strongly encouraged once others have commit access.

## Release process (maintainer only)

1. Ensure `pytest` passes on a clean checkout (CI re-runs it anyway).
2. Update `CHANGELOG.md`: move *Unreleased* items under the new version and
   date.
3. Bump the version in both locations above.
4. Commit: `Release vX.Y.Z`.
5. Rehearse: Actions → Release → Run workflow → target `testpypi`,
   then verify `pip install --index-url https://test.pypi.org/simple/ aiguard-gate`.
6. Tag and push: `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`.
   The workflow publishes to PyPI and creates the GitHub Release with the
   SBOM attached; provenance attestations are stored on the repository.
7. Verify the published release (see below) before announcing it.

## Verifying a release

Before announcing a release, verify its supply-chain artifacts:

```bash
# 1. Download the release assets
gh release download vX.Y.Z --repo alreshi/aiguard

# 2. Verify SLSA provenance for the wheel and sdist
gh attestation verify aiguard_gate-X.Y.Z-py3-none-any.whl --repo alreshi/aiguard
gh attestation verify aiguard_gate-X.Y.Z.tar.gz --repo alreshi/aiguard

# 3. Inspect the SBOM (dependency inventory of this exact release)
cat sbom.spdx.json | jq '.packages | length'

# 4. Confirm the dependency tree has no known vulnerabilities
pip install aiguard-gate==X.Y.Z && pip-audit
```

All four checks must pass. If provenance verification fails, treat the
artifacts as compromised: yank the PyPI release, delete the GitHub Release,
and open a Security Advisory.

## Support policy

During Beta, only the latest pre-release is supported. After the first stable
release, the latest `MAJOR.MINOR` line receives fixes; older lines do not.
See the supported-versions table in [SECURITY.md](../SECURITY.md).

## Deprecations

Behavior removals are announced in the changelog and, where possible, with a
runtime warning for at least one minor release before taking effect.
Domain-term deprecations are tracked in [GLOSSARY.md](../GLOSSARY.md).
