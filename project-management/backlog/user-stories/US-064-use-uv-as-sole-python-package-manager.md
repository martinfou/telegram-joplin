---

## template_version: 1.1.0
last_updated: 2026-04-06
compatible_with: [feature-request, sprint-planning, product-backlog]
requires: [markdown-support]

# User Story: US-064 - Use uv as the Sole Python Package Manager

[← Back to Product Backlog](../product-backlog.md)

**Status**: ✅ Done  
**Priority**: 🟡 Medium  
**Story Points**: 5  
**Created**: 2026-04-06  
**Updated**: 2026-04-06  
**Assigned Sprint**: —  

## Description

Standardize the **telegram-joplin** codebase so **uv** is the **only** supported tool for Python dependency install, lockfile management, and virtual environments. Other managers (plain `pip install` workflows, Poetry, Pipenv, etc.) are not part of the documented or CI-supported path.

## User Story

As a contributor or operator,  
I want one documented and automated way to install Python dependencies (`uv`),  
so that environments are reproducible and instructions never disagree.

## Acceptance Criteria

- **Documentation**: README, Quick Start, and contributor docs describe **uv** only (sync/install from lockfile; how to get uv). Remove or clearly deprecate alternate install paths.
- **Lockfile**: Project uses `**uv.lock`** (or agreed uv-native lock) as source of truth; `pyproject.toml` aligned.
- **CI**: GitHub Actions (and any other automation) use `**uv`** for dependency install and test runs—not ad-hoc `pip install -r requirements.txt` unless generated/managed by uv.
- **Scripts**: Pre-commit, local dev scripts, and `scripts/` entrypoints reference **uv** where they invoke Python tooling (or document a single venv created via uv).
- **Cleanup**: Remove redundant `requirements*.txt` files **or** mark them generated-only from uv and not hand-edited (team choice recorded in README).

## Non-goals

- Changing runtime behavior of the bot (dependency versions may bump only as needed for the migration).

## History

- 2026-04-06 - Created (INDEX + product backlog).
- 2026-04-06 - **Done**: `pyproject.toml` + `uv.lock`; CI (`astral-sh/setup-uv` + `uv sync --frozen` + `uv run`); Dockerfile (`uv sync --frozen --no-dev`, `PATH` to `.venv`); `setup.sh` and docs; removed `requirements.txt` / `requirements-dev.txt`.
