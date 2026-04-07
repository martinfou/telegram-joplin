# Project Management Process State

**Purpose**: Tracks where the AI/user is in project management processes so the AI can provide contextually relevant guidance.

**Last Updated**: 2026-04-06 (idle; Sprint 21 planning doc [sprints/sprint-21-next.md](sprints/sprint-21-next.md))

---

## Current State

| Field | Value |
|-------|-------|
| **Process** | (none) |
| **Step** | (none) |
| **Context** | — |

---

## Supported Processes

When starting or continuing work, set **Process** and **Step** below. Update as you progress.

### Release Notes (`release_notes`)

**Process doc**: [docs/processes/release-notes-process.md](docs/processes/release-notes-process.md)

| Step | Description |
|------|-------------|
| 1 | Run `python scripts/generate_release_notes_draft.py` |
| 2 | Add new section to `RELEASE_NOTES.md` with today's date |
| 3 | Fill in New Features (from completed US-XXX) |
| 4 | Fill in Bug Fixes (from completed DEF-XXX) |
| 5 | Add Breaking Changes if any |
| 6 | Add Migration Notes if any |
| 7 | Commit release notes with sprint/feature commits |

### Backlog Management (`backlog_management`)

**Process doc**: [docs/processes/backlog-management-process.md](docs/processes/backlog-management-process.md)

| Step | Description |
|------|-------------|
| 1 | Create user story/defect file in `backlog/user-stories/` or `backlog/defects/` |
| 2 | Add entry to `backlog/product-backlog.md` |
| 3 | Backlog refinement (clarify, estimate, prioritize) |

### Sprint Planning (`sprint_planning`)

**Process doc**: [docs/processes/backlog-management-process.md](docs/processes/backlog-management-process.md) (Sprint Planning section)

| Step | Description |
|------|-------------|
| 0 | Run doc-code consistency review: `./scripts/doc-code-review.sh` |
| 1 | Select items from backlog |
| 2 | Add to sprint planning document |
| 3 | Update backlog status (⏳ In Progress) |

### Pre-Commit (`pre_commit`)

**Process doc**: [docs/processes/pre-commit-checklist.md](docs/processes/pre-commit-checklist.md)

| Step | Description |
|------|-------------|
| 1 | Run `ruff check src/ config.py main.py` |
| 2 | Run `mypy src/` |
| 3 | Run `pytest tests/ -v --ignore=tests/e2e` |
| 4 | Commit |

---

## How to Use (for AI)

1. **When user starts a process**: Set Process and Step in the table above. Add Context if relevant (e.g. sprint number, backlog item ID).
2. **When moving to next step**: Update Step. Optionally add a brief note in Context.
3. **When process completes**: Set Process to `(none)` and Step to `(none)`.
4. **Always read this file** when working in `project-management/` or when the user mentions release notes, backlog, sprint planning, or pre-commit.
