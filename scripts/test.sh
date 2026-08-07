#!/usr/bin/env bash
#
# SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
# SPDX-License-Identifier: GPL-3.0-or-later
#
# cspell:ignore prek tput

# exit script if any command fails
set -e

# Helper to print step labels
print_step() {
  echo
  echo "$(tput bold)$1...$(tput sgr0)"
}

# pre commit on all files and changes (not only staged ones)
print_step "Pre-commit checks"
uv run prek run --all-files

# markdown
print_step "Markdown linting"
npm exec markdownlint-cli2 -- "./docs/**/*.md" "./README.md"

# static code checks (ruff: linter)
print_step "Ruff linter"
uv run ruff check src
uv run ruff check tests
if [[ -n $(find scripts -name "*.py[i]" -print -quit) ]]; then
  uv run ruff check scripts
fi
# static code checks (ruff: formatter)
print_step "Ruff formatter"
uv run ruff format --diff src
uv run ruff format --diff tests
if [[ -n $(find scripts -name "*.py[i]" -print -quit) ]]; then
  uv run ruff format --diff scripts
fi

# static type checks (ty)
print_step "Type checks"
uv run ty check src
uv run ty check tests
if [[ -n $(find scripts -name "*.py[i]" -print -quit) ]]; then
  uv run ty check scripts
fi

# static code analysis (pylint)
print_step "Pylint code analysis"
uv run pylint --fail-under=8 src

# typo check (typos)
print_step "Typo check"
uv run typos

# unit tests
print_step "Unit tests"
uv run coverage run -m pytest

# license checks
print_step "License checks"
uv run licensecheck
uv run reuse lint

# vulnerability checks
print_step "Vulnerability checks"
uv audit

# success message
echo
echo "$(tput bold)Congratulations 🎉$(tput sgr0)"
echo "All tests successful."
