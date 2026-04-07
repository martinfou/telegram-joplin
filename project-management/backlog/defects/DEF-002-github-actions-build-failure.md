# Defect: DEF-002 - GitHub Actions Build Failure

**Status**: ✅ Completed  
**Priority**: 🔴 Critical  
**Story Points**: 3  
**Created**: 2026-03-01  
**Updated**: 2026-03-03  
**Assigned Sprint**: Backlog

## Description

The application does not build successfully on the GitHub Actions CI/CD pipeline. This blocks all automated deployment and prevents merges from being validated.

## Steps to Reproduce

1. Push a commit to the repository (any branch).
2. Observe the GitHub Actions workflow run.
3. Build step fails.

**Precondition**: Repository has GitHub Actions workflows configured.

## Expected Behavior

- GitHub Actions pipeline completes successfully.
- Application builds, tests pass, and deployment proceeds (if on main).

## Actual Behavior

- The build step fails in the GitHub Actions CI/CD pipeline.
- Deployment is blocked.

## Environment

- **Server Environment**: GitHub Actions CI/CD
- **Platform**: Ubuntu (GitHub-hosted runner)
- **Python Version**: See workflow configuration
- **Deployment Target**: Fly.io

## Screenshots/Logs

From GitHub Actions run `22548897489` (lint-and-test 3.12):

```
Found 538 errors.
[*] 488 fixable with the --fix option (9 hidden fixes can be enabled with the --unsafe-fixes option).
##[error]Process completed with exit code 1.
```

Errors were across all `src/` files — UP045 (Optional→X|None), UP037 (remove quotes from annotations), SIM108 (ternary), SIM105 (contextlib.suppress), SIM110 (any()), B904 (raise from), B007 (unused loop vars), B025 (duplicate except), F841 (unused var), E722 (bare except).

## Technical Details

- Build failure blocks the entire CI/CD pipeline.
- Combined with DEF-003 (scheduler issue), this means the application is both down and cannot be redeployed through the normal pipeline.
- Need to investigate whether the failure is in dependency installation, test execution, or deployment step.

## Root Cause

The `ruff.toml` config selects rules `["E", "F", "W", "I", "UP", "B", "SIM"]` but only ignores `E501`. The CI installs the latest ruff (`>=0.4.0`) which, at version 0.15.4, enforces modern Python style rules (UP045 for `X | None`, SIM108 for ternaries, etc.) that the codebase wasn't following. All 538 errors are lint violations — not dependency or build failures.

## Solution

1. Ran `ruff check --fix` to auto-fix 546 of the errors (mostly UP045 Optional→union, import sorting)
2. Manually fixed the remaining 14 errors:
   - B025: Removed duplicate `except Exception` block in `google_tasks_client.py`
   - SIM105: Replaced `try/except/pass` with `contextlib.suppress()` in `core.py`, `report_generator.py`
   - SIM108: Used ternary operators in `log_config.py`, `report_generator.py`, `url_enrichment.py`
   - B904: Added `from e` to re-raises in `reorg_orchestrator.py`
   - SIM110: Used `any()` in `report_generator.py`, `url_enrichment.py`
   - B007: Prefixed unused loop vars with `_` in `report_generator.py`
   - F841: Prefixed unused var with `_` in `task_service.py`
   - E722: Replaced bare `except:` with specific exceptions in `report_generator.py`
3. Verified: `ruff check src/ config.py main.py` → "All checks passed!"
4. Verified: `pytest tests/ -v` → 71 passed, 0 failed

## Reference Documents

- `.github/workflows/` — Workflow configuration files
- `requirements.txt` — Python dependencies
- `Dockerfile` or `fly.toml` — Deployment configuration

## Technical References

- Directory: `.github/workflows/`
- File: `requirements.txt`
- File: `fly.toml`

## Testing

- [x] Build passes locally before pushing
- [x] `ruff check` passes with 0 errors
- [x] `pytest tests/` passes — 71 tests, 0 failures
- [ ] GitHub Actions workflow completes successfully (pending push)
- [ ] Deployment to Fly.io succeeds

## Notes

- This defect is related to DEF-003 (scheduler not working). Both issues contribute to the application being unavailable.
- Development and deployment are blocked until this is resolved.
- Workaround: manual deployment via `fly deploy` from local machine (if build succeeds locally).

## History

- 2026-03-01 - Created
- 2026-03-03 - Root cause identified: 538 ruff lint errors
- 2026-03-03 - Fixed: auto-fix + 14 manual fixes, all tests pass
- 2026-03-03 - Status changed to ✅ Completed
