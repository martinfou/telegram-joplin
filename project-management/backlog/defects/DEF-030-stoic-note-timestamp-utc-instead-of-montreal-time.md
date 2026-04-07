# Defect: DEF-030 - Stoic Journal Note Timestamp Shows UTC Instead of Montreal Time

**Status**: ✅ Completed
**Priority**: 🟡 Medium
**Story Points**: 2
**Created**: 2026-03-09
**Updated**: 2026-03-10
**Assigned Sprint**: Sprint 19

---

## Problem Statement

Timestamps in Stoic Journal notes (e.g. "### 🌞 Morning (09:30)", "### 🌙 Evening (21:15)") are displayed in UTC instead of the user's local timezone (Montreal / America/Montreal). Users in Montreal expect to see their local time in the journal entries.

**User impact:** A Montreal user doing an evening reflection at 9pm local sees "02:00" (UTC) in the note instead of "21:00". Confusing and breaks the journal's value as a personal record.

---

## Root Cause

**LLM formatting path** in `src/llm_orchestrator.py` line 622:

```python
ts = datetime.now().strftime("%H:%M")  # ← UTC on Fly.io
```

When the Stoic handler uses the LLM to format the reflection (`format_stoic_reflection`), the timestamp is passed as `datetime.now()` — server time (UTC on Fly.io). The LLM prompt says "Use timestamp: {ts}" and embeds this UTC value.

**Rule-based fallback** in `src/handlers/stoic.py` correctly uses `get_user_timezone_aware_now()` — so when the LLM fails and the code falls back to `_format_morning_content` / `_format_evening_content`, the timestamp is correct. The defect only appears when the LLM path succeeds.

---

## Steps to Reproduce

1. Set timezone to America/Montreal via `/report_set_timezone America/Montreal`
2. Run `/stoic morning` or `/stoic evening` at a known local time (e.g. 9:00 Montreal)
3. Complete the session and save with `/stoic_done`
4. Open the saved note in Joplin
5. Check the timestamp in the Morning/Evening section header — it shows UTC (e.g. 14:00 when local is 9:00 Eastern)

---

## Expected Behavior

Timestamps in Stoic notes should use the user's configured timezone (e.g. Montreal = America/Montreal). Same as reports and the rule-based Stoic formatter.

---

## Actual Behavior

When LLM formatting is used, timestamps appear in UTC.

---

## Affected Code

| File | Location | Change |
|------|----------|--------|
| `src/llm_orchestrator.py` | `_format_stoic_reflection_impl` line 622 | Pass user timezone-aware time instead of `datetime.now()` |
| `src/handlers/stoic.py` | Call to `format_stoic_reflection` | Pass `user_id` and `orch.logging_service` so LLM orchestrator can resolve user timezone |

---

## Proposed Solution

1. Add optional `user_id` and `logging_service` params to `format_stoic_reflection` (or a `user_tz_now` datetime param)
2. In `_format_stoic_reflection_impl`, use `get_user_timezone_aware_now(user_id, logging_service).strftime("%H:%M")` when user context is provided; fallback to `datetime.now()` only when not (e.g. tests)
3. Update stoic handler to pass user context when calling `format_stoic_reflection`

---

## References

- [DEF-005: Stoic Journal Timezone](DEF-005-stoic-journal-timezone-and-data-loss.md) — Fixed note title/date; rule-based formatter uses `get_user_timezone_aware_now`. This defect is the remaining LLM path.
- `src/timezone_utils.py` — `get_user_timezone_aware_now`, `get_user_timezone`

## History

- 2026-03-09 - Created
- 2026-03-10 - Assigned to Sprint 19; Status changed to ✅ Completed
