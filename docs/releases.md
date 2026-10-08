# Release and Versioning Strategy

## Status: private Beta

The repository is **private** and the current release line is **Beta**. No
public release, tag announcement, or artifact distribution happens without
the maintainer's explicit approval. Until then, all builds are evaluation
builds.

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

Because `aiguard-cli` is not yet on PyPI, use the *pending publisher* flow
(once per index):

1. Log in to [PyPI](https://pypi.org) (and [TestPyPI](https://test.pypi.org)
   for rehearsals). Enable 2FA on both.
2. Go to **Account settings → Publishing → Add a new pending publisher** and
   enter:
   - **PyPI project name:** `aiguard-cli`
   - **Owner:** `alreshi` · **Repository:** `aiguard`
   - **Workflow name:** `release.yml`
   - **Environment name:** leave blank (environment protection rules require
     a public repo or a paid plan; add an environment later when the repo is
     public)
3. Repeat on TestPyPI with the same values.

After the first successful publish, the pending publisher becomes a regular
trusted publisher and the project page exists.

## Release process (maintainer only)

1. Ensure `pytest` passes on a clean checkout (CI re-runs it anyway).
2. Update `CHANGELOG.md`: move *Unreleased* items under the new version and
   date.
3. Bump the version in both locations above.
4. Commit: `Release vX.Y.Z`.
5. **While private:** stop here. Do not tag, do not run the release
   workflow, do not flip repository visibility.
6. **After explicit release approval:**
   - Rehearse: Actions → Release → Run workflow → target `testpypi`,
     then verify `pip install --index-url https://test.pypi.org/simple/ aiguard-cli`.
   - Tag and push: `git tag -a vX.Y.Z -m "vX.Y.Z" && git push origin vX.Y.Z`.
     The workflow publishes to PyPI and creates the GitHub Release.

## Support policy

During Beta, only the latest pre-release is supported. After the first stable
release, the latest `MAJOR.MINOR` line receives fixes; older lines do not.
See the supported-versions table in [SECURITY.md](../SECURITY.md).

## Deprecations

Behavior removals are announced in the changelog and, where possible, with a
runtime warning for at least one minor release before taking effect.
Domain-term deprecations are tracked in [GLOSSARY.md](../GLOSSARY.md).
