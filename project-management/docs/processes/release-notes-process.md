# Release Notes Process

## Overview

Release notes document changes for **users and developers** at the root of the project in `RELEASE_NOTES.md`. One entry per merge to main (or push). Date-based versioning.

**Location**: `RELEASE_NOTES.md` (project root)

## When to Update

- **Each push/merge to main** — Add a new dated section
- **End of sprint** — Review and ensure all sprint changes are documented; run the draft script

## Release Note Structure

Each release section includes:

| Section | Content |
|---------|---------|
| **New Features** | Short title, short description, link to backlog (US-XXX) |
| **Bug Fixes** | Short title, short description, link to backlog (DEF-XXX) |
| **Breaking Changes** | If any; migration steps |
| **Migration Notes** | If any; upgrade instructions |

## Format

```markdown
## YYYY-MM-DD

### New Features
- **Title** — Short description. (Link to backlog: `../backlog/user-stories/US-XXX-slug.md` from this folder.)

### Bug Fixes
- **Title** — Short description. (Link: `../backlog/defects/DEF-XXX-slug.md`.)

### Breaking Changes
- (none this release)

### Migration Notes
- (none this release)
```

## Guidelines

- **Short titles** — One line, imperative mood
- **Short descriptions** — 1–2 sentences max
- **Link to backlog** — Use relative path to the backlog item file
- **Audience** — Write for both users (what changed) and developers (technical context when relevant)

## Semi-Automation

Run the draft generator before writing:

```bash
python scripts/generate_release_notes_draft.py
```

This parses recent commits for `DEF-XXX` and `US-XXX` patterns and outputs a draft. Copy into `RELEASE_NOTES.md` and edit for clarity.

## Checklist (End of Sprint)

- [ ] Run `python scripts/generate_release_notes_draft.py`
- [ ] Add new section to `RELEASE_NOTES.md` with today's date
- [ ] Fill in New Features (from completed US-XXX)
- [ ] Fill in Bug Fixes (from completed DEF-XXX)
- [ ] Add Breaking Changes if any
- [ ] Add Migration Notes if any
- [ ] Commit release notes with the sprint/feature commits

## Example Entry

```markdown
## 2026-03-06

### New Features
- **Joplin ↔ Google Tasks project sync** — Feature request added for syncing projects with Google Tasks. [US-034](../../backlog/user-stories/US-034-joplin-google-tasks-project-sync.md)

### Bug Fixes
- **Weekly report shows 0 notes/tasks** — Fixed by requesting completed tasks and explicit Joplin timestamp fields. [DEF-018](../../backlog/defects/DEF-018-weekly-report-incorrect-numbers.md)
- **Dream analysis "Message is too long"** — Long analyses now split into multiple messages. [DEF-019](../../backlog/defects/DEF-019-dream-message-too-long.md)

### Breaking Changes
- (none this release)

### Migration Notes
- (none this release)
```

---

**Last Updated**: 2026-03-06
