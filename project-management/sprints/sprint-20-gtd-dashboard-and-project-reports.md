# Sprint 20: GTD Dashboard & Project Intelligence

**Sprint Goal**: Transform the two most-used status commands into world-class GTD tools — a personal productivity cockpit (`/tasks_status`) and a full portfolio project report (`/project_report`) — while closing the last deferred stretch item from Sprint 19 and two overdue retro action items.

**Duration**: 2026-03-24 – 2026-04-06 (2 weeks)
**Status**: ✅ Complete
**Team Velocity**: 19 pts last sprint; target 20 committed + 5 stretch = 25 pts
**Sprint Planning Date**: 2026-03-10
**Sprint Review Date**: 2026-04-06
**Sprint Retrospective Date**: 2026-04-06

---

## Sprint Overview

**High-Priority Deliverables (13 pts):**

- US-059: GTD Dashboard — replace `/tasks_status` sync diagnostics with a personal productivity cockpit (5 pts)
- US-060: Project Report — replace `/project_status` tag count with a per-project portfolio view with stall detection (8 pts)

**Deferred from Sprint 19 (5 pts):**

- US-055: Google Tasks — duplicate check before add, offer edit/priority/cancel (5 pts)

**Retro Action Items — Sprint 18 & 19 carry-overs (2 pts):**

- T-020: Update MCP story/defect templates to remove obsolete template boilerplate (1 pt)
- T-021: Add `_parse_variant_block` slot boundary CI guard test (1 pt)

**Stretch (5 pts, if capacity allows):**

- US-058: Conversational intent — bot understands natural phrasing without explicit commands (5 pts)

**Bonus shipped (unplanned, 5 pts):**

- US-061: Stoic Journal — LLM-generated image after `/stoic_done` (5 pts)

**Hotfixes shipped since Sprint 19 close (not counted in velocity):**

- fix(DEF-030 re-open): Stoic note timestamp UTC defect — LLM path still used `datetime.now()` — fixed by passing `ts` from stoic.py
- fix: `/tasks` (plural) command registered as alias for `/tasks_list`

**Focus Areas:**

- Intelligence: commands that answer GTD questions, not expose system internals
- Closure: finally ship the deferred Sprint 19 stretch item and two 2-sprint-old retro items
- Reliability: CI guard prevents future slot-boundary regressions in Stoic template

**Key Deliverables:**

- US-059: `/tasks_status` shows overdue, today, this week, inbox count, health line
- US-060: `/project_report` shows per-project next action, stall detection, no-next-action alerts
- US-061: `/stoic_done` generates and embeds a symbolic image into the Stoic note; backfill script available
- US-055: Task creation checks for duplicates before adding; inline keyboard on match
- T-020: MCP templates no longer reference non-existent template boilerplate
- T-021: `_parse_variant_block` slot boundary guarded by CI test
- All new code has unit tests
- RELEASE_NOTES.md updated

**Dependencies (all satisfied):**

- US-012 (Google Tasks) ✅
- US-034 (Joplin ↔ Google Tasks project sync) ✅
- US-044 (/project_new) ✅
- US-015 (Weekly Report) ✅
- DEF-028 (timezone fix) ✅ Sprint 19

**Risks & Blockers:**

- US-060 requires Joplin note `updated_time` field — verify API returns it; fallback to `created_time` if not
- US-059 Google Tasks "inbox" detection (tasks with no list) may need API exploration; timebox to 2h
- US-055 fuzzy duplicate matching threshold needs tuning — default to exact + case-insensitive first

---

## Pre-Sprint Checklist

- Sprint 19 completed ✅
- DEF-030 (Stoic UTC timestamp) fully fixed in LLM path ✅
- `/tasks` alias registered ✅
- US-059 and US-060 user stories written and in backlog ✅
- Backlog integrity validated (MCP) ✅
- PM lint passed ✅
- Doc-code consistency review run (docs updated from code; report in reports/doc-code-consistency-latest.md)

---

## Story 1: GTD Dashboard — /tasks_status Cockpit — 5 Points

**User Story**: [US-059](../backlog/user-stories/US-059-us-059-world-class-gtd-dashboard-tasks_status-as-p.md)

**Description**: Replace the current sync-diagnostic output with a personal productivity cockpit: overdue, due today, due this week, inbox count, and a motivating empty state. Old sync diagnostics move to `/tasks_sync_detail`.

**Acceptance Criteria**:

- Overdue section: count + top 3 titles with days overdue; "✅ All clear" if none
- Today section: tasks due today with project context; nudge to `/task` if empty
- This week section: tasks grouped by project for next 7 days; `+N more` if > 5
- Inbox section: count of tasks with no project; nudge if > 5
- System health: single line at bottom; expands only if action needed
- Motivating empty state when everything is clear
- Timezone-correct (user's configured tz)
- Response < 2 seconds
- Old sync diagnostics preserved at `/tasks_sync_detail`

**Technical References**:

- `src/handlers/google_tasks.py` — `_tasks_status()` (replace body)
- `src/task_service.py` — add `get_dashboard_data(user_id)`
- `src/timezone_utils.py` — `get_user_timezone_aware_now()`

**Priority**: 🟠 High
**Story Points**: 5

**Tasks**:


| Task ID | Task Description                                                                                                | Reference                   | Status | Points |
| ------- | --------------------------------------------------------------------------------------------------------------- | --------------------------- | ------ | ------ |
| T-001   | Add `get_dashboard_data()` to `task_service.py`: returns overdue, due_today, due_week, inbox_count              | task_service.py             | ✅      | 2      |
| T-002   | Rewrite `_tasks_status()` handler body to render the 5-section cockpit; move old body to `_tasks_sync_detail()` | google_tasks.py             | ✅      | 2      |
| T-003   | Unit tests: overdue section, today section, empty state, not-connected state                                    | tests/test_gtd_dashboard.py | ✅      | 1      |


---

## Story 2: World-Class Project Report — 8 Points

**User Story**: [US-060](../backlog/user-stories/US-060-us-060-world-class-project-report-full-portfolio-v.md)

**Description**: Replace `/project_status` tag count with a per-project portfolio view. Each project shows name, status badge, next Google Task, last activity, and note/task counts. Stalled projects and missing-next-action alerts surfaced at the top.

**Acceptance Criteria**:

- Portfolio header: active/blocked/planning/"no next action" counts; warns if active > 15
- Per-project block: name, status, next task, last activity, note count, open task count
- Stall detection: no note update + no task complete in 14+ days → "⚠️ Stalled" + "Needs Attention" section
- No-next-action alert: projects with no open task flagged with nudge to `/task`
- Status order: Blocked → Stalled → Building → Planning; completed last (collapsed)
- Drill-down: `/project_report <name>` fuzzy match shows full detail
- Weekly report integration: optional project section in `/weekly_report`
- Timezone-correct; < 3s for 20 projects

**Technical References**:

- `src/handlers/core.py` — `_project_status()` → replace with `_project_report()`
- `src/joplin_client.py` — `get_notes_with_tag()`, `get_all_notes()` with `updated_time` field
- `src/task_service.py` — `get_tasks_by_project()`
- `src/handlers/reports.py` — weekly report integration

**Priority**: 🟠 High
**Story Points**: 8

**Tasks**:


| Task ID | Task Description                                                                              | Reference                    | Status | Points |
| ------- | --------------------------------------------------------------------------------------------- | ---------------------------- | ------ | ------ |
| T-004   | Add `updated_time` to note fields; `get_tasks_by_project()` — batch fetch, group by folder    | task_service.py              | ✅      | 2      |
| T-005   | Build per-project block renderer and portfolio header; stall + no-next-action detection logic | core.py                      | ✅      | 3      |
| T-006   | Implement `/project_report <name>` drill-down (fuzzy match, full detail)                      | core.py                      | ✅      | 1      |
| T-007   | Add project portfolio section to `/weekly_report` (optional, gated by config)                 | reports.py                   | ✅      | 1      |
| T-008   | Unit tests: stall detection, no-next-action, drill-down, empty state                          | tests/test_project_report.py | ✅      | 1      |


---

## Story 3: Google Tasks — Duplicate Check Before Add — 5 Points

**User Story**: [US-055](../backlog/user-stories/US-055-google-tasks-duplicate-check-before-add.md)

**Description**: Before creating a Google Task, check if a task with the same or similar title already exists. If found, show inline keyboard: Edit / Change Priority / Add Anyway / Cancel.

**Acceptance Criteria**:

- Before creating, search existing tasks for title match (case-insensitive, strip punctuation)
- Duplicate found: show inline keyboard with Edit / Change Priority / Add Anyway / Cancel
- No duplicate: proceed silently as before
- Works in braindump and direct task creation flows
- Unit tests: duplicate found, no duplicate, user cancel

**Technical References**:

- `src/task_service.py` — duplicate detection
- `src/handlers/core.py` — inline keyboard for duplicate confirmation

**Priority**: 🟡 Medium
**Story Points**: 5

**Tasks**:


| Task ID | Task Description                                                                                                          | Reference                    | Status | Points |
| ------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------- | ------ | ------ |
| T-009   | `detect_duplicate_task()` in `task_service.py`: fetch existing tasks, compare title (case-insensitive, strip punctuation) | task_service.py              | ✅      | 2      |
| T-010   | Show inline keyboard when duplicate detected; wire Edit/Priority/Add Anyway/Cancel callbacks                              | core.py                      | ✅      | 2      |
| T-011   | Unit tests: duplicate found flow, no duplicate, cancel flow                                                               | tests/test_task_duplicate.py | ✅      | 1      |


---

## Story 4: Retro Action Items — CI Guards & Template Cleanup — 2 Points

**Source**: Sprint 18 & 19 Retrospectives

**Tasks**:


| Task ID | Task Description                                                                                             | Reference                         | Status | Points |
| ------- | ------------------------------------------------------------------------------------------------------------ | --------------------------------- | ------ | ------ |
| T-012   | Update MCP story/defect templates: remove obsolete template boilerplate (real paths only)                    | mcp-project-management/templates/ | ✅      | 1      |
| T-013   | Add `test_parse_variant_block_slot_boundary`: assert all 3 variants present for each slot across all 6 slots | tests/test_stoic_sprint18.py      | ✅      | 1      |


---

## Story 5: Stoic Journal — LLM Image After Save — 5 Points (Bonus)

**User Story**: [US-061](../backlog/user-stories/US-061-stoic-llm-image-after-reflection.md)

**Description**: After `/stoic_done`, generate a symbolic image (Gemini) representing the reflection and embed it into the saved Joplin note. Provide a backfill script for existing Stoic notes.

**Acceptance Criteria**:

- Image generated after save (including replace/append flows)
- Uploaded as Joplin resource and embedded in note body
- Safe/tasteful prompt (no text, journal-appropriate)
- Failure does not break save flow
- Backfill script available for existing notes

**Technical References**:

- `src/handlers/stoic.py` — generate and embed after save
- `src/stoic_image.py` — Gemini image prompt/call
- `scripts/backfill_stoic_images.py` — backfill existing notes

**Priority**: 🟠 High
**Story Points**: 5

**Tasks**:


| Task ID | Task Description                                                                | Reference                        | Status | Points |
| ------- | ------------------------------------------------------------------------------- | -------------------------------- | ------ | ------ |
| T-017   | Generate + embed image after `/stoic_done` (new note + update + replace/append) | stoic.py                         | ✅      | 3      |
| T-018   | Add Gemini image generator for Stoic reflections                                | stoic_image.py                   | ✅      | 1      |
| T-019   | Backfill script for existing Stoic notes (dry-run, limit)                       | scripts/backfill_stoic_images.py | ✅      | 1      |


---

## Stretch Story: Conversational Intent — 5 Points

**User Story**: [US-058](../backlog/user-stories/US-058-bot-understands-natural-conversational-intent-from.md)

**Description**: Bot understands natural phrasing without explicit commands. "I need to call John tomorrow" → task. "Here are my notes from the meeting" → note. No need to prefix with `/task` or `/note`.

**Acceptance Criteria**:

- Bot correctly routes action-oriented phrasing to Google Tasks without `/task`
- Bot correctly routes knowledge-oriented phrasing to Joplin without `/note`
- Ambiguous input asks for clarification before acting
- Explicit commands still work unchanged (no regression)
- Unit tests cover action routing, knowledge routing, ambiguous routing

**Technical References**:

- `src/handlers/core.py` — `_route_plain_message()` — intent classification enhancement
- `src/llm_orchestrator.py` — intent classifier prompt

**Priority**: 🟡 Medium
**Story Points**: 5

**Tasks**:


| Task ID | Task Description                                                                                  | Reference                           | Status | Points |
| ------- | ------------------------------------------------------------------------------------------------- | ----------------------------------- | ------ | ------ |
| T-014   | Enhance intent classifier: add explicit action/knowledge/ambiguous labels to LLM routing prompt   | llm_orchestrator.py                 | ⭕      | 2      |
| T-015   | Route action-labeled messages directly to task creation; knowledge-labeled to note creation       | core.py                             | ⭕      | 2      |
| T-016   | Unit tests: action routing, knowledge routing, ambiguous routing, regression on explicit commands | tests/test_conversational_intent.py | ⭕      | 1      |


---

## Sprint Summary

**Committed Story Points**: 20

- US-059: 5 pts
- US-060: 8 pts
- US-055: 5 pts
- T-020 + T-021 (retro): 2 pts

**Stretch Story Points**: 5 (US-058)
**Total with Stretch**: 25 points

**Sprint Burndown Plan**:

- **Week 1**: US-059 GTD Dashboard (T-001–T-003) + US-055 dup check (T-009–T-011) + retro items (T-012–T-013)
- **Week 2**: US-060 Project Report (T-004–T-008) + stretch US-058 if capacity (T-014–T-016)

**Scope Reduction** (if needed):

- Drop US-058 stretch first (5 pts)
- Drop US-060 weekly report integration T-007 (-1 pt) if Joplin `updated_time` API proves complex

**Success Criteria** (Definition of Done):

- US-059 `/tasks_status` is a GTD cockpit; old diagnostics at `/tasks_sync_detail`
- US-060 `/project_report` shows stalls, next actions, portfolio health
- US-055 duplicate task detection working in all creation flows
- T-012 MCP templates cleaned of non-existent file references
- T-013 `_parse_variant_block` slot boundary test added
- All new code has unit tests
- RELEASE_NOTES.md updated
- Backlog updated
- Lint passes (`project-management/scripts/check-links.sh` / `lint-project-management.sh`)

---

## Related Documents

- [US-059](../backlog/user-stories/US-059-us-059-world-class-gtd-dashboard-tasks_status-as-p.md)
- [US-060](../backlog/user-stories/US-060-us-060-world-class-project-report-full-portfolio-v.md)
- [US-055](../backlog/user-stories/US-055-google-tasks-duplicate-check-before-add.md)
- [US-058](../backlog/user-stories/US-058-bot-understands-natural-conversational-intent-from.md)
- [Sprint 19](sprint-19-polish-and-bug-fixes.md)
- [Product Backlog](../backlog/product-backlog.md)

---

**Last Updated**: 2026-04-06 (sprint closed; link lint addressed)