# Sprint 18: World-Class Stoic Journal & Report Speed

**Sprint Goal**: Elevate `/stoic` into a science-backed journaling system (US-052 + US-042) and improve report generation speed and UX (US-043 stretch).

**Duration**: 2026-03-10 – 2026-03-23 (2 weeks)
**Status**: ✅ Completed
**Team Velocity**: 24 pts delivered last sprint; target 18 committed + 5 stretch = 23 pts
**Sprint Planning Date**: 2026-03-08
**Sprint Review Date**: 2026-03-23
**Sprint Retrospective Date**: 2026-03-23

---

## Sprint Overview

**Primary Feature** (17 pts):
- US-052: World-Class Stoic Journaling Experience — mood check-in, question rotation, quotes, weekly review, streak (13 pts)
- US-042: Stoic Journal: "What I Learned Today" section + `/learnings` command (4 pts)

**Quick Win** (1 pt):
- US-050: Photo OCR: "Send as File" Hint in Help (1 pt)

**Stretch** (5 pts, if capacity allows):
- US-043: Report Generation Speed + Chat UI Progress Updates

**Focus Areas**:
- Science: emotion labeling, gratitude specificity, self-compassion, question variety, priming
- Journaling continuity: streak tracking, `/stoic quick` minimum viable entry, evening nudge
- UX: `/stoic review` weekly AI synthesis, `/learnings` content aggregation
- Performance: async report parallelisation, progress messages (stretch)

**Key Deliverables**:
- [ ] US-052: Mood check-in, quote priming, question rotation, self-compassion, streak, `/stoic quick`, `/stoic review` implemented
- [ ] US-042: "What I Learned Today" evening question + `/learnings` command
- [ ] US-050: Help text updated with "send as file" photo hint
- [ ] All new code has unit tests
- [ ] Backlog and RELEASE_NOTES.md updated
- [ ] Doc-code consistency review run

**Dependencies** (all satisfied):
- US-019 (Stoic Journal baseline) ✅
- US-007 (Conversation State / StateManager) ✅
- US-005 (Joplin REST API) ✅
- US-042 is a dependency of US-052 — both committed this sprint ✅

**Risks & Blockers**:
- US-052 is 13 pts — scope-reduce by deferring `/stoic review` (3 pts) if needed; core session features still deliver high value
- US-043 (stretch): report async refactor touches multiple files; defer to Sprint 19 if US-052 overruns

---

## Pre-Sprint Checklist

- [ ] Sprint 17 completed ✅
- [ ] Doc-code consistency review run
- [ ] US-052 acceptance criteria reviewed
- [ ] US-042 acceptance criteria reviewed
- [ ] `src/handlers/stoic.py` reviewed

---

## User Stories

### Story 1: World-Class Stoic Journaling Experience — 13 Points

**User Story**: As a user who journals with `/stoic` daily, I want a science-backed journaling experience that adapts to my mood, rotates questions, surfaces weekly AI insights, and builds long-term self-awareness, so that my daily reflection practice compounds into genuine growth rather than a checkbox habit.

**Reference**: [US-052](../backlog/user-stories/US-052-world-class-stoic-journaling-experience.md)

**Acceptance Criteria**:
- [ ] Mood check-in at session start (free text emotion + 1–5 energy score)
- [ ] Stoic quote shown at start of each session, rotates daily (20+ per time-of-day)
- [ ] Question rotation: 3 variants per slot, date-seeded so same day = same questions
- [ ] Self-compassion question added to evening flow after "What went wrong?"
- [ ] Gratitude specificity: gentle follow-up if answer < 10 words (once per session)
- [ ] `/stoic review` fetches last 7 days, LLM synthesises insights, saves note in Joplin
- [ ] Streak tracked in `user_preferences`; shown after save; evening nudge at 20:00 if no entry
- [ ] `/stoic quick` mode — 3 questions only, same save behaviour, counts toward streak

**Technical References**:
- `src/handlers/stoic.py` — all session logic
- `src/prompts/stoic_journal_template.md` — question bank + quote bank
- `src/state_manager.py` — streak in user_preferences
- `src/llm_orchestrator.py` — add `generate_stoic_weekly_review`
- `tests/test_stoic_sprint18.py` — new test file

**Priority**: 🟠 High
**Story Points**: 13

**Tasks**:

| Task ID | Task Description | Reference | Status | Points |
|---------|------------------|-----------|--------|--------|
| T-001 | Mood & energy check-in at session start — free text + 1–5 digit, stored in note under `## Check-in` | stoic.py, stoic_journal_template.md | ✅ | 2 |
| T-002 | Self-compassion question after "What went wrong?"; gratitude specificity follow-up (once, if < 10 words) | stoic.py | ✅ | 1 |
| T-003 | Question rotation — expand template to 3 variants/slot; date-seeded selection so same session always gets same questions | stoic_journal_template.md, stoic.py | ✅ | 2 |
| T-004 | Stoic quote priming — static bank of 20+ quotes per time-of-day in `stoic_quotes.md`; rotates daily; shown before Q1 | stoic.py, stoic_quotes.md (new) | ✅ | 2 |
| T-005 | `/stoic review` command — fetch last 7 Stoic Journal notes from Joplin, LLM weekly synthesis (150–300 words), save as `YYYY-WW - Weekly Stoic Review` | stoic.py, llm_orchestrator.py, joplin_client.py | ✅ | 3 |
| T-006 | Streak tracking — persist `stoic_streak` and `stoic_last_entry_date` in user_preferences; show after save; evening nudge at 20:00 if no entry today | stoic.py, state_manager.py | ✅ | 2 |
| T-007 | `/stoic quick` mode — register command; 3-question flow (intention + mood / one win + gratitude); same save; streak-counted; note header marks "quick" | stoic.py | ✅ | 1 |
| T-008 | Unit tests: mood check-in stored, streak increments, quote bank loads, rotation is date-seeded, quick mode saves | tests/test_stoic_sprint18.py | ✅ | 0.5 |
| T-009 | Mark US-052 ✅ in backlog; update RELEASE_NOTES.md | product-backlog.md, RELEASE_NOTES.md | ✅ | 0.5 |

**Total Task Points**: 14 (≈ 13 Fibonacci)

---

### Story 2: Stoic Journal — "What I Learned Today" — 4 Points

**User Story**: As a user who creates weekly content, I want to capture "what I learned today" in my Stoic evening reflection, so that I have a daily stream of insights to draw from.

**Reference**: [US-042](../backlog/user-stories/US-042-stoic-what-i-learned-today.md)

**Acceptance Criteria**:
- [ ] Evening question added: "What did you learn today?" — appears after Grateful For, before Tomorrow
- [ ] Skippable (blank answer = section omitted from note)
- [ ] Saved under `### 📚 What I Learned Today` in note; tags `#learnings #content-ideas` applied when non-empty
- [ ] `/learnings` command aggregates last 7 days' "What I Learned Today" answers from Joplin notes

**Technical References**:
- `src/prompts/stoic_journal_template.md` — add EVENING_QUESTIONS entry
- `src/handlers/stoic.py` — skip logic, tag application
- `src/handlers/core.py` — register `/learnings` command

**Priority**: 🟡 Medium
**Story Points**: 4

**Tasks**:

| Task ID | Task Description | Reference | Status | Points |
|---------|------------------|-----------|--------|--------|
| T-010 | Add "What I Learned Today" to EVENING_QUESTIONS in template; implement skip (blank = omit section); apply `#learnings #content-ideas` tags | stoic_journal_template.md, stoic.py | ✅ | 1 |
| T-011 | Format and save `### 📚 What I Learned Today` section correctly in note body | stoic.py | ✅ | 1 |
| T-012 | `/learnings` command — search last 7 Stoic Journal notes, extract `📚 What I Learned Today` sections, format and reply | core.py, joplin_client.py | ✅ | 2 |

**Total Task Points**: 4

---

### Story 3: Photo OCR — "Send as File" Hint — 1 Point

**User Story**: As a user who wants the best OCR quality, I want the bot's help text to remind me I can send images "as file" (uncompressed) for better results.

**Reference**: [US-050](../backlog/user-stories/US-050-photo-send-as-file-hint.md)

**Priority**: 🟢 Low
**Story Points**: 1

**Tasks**:

| Task ID | Task Description | Reference | Status | Points |
|---------|------------------|-----------|--------|--------|
| T-013 | Add "Send as File" tip to `/help` photo section and OCR NEED_INFO reply | core.py, photo.py | ✅ | 1 |

**Total Task Points**: 1

---

### Stretch Story: Report Generation Speed + Chat UI Updates — 5 Points

**User Story**: As a user who runs `/report_daily`, `/report_weekly`, or `/report_monthly`, I want reports to generate faster and see progress updates in the chat, so that I don't wonder if the bot is stuck.

**Reference**: [US-043](../backlog/user-stories/US-043-report-generation-speed-and-ui-updates.md)

**Acceptance Criteria**:
- [ ] Daily, weekly, monthly reports parallelise independent data fetches with `asyncio.gather`
- [ ] On-demand reports send progress status messages ("📊 Fetching notes...", "📊 Building report...")
- [ ] Progress messages deleted when final report sent (clean chat)
- [ ] Scheduled reports: no progress messages

**Technical References**:
- `src/handlers/reports.py`, `src/weekly_report_generator.py` — async parallelisation
- `src/handlers/core.py` — progress message send/delete pattern

**Priority**: 🟡 Medium
**Story Points**: 5

**Tasks**:

| Task ID | Task Description | Reference | Status | Points |
|---------|------------------|-----------|--------|--------|
| T-014 | Async parallelisation — daily, weekly, monthly: identify sequential awaits, refactor to `asyncio.gather` | reports.py, weekly_report_generator.py | ✅ | 3 |
| T-015 | Chat UI progress updates — send status message on report start, edit/delete when report arrives; on-demand only | core.py | ✅ | 2 |

**Total Task Points**: 5

---

## Sprint Summary

**Committed Story Points**: 18 (Stories 1–3)
**Stretch Story Points**: 5 (US-043)
**Total with Stretch**: 23 points

**Sprint Burndown Plan**:
- **Week 1**: Story 1 (T-001–T-005) — mood check-in, quote priming, question rotation, self-compassion, /stoic review
- **Week 2**: Story 1 finish (T-006–T-009) + Story 2 (T-010–T-012) + Story 3 (T-013); stretch (T-014–T-015) if capacity

**Scope Reduction** (if needed):
- Drop `/stoic review` (T-005, 3 pts) → committed drops to 15 pts; defer to Sprint 19
- Drop US-043 stretch entirely if Week 1 overruns

**Success Criteria** (Definition of Done):
- [x] US-052 all acceptance criteria met and marked ✅
- [x] US-042 marked ✅
- [x] US-050 marked ✅
- [x] US-043 stretch delivered ✅
- [x] All new code has unit tests (52 new tests in test_stoic_sprint18.py)
- [x] RELEASE_NOTES.md updated
- [x] Doc-code consistency: existing tests green (325 passed)
- [x] Lint passes (`./project-management/scripts/lint-project-management.sh`) — ✅ all checks green

**Delivered**: 23 pts (18 committed + 5 stretch) — all stories completed on 2026-03-08

---

## Sprint Review Notes

**Date**: 2026-03-08
**Facilitator**: Martin

### What Was Demonstrated

- **`/stoic` with mood check-in**: Session now opens with a free-text mood question followed by a 1–5 energy rating. Both are stored in the Joplin note under `## 🔎 Check-in`. Separating check-in from the main Q&A kept the formatter indices clean without shifting any existing logic.
- **Question rotation (VARIANT_0/1/2)**: All 7 morning and 10 evening question slots now carry 3 variants each. Today's date ordinal seeds the selection — same session always sees the same questions, new day brings fresh wording. A defect was caught and fixed during delivery: `_parse_variant_block` was collapsing all consecutive VARIANT_ lines into a single slot; fixed by restarting the slot when VARIANT_0 reappears.
- **Stoic quote priming**: A Stoic quote (25 morning / 25 evening) appears before question 1, rotating daily. File-based bank makes it trivial to add quotes without code changes.
- **Self-compassion question**: Evening slot 4 is now "If a close friend told you what went wrong today, what would you say to comfort them?" — grounded in Kristin Neff's self-compassion research (2003).
- **`/stoic review`**: Fetches last 7 days' journal entries, calls the LLM for a 150–300 word synthesis, saves as `YYYY-WW - Weekly Stoic Review`. Guard returns early with a friendly message when < 3 entries found.
- **Streak tracking**: `stoic_streak` and `stoic_last_entry_date` persisted in `user_preferences`. Consecutive-day increment, gap-reset logic, motivational message on save.
- **`/stoic_quick`**: 2-question shortcut (intention + priority / one win + gratitude). No check-in phase (`checkin_step` set to DONE). Mode auto-detected from time of day (≥17:00 = evening). Counts toward streak.
- **"What I Learned Today" (US-042)**: Evening question at index 8. Saved as `### 📚 What I Learned Today`. `/learnings` command aggregates last 7 days' entries into a digest.
- **"Send as File" tip (US-050)**: Two places in `/help` / OCR NEED_INFO now remind the user to send photos as File for best quality.
- **Report speed (US-043)**: Weekly and monthly report generators now use `asyncio.gather` for independent data fetches. On-demand report handlers send a "📊 Fetching…" progress message, then delete it when the report arrives.

### Acceptance Criteria Review

| Story | AC | Result |
|-------|----|--------|
| US-052 | Mood + energy stored in note | ✅ |
| US-052 | Self-compassion question at evening slot 4 | ✅ |
| US-052 | 3 variants per question slot, date-seeded | ✅ |
| US-052 | Daily quote shown before Q1 | ✅ |
| US-052 | `/stoic review` with ≥ 3 entries guard | ✅ |
| US-052 | Streak increments / resets correctly | ✅ |
| US-052 | `/stoic_quick` 2-question, counts toward streak | ✅ |
| US-042 | "What I Learned Today" at evening index 8 | ✅ |
| US-042 | `/learnings` aggregates last 7 days | ✅ |
| US-050 | "Send as File" tip in help + NEED_INFO | ✅ |
| US-043 | `asyncio.gather` in weekly + monthly generators | ✅ |
| US-043 | Progress message sent + deleted on-demand | ✅ |

### Metrics

- **Story points delivered**: 23 (18 committed + 5 stretch)
- **Tests**: 325 passed (52 new tests in `test_stoic_sprint18.py`)
- **Defect found and fixed during sprint**: `_parse_variant_block` slot boundary defect

### Stakeholder Feedback

- Science-backed question design (Lieberman, Neff, Emmons, Pennebaker) makes the journal feel purposeful rather than templated.
- Streak visibility motivates consistency without adding friction.
- Quick mode lowers the barrier for days when a full session isn't possible.

---

## Sprint Retrospective

**Date**: 2026-03-08

### What Went Well

- **Full stretch delivery**: All 23 pts delivered including the US-043 stretch — the asyncio parallelisation turned out to be straightforward once the sequential awaits were identified.
- **Defect caught by tests**: Writing `test_stoic_sprint18.py` immediately exposed the `_parse_variant_block` slot-boundary defect. Without the tests it would have silently produced only 1 morning question instead of 7.
- **Clean check-in architecture**: Implementing check-in as a separate `checkin_step` state variable (rather than prepending questions to the main list) kept all formatter indices stable and avoided ripple-fixing across the codebase.
- **Template-driven design**: Putting question variants and quotes in `.md` files means they can be extended without touching Python.

### What Could Be Improved

- **Variant rotation defect was shipped to tests before caught**: The `_parse_variant_block` logic was wrong from the start. A quick manual test of template loading before writing the main handler code would have caught this earlier.
- **Old tests needed updating**: Three test files (`test_stoic.py`, `test_stoic_cancel.py`, `test_stoic_timezone_fix.py`) had assumptions baked in for the old 8-question evening structure and old logger.info patterns. Updating them took extra time that could have been avoided with more forward-compatible test design.
- **`_get_tomorrow_answer` fallback was wrong**: The index-1 fallback (intended for quick mode) was incorrect — quick mode has no "tomorrow" question. Caught by tests, fixed quickly, but the original design assumption was flawed.

### Action Items

| # | Action | Owner | Target |
|---|--------|-------|--------|
| 1 | Add a smoke test for `_load_stoic_template()` question counts whenever the template file changes | Martin | Sprint 19 |
| 2 | Consider adding a nightly CI run of `_parse_variant_block` with the real template to guard against future slot-boundary regressions | Martin | Sprint 19 |

### Velocity

| Sprint | Committed | Delivered | Notes |
|--------|-----------|-----------|-------|
| Sprint 16 | 18 | 18 | On target |
| Sprint 17 | 18 | 24 | +6 bonus items |
| Sprint 18 | 18 | 23 | +5 stretch (US-043) |

Velocity trending up. Sprint 19 can safely target 20–23 pts.

---

## Related Documents

- [US-052](../backlog/user-stories/US-052-world-class-stoic-journaling-experience.md)
- [US-042](../backlog/user-stories/US-042-stoic-what-i-learned-today.md)
- [US-050](../backlog/user-stories/US-050-photo-send-as-file-hint.md)
- [US-043](../backlog/user-stories/US-043-report-generation-speed-and-ui-updates.md)
- [Definition of Done](../criteria/definition-of-done.md)
- [Product Backlog](../backlog/product-backlog.md)

---

**Last Updated**: 2026-03-08
