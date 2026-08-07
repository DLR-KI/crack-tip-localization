---
title: Testing
hide: navigation
---
<!--
SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
SPDX-License-Identifier: CC-BY-4.0
-->

<!-- markdownlint-disable-next-line MD025 -->
# Testing

This project provides a few different tests and checks.

In general, we have two files which define all the tests:

- [prek.toml](https://github.com/DLR-KI/crack-tip-localization/blob/main/prek.toml)
- CI pipeline: [.gitlab-ci.yml](https://github.com/DLR-KI/crack-tip-localization/blob/main/.gitlab-ci.yml)

To easily run these tests locally, use:

```bash
./scripts/test.sh
```

If you only want to run the pre-commit hooks manually, use:

```bash
uv run prek run --all-files
```

## Python Code Tests

Feature tests as well as test coverage:

```bash
# run tests
uv run coverage run -m pytest

# serve html coverage report
uv run python -m http.server -d build/htmlcov
```

Static code checks using [ruff](https://docs.astral.sh/ruff):

```bash
# linter
uv run ruff check src
uv run ruff check tests
# formatter
uv run ruff format --diff src
uv run ruff format --diff tests
```

To run automatic static code fixes, use:

```bash
# linter
uv run ruff check --fix src
uv run ruff check --fix tests
# formatter
uv run ruff format src
uv run ruff format tests
```

Static code analysis using [pylint](https://www.pylint.org/):

```bash
uv run pylint --fail-under=8 src
uv run pylint --exit-zero tests
```

Static type checks using [ty](https://docs.astral.sh/ty/reference/cli/#ty-check):

```bash
uv run ty check src
uv run ty check tests
```

General typo checking using [typos](https://github.com/crate-ci/typos):

```bash
uv run typos
```

## Markdown Checks

Verify documentation (markdown) compliance w.r.t.
[markdown linting rules](https://github.com/DavidAnson/markdownlint#rules--aliases)
further specified inside the
[.markdownlint-cli2.jsonc](https://github.com/DLR-KI/crack-tip-localization/blob/main/.markdownlint-cli2.jsonc)
configuration file.

```bash
npm exec markdownlint-cli2 -- "./docs/**/*.md" "./README.md"
```

## License Checks

```bash
uv run licensecheck
uv run reuse lint
```

## Vulnerability Checks

```bash
uv audit
```
