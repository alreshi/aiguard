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

## Release process (maintainer only)

1. Ensure `pytest` passes on a clean checkout.
2. Update `CHANGELOG.md`: move *Unreleased* items under the new version and
   date.
3. Bump the version in both locations above.
4. Commit: `Release vX.Y.Z`.
5. Tag: `git tag -a vX.Y.Z -m "vX.Y.Z"` and push with `git push --tags`.
6. **While private:** stop here. Do not publish to PyPI, do not create a
   GitHub Release, do not flip repository visibility.
7. **After public approval:** build (`python -m build`), publish to PyPI
   (`twine upload dist/*`), and create a GitHub Release from the tag with the
   changelog entry as notes.

## Support policy

During Beta, only the latest pre-release is supported. After the first stable
release, the latest `MAJOR.MINOR` line receives fixes; older lines do not.
See the supported-versions table in [SECURITY.md](../SECURITY.md).

## Deprecations

Behavior removals are announced in the changelog and, where possible, with a
runtime warning for at least one minor release before taking effect.
Domain-term deprecations are tracked in [GLOSSARY.md](../GLOSSARY.md).
