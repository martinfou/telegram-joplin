# Sprint 20: Manual Testing Guide

**Sprint status**: Backlog marks Sprint 20 complete as of 2026-04-06. Run the sections below in Telegram once before your next production push if you have not already smoke-tested these flows.

This document describes how to manually verify the Sprint 20 changes in Telegram: **GTD Dashboard** (`/tasks_status`), **Project Report** (`/project_report`), **Duplicate task check** (before adding tasks), and **Weekly report project portfolio**.

**Stories**: US-059 (GTD Dashboard), US-060 (Project Report), US-055 (Duplicate check), US-061 (Stoic image).

---

## Prerequisites

- **Bot running** and reachable in Telegram (local or deployed).
- **Google Tasks connected**: `/tasks_connect` completed; at least one task list with some tasks (including tasks with and without due dates, and optionally tasks without a project / “inbox”).
- **Joplin**: Projects folder with notes; some notes tagged with `status/planning`, `status/building`, `status/blocked`, or `status/done` (so `/project_report` has data). At least one project with a linked Google Tasks project (for next-action and stall detection).
- **Timezone set** (for “today” / “this week” and report times): `/report_set_timezone` e.g. `America/Montreal`.
- **Optional for duplicate check**: `GEMINI_API_KEY` in `.env` enables *semantic* duplicate detection (same embeddings as note search). If unset, the bot uses normalized string match only.

---

## 1. GTD Dashboard — `/tasks_status` (US-059)

**Goal**: `/tasks_status` is a short productivity cockpit; old sync diagnostics live in `/tasks_sync_detail`.

### 1.1 Dashboard layout

1. Send `**/tasks_status`**.
2. **Check**:
  - **Overdue**: Either “✅ All clear” or a count + up to 3 titles with “X days overdue”.
  - **Today**: Tasks due today with project context, or “Nothing scheduled for today” with a nudge to `/task`.
  - **This week**: Tasks due in the next 7 days (grouped by project); if more than 5, “+N more” style truncation.
  - **Inbox**: Count of tasks with no project; if > 5, a nudge to review.
  - **System health**: One line at the bottom (e.g. “✅ Google Tasks connected · Last sync: X min ago”). Only expands to errors if there are sync issues.
  - **Empty state**: If nothing overdue and nothing due today (and inbox clear), an encouraging “on top of everything” style message with the next upcoming task if any.
3. **Response time**: Should feel fast (< 2 seconds).
4. **Timezone**: “Today” and “this week” must match your configured timezone (e.g. evening local time = next calendar day where appropriate).

### 1.2 Not connected

1. If you have a second user or a way to disconnect Google Tasks, send `**/tasks_status`** when not connected.
2. **Check**: Single friendly line prompting connection, not a long technical error.

### 1.3 Old sync diagnostics

1. Send `**/tasks_sync_detail`**.
2. **Check**: Previous sync-diagnostic content (sync counts, success/fail, recent sync times, etc.) appears here and is **not** shown in `/tasks_status`.

**Pass**: Dashboard shows the 5 sections (or empty state), one health line, and sync details only in `/tasks_sync_detail`.

---

## 2. Project Report — `/project_report` (US-060)

**Goal**: Portfolio view per project with next action, last activity, stall and “no next action” alerts; drill-down and optional weekly report section.

### 2.1 Full portfolio

1. Send `**/project_report`** (no arguments).
2. **Check**:
  - **Header**: Counts for active/blocked/planning and “no next action” (or similar); if active projects > 15, a warning.
  - **Per project**: Name, status badge (e.g. Building, Blocked, Planning), next Google Task (or “No next action” + nudge to `/task`), last activity (e.g. “2 days ago” or “⚠️ Stalled: 18 days”), note count and open task count.
  - **Needs Attention**: Stalled projects (no note update and no task completion in 14+ days) and projects with no open task are called out (e.g. “Needs Attention” section).
  - **Order**: Blocked / Stalled / Building / Planning first; completed last (e.g. collapsed).
  - **Completed**: Summary like “✅ N completed this week” without full detail.
3. **Response time**: Under a few seconds even with many projects.

### 2.2 Drill-down

1. Send `**/project_report <name>`** where `<name>` is a partial match for one project (e.g.  `/project_report learn` for “Learn to Sing Harmonies”).
2. **Check**: One project shown in full detail (all open tasks, recent notes, etc.); fuzzy match works.

### 2.3 Weekly report with project portfolio

1. Enable portfolio in weekly report: `**/report_toggle_portfolio on`**.
2. Send `**/weekly_report`** (or trigger weekly report as configured).
3. **Check**: Report includes a project portfolio section (same kind of view as `/project_report`).
4. Turn off: `**/report_toggle_portfolio off`** and run weekly report again; portfolio section should be absent.

**Pass**: Portfolio, drill-down, and optional weekly portfolio section behave as above; stall and “no next action” are visible.

---

## 3. Duplicate task check (US-055)

**Goal**: Before creating a task, the bot checks for an existing task with a *semantically similar* title (Gemini embeddings; same infrastructure as note search). If none, it falls back to normalized string match. When a duplicate is found, the bot offers Edit / Change Priority / Add Anyway / Cancel.

### 3.1 Direct `/task` flow

1. Create a task (e.g. `**/task Buy milk`**) so “Buy milk” exists in Google Tasks.
2. Send `**/task Buy milk`** again (same or very similar title).
3. **Check**: Bot does **not** create a second task immediately. It detects the duplicate (by semantic similarity when GEMINI_API_KEY is set, else by normalized string match) and shows a message with an **inline keyboard**: **Edit** | **Change Priority** | **Add Anyway** | **Cancel**.
4. **Edit**: Tap Edit; confirm you can update the existing task (e.g. notes or due date).
5. **Add Anyway**: Start a new flow that adds a second task with the same title; confirm it appears in Google Tasks.
6. **Cancel**: Dismiss without creating or changing anything.

### 3.2 Similar and normalized titles

1. Add a task `**/task Call dentist`**.
2. Try `**/task call dentist`** or `**/task Call dentist!**` — should be detected (normalized string match or semantic).
3. With semantic search (GEMINI_API_KEY set), try `**/task Call the dentist**` or `**/task Phone dentist appointment**` — the bot may treat these as duplicates if similarity is above threshold (~0.9); inline keyboard appears.

### 3.3 No duplicate

1. Send `**/task Something unique 12345**` (title that does not exist).
2. **Check**: Task is created as before, no duplicate prompt.

### 3.4 Other flows (optional)

- **Braindump**: In a braindump session, add an action that matches an existing task title; duplicate check and keyboard should appear.
- **Content routing**: Send a message that is routed to “task” or “both” and would create a task whose title matches an existing one; duplicate check and keyboard should appear.

**Pass**: Duplicate is detected on same or semantically similar title (or normalized match when Gemini is not configured); all four options work; no duplicate when title is clearly different.

---

## 4. Stoic Journal image after save (US-061)

**Goal**: After `/stoic_done`, the saved Stoic note gets a symbolic image embedded near the top.

### 4.1 New Stoic entry image

1. Run `**/stoic morning`**, answer prompts, then `**/stoic_done`**.
2. **Check**:
  - Reflection is saved as usual (no regressions).
  - Bot says it is generating an image and then confirms it was added.
  - In Joplin, the note has an embedded image near the top (no text in the image).
3. Repeat with `**/stoic evening`**.

### 4.2 Duplicate flows

1. Run `/stoic morning` twice on the same day.
2. Choose `**/stoic_replace`** and verify an image is still added/updated.
3. Choose `**/stoic_append**` and verify an image is added (and not duplicated on re-run).

### 4.3 Backfill existing notes (script)

1. Export your Joplin token and run a dry-run:
  - `export JOPLIN_TOKEN='...'`
  - `./venv/bin/python scripts/backfill_stoic_images.py --dry-run`
2. Run a small batch:
  - `./venv/bin/python scripts/backfill_stoic_images.py --limit 5`

**Pass**: Stoic notes get an image without breaking the save flow; backfill works with dry-run/limit.

---

## 4. Quick checklist


| Area             | Command / action                       | What to verify                                         |
| ---------------- | -------------------------------------- | ------------------------------------------------------ |
| GTD Dashboard    | `/tasks_status`                        | 5 sections, one health line, < 2 s                     |
| Sync diagnostics | `/tasks_sync_detail`                   | Old sync stats here only                               |
| Project report   | `/project_report`                      | Portfolio header, per-project blocks, stall/no-next    |
| Drill-down       | `/project_report <name>`               | One project, full detail                               |
| Weekly portfolio | `/report_toggle_portfolio on` + weekly | Portfolio in report; off removes it                    |
| Duplicate        | `/task <existing title>`               | Inline keyboard: Edit / Priority / Add Anyway / Cancel |
| No duplicate     | `/task <new title>`                    | Task created normally                                  |


---

## 5. Reporting issues

If something fails:

- Note **exact command** and **full bot response** (or a screenshot).
- Note **user state**: timezone, Google Tasks connected or not, number of tasks/projects.
- For defects, add a short description and paste into a new defect in the backlog (or reference an existing DEF-XXX).

---

*Sprint 20 — GTD Dashboard & Project Intelligence. Last updated: 2026-03-11.*