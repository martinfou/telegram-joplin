# Pre-Commit Checklist

**Purpose**: Ensure CI passes before pushing. The [GitHub Actions workflow](https://github.com/martinfou/telegram-joplin/actions) runs on every push to `main` and will fail if lint, mypy, or tests fail.

## Git Pre-Commit Hook (optional)

Install a hook that runs ruff and mypy automatically before each commit:

```bash
cp scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
```

The hook runs ruff and mypy only (not tests). Run `pytest` manually before pushing.

## ⚠️ Run Before Every Commit

> **Do not commit until lint, mypy, and tests pass.** Run these checks *before* `git commit`, not after.

### Step 1: Lint (run first)

```bash
ruff check src/ config.py main.py
```

If using venv: `.venv/bin/ruff check src/ config.py main.py`

### Step 2: Type check (mypy)

```bash
mypy src/ --ignore-missing-imports --no-strict-optional --explicit-package-bases
```

### Step 3: Tests

```bash
pytest tests/ -v --ignore=tests/e2e
```

### One-liner (lint, mypy, then tests)

```bash
ruff check src/ config.py main.py && mypy src/ --ignore-missing-imports --no-strict-optional --explicit-package-bases && pytest tests/ -v --ignore=tests/e2e
```

## Auto-Fix Lint Issues

Ruff can auto-fix many issues:

```bash
ruff check src/ config.py main.py --fix
```

Then re-run `ruff check` to confirm no remaining errors.

## Reference

- **CI workflow**: [.github/workflows/ci.yml](../../.github/workflows/ci.yml)
- **CI runs**: [GitHub Actions](https://github.com/martinfou/telegram-joplin/actions)
- **Example failure**: [CI run #30](https://github.com/martinfou/telegram-joplin/actions/runs/22724990395) — lint errors caused deploy to be skipped

## Rule

> **1. Run `ruff check` — fix any lint errors.**  
> **2. Run `mypy` — fix any type errors.**  
> **3. Run `pytest` — fix any failing tests.**  
> **4. Then commit.**  
> Do not skip steps 1–3.

## Before Pushing to Main (optional)

If this push includes completed backlog items (DEF-XXX, US-XXX):

- [ ] Run `python scripts/generate_release_notes_draft.py`
- [ ] Add or update section in [RELEASE_NOTES.md](../../RELEASE_NOTES.md)
- See [release-notes-process.md](release-notes-process.md) for full process
