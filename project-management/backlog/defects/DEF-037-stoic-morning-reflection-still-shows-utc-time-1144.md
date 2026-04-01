# Defect: DEF-037 - Stoic morning reflection still shows UTC time (11:44 instead of 07:44)

[← Back to Product Backlog](../product-backlog.md)

**Status**: ✅ Done
**Priority**: 🟠 High
**Story Points**: 3
**Created**: 2026-03-31
**Updated**: 2026-03-31
**Assigned Sprint**: Backlog

## Description

Despite the DEF-035 timezone fix, the Stoic Journal morning reflection still writes UTC time in the note. User completed `/stoic` morning at 07:44 Montreal time (EDT) and chose "Replace", but the note header shows "Morning (11:44)" — exactly 4 hours ahead (EDT = UTC-4).

## Steps to Reproduce

1. Have a report configuration saved (e.g., enabled daily reports)
2. At 07:44 EDT, send `/stoic` and complete the morning reflection
3. When prompted about existing section, choose "Replace"
4. Open the saved note in Joplin
5. Observe the header shows "Morning (11:44)" instead of "Morning (07:44)"

## Expected Behavior

Note header: `### 🌞 Morning (07:44)` — matching Montreal local time.

## Actual Behavior

Note header: `### 🌞 Morning (11:44)` — UTC time, 4 hours ahead of Montreal (EDT = UTC-4).

## Root Cause

`save_report_configuration()` in `logging_service.py:602` defaulted timezone to `'UTC'`:

```python
config.get('timezone', 'UTC'),  # <-- hardcoded UTC default
```

Any user who saved a report config (e.g., via `/report_time`, `/report_toggle`) got `timezone: 'UTC'` stored in the database. Then `get_user_timezone()` in `timezone_utils.py` read this stored `'UTC'` and used it instead of falling through to the configured default (`America/Montreal`).

The DEF-035 fix added `America/Montreal` as the app default but never fixed the `'UTC'` already stored in existing report configurations, nor the code that writes new ones with `'UTC'` as default.

## Solution

Three changes:

1. **`src/logging_service.py:602`** — Changed `config.get('timezone', 'UTC')` to `config.get('timezone') or None` so new report configs don't store a timezone unless explicitly set by the user.

2. **`src/timezone_utils.py:58-70`** — `get_user_timezone()` now treats stored `'UTC'` as legacy "no user preference" and falls through to the app default (`America/Montreal`).

3. **`src/handlers/reports.py`** — Changed `_DEFAULT_CONFIG` timezone from `'UTC'` to `'America/Montreal'` and all `cfg.get("timezone", "UTC")` fallbacks to `cfg.get("timezone") or "America/Montreal"`.

## Technical References

- `src/logging_service.py:602` — `save_report_configuration()` timezone default
- `src/timezone_utils.py:55-70` — `get_user_timezone()` with legacy UTC bypass
- `src/handlers/reports.py:39` — `_DEFAULT_CONFIG` timezone
- `tests/test_stoic_sprint18.py` — Updated streak tests to use Montreal timezone

## Testing

- [x] All 412 tests pass
- [x] Streak tests updated to use `get_now_in_default_tz()` instead of `datetime.now(UTC)`
- [x] ruff + mypy clean

## Acceptance Verification

- [x] Root cause identified and fixed
- [x] New report configs won't store 'UTC' as default timezone
- [x] Existing 'UTC' in report configs treated as "use app default"

## History

- 2026-03-31 - Created and fixed
