# Sprint 21: Stoic → Tasks + health data (execution)

**Sprint Goal**: Ship **[US-063](../backlog/user-stories/US-063-stoic-session-create-google-tasks-from-top-3-prior.md)** — after Stoic completion, offer creating Google Tasks from the user’s top priorities — and **advance [US-057](../backlog/user-stories/US-057-parse-health-data-from-garmin-fatsecret-and-arbole.md)** (health parsers) as capacity allows. **[US-062](../backlog/user-stories/US-062-web-interface-for-telegram-joplin-app-laravel-vuej.md)** (web UI) stays **backlog** — too large for this two-week window unless scope is split in a later planning pass.

**Duration**: 2026-04-07 – 2026-04-20 (2 weeks)
**Status**: ⏳ In Progress
**Committed points**: 5 (US-063) + **stretch** 8 (US-057) = up to 13 if both land
**Sprint Planning Date**: 2026-04-07
**Sprint Review Date**: 2026-04-20
**Sprint Retrospective Date**: 2026-04-20

---

## Pre-sprint (done)

- [x] Documentation–code consistency review: `./scripts/doc-code-review.sh` (report: `project-management/reports/doc-code-consistency-latest.md`)
- [x] Sprint 20 pushed to `main`; backlog / this doc updated for Sprint 21

---

## Sprint backlog

| Story | Points | Role | Status |
|-------|--------|------|--------|
| US-063 | 5 | Committed | ⏳ |
| US-057 | 8 | Stretch | ⏳ |

---

## Tasks (high level)

### US-063 — Stoic session → Google Tasks

- [ ] Parse or extract “top 3” / priority lines from completed Stoic note (or session state)
- [ ] After `/stoic_done`, prompt: create tasks? (titles editable); pick list / project
- [ ] Reuse duplicate-task path where appropriate; clear errors on partial failure
- [ ] Unit tests for parsing + handler routing

### US-057 — Health parsers (stretch)

- [ ] Confirm scope for this sprint (which sources: Garmin / FatSecret / Arboleaf)
- [ ] Incremental PRs: parse → normalize → optional Joplin note or dashboard line
- [ ] Tests for sample exports or fixtures

---

## Sprint planning checklist

- [x] Sprint goal and stories selected; [product backlog](../backlog/product-backlog.md) updated (⏳, Sprint 21)
- [x] Tasks / success criteria in this file
- [x] **Current Sprint** in product backlog points here

---

**Last Updated**: 2026-04-06
