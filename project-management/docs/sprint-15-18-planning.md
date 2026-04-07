# Sprint 15–18 Planning: Feature Order & Rationale

**Date**: 2026-03-06  
**Status**: Ready for Review  
**Historical Velocity**: ~14 pts/sprint (2 weeks)  
**Definition of Done**: [definition-of-done.md](definition-of-done.md)

---

## Executive Summary

This document proposes sprint ordering for Sprints 15–18 based on:
1. **Stability first** — Fix production bugs before new features
2. **Dependency order** — Features that enable others come first
3. **Quick wins** — Small, high-impact items paired with larger work
4. **Cohesive themes** — Group related work for focus

---

## Bug Fixes (Sprint 14 & 15)

| Sprint | Bug | Description | Pts |
|--------|-----|-------------|-----|
| **Sprint 14** | DEF-017 | /dream command crashes on invocation — fix parse_mode, welcome message | 1 |
| **Sprint 15** | DEF-022 | /find command error in Fly.io — get_folders try/except, HTML escape | 2 |
| **Sprint 15** | DEF-023 | /ask command crashes on certain prompts — HTML escape, plain-text fallback | 2 |

**Total defect fix points**: 5 pts across Sprints 14–15. All three share the same root cause (Telegram Markdown parse errors); fix pattern: HTML mode + `html.escape()` + plain-text fallback.

---

## Current State

| Sprint | Status | Contents | Points |
|--------|--------|----------|--------|
| **Sprint 13** | ⏳ In Progress | DEF-007, US-036 | 13 |
| **Sprint 14** | ⏳ Planned | DEF-017 (defect), US-033 | 9 |
| **Sprint 15** | 📋 Planned | DEF-022 (defect), DEF-023 (defect), US-044, US-039 | 12 |

**Remaining unassigned bugs**: None (all high-priority bugs assigned to Sprint 14–15)

**Unassigned Features** (by proposed order):

| Order | ID | Title | Pts | Rationale |
|-------|-----|-------|-----|------------|
| 1 | US-044 | /project_new command | 5 | **Enables US-034** — Users need to create projects before syncing them |
| 2 | US-034 | Joplin ↔ Google Tasks project sync | 13 | High value; depends on project creation flow |
| 3 | US-039 | Star on task as high priority | 3 | Quick win; improves all reports |
| 4 | US-043 | Report speed + async + UI updates | 5 | Improves daily/weekly/monthly report UX |
| 5 | US-042 | Stoic "What I Learned Today" | 4 | Builds on US-019; content pipeline |
| 6 | US-040 | Check existing task/note, update/append | 8 | Reduces duplicates; uses US-026 semantic search |
| 7 | US-038 | AI Identity, User Profile, Chat History | 8 | Personalization; standalone |
| 8 | US-041 | Project mgmt: Commit style + Doc sync | 5 | Process/documentation; can slot in anytime |
| 9 | US-035 | World-class brain dump | 13 | Large enhancement; no blocking deps |

---

## Proposed Sprint Plan

### Sprint 14: Flashcard & Dream Fix (context)
**Duration**: 2026-05-05 – 2026-05-18  
**Bug Fix**: DEF-017 (1 pt) — /dream command crash  
**Feature**: US-033 (8 pts) — Flashcard practice from notes  
**Plan**: [sprint-14-flashcard-and-dream-fix.md](../sprints/sprint-14-flashcard-and-dream-fix.md)  
**Success Criteria**: /dream shows welcome without crash; /flashcard with SM-2, card extraction, session flow.

---

### Sprint 15: Stability & Project Foundation
**Duration**: 2026-05-19 – 2026-06-01 (2 weeks)  
**Target**: 12 pts  
**Plan**: [sprint-15-stability-and-project-foundation.md](../sprints/sprint-15-stability-and-project-foundation.md)  
**Implementation Guide**: [sprint-15-implementation-guide.md](../sprints/sprint-15-implementation-guide.md) — LLM-ready code snippets, file paths, patterns

**Bug Fixes** (4 pts):
| Item | Points | Rationale |
|------|--------|-----------|
| DEF-022 | 2 | /find fix — in progress; complete for production stability |
| DEF-023 | 2 | /ask fix — same Markdown parse pattern as DEF-022, DEF-017 |

**Features** (8 pts):
| Item | Points | Rationale |
|------|--------|-----------|
| US-044 | 5 | /project_new — creates projects with default folders; prerequisite for US-034 |
| US-039 | 3 | Star on task — quick win; improves reports immediately |

**Total**: 12 pts (4 defect fix + 8 feature)

**Theme**: Fix broken commands first, then establish project creation flow.

**Success Criteria**: All 4 stories done; /find and /ask work in production; /project_new creates projects; star priority in reports. See [Definition of Done](definition-of-done.md).

**Scope Reduction** (if needed): Drop US-039 → 9 pts; or drop US-044 → 7 pts (bugs + US-039 only).

---

### Sprint 16: Project Sync
**Duration**: 2026-06-02 – 2026-06-15 (2 weeks)  
**Target**: 13 pts

| Item | Points | Rationale |
|------|--------|-----------|
| US-034 | 13 | Joplin Projects ↔ Google Tasks sync — project = parent task, notes → subtasks |

**Total**: 13 pts

**Theme**: Unify Joplin project structure with Google Tasks. US-044 (project creation) done in Sprint 15.

**Success Criteria**: Project folders map to parent tasks; action items from project notes become subtasks; stalled projects flagged in reports.

**Scope Reduction**: US-034 is a single 13-pt feature; consider splitting into Phase 1 (basic sync) + Phase 2 (rename/delete, stalled detection) if needed.

---

### Sprint 17: Reports & Stoic
**Duration**: 2026-06-16 – 2026-06-29 (2 weeks)  
**Target**: 9 pts

| Item | Points | Rationale |
|------|--------|-----------|
| US-043 | 5 | Report speed + async + progress UI — improves perceived and actual performance |
| US-042 | 4 | Stoic "What I Learned Today" — content pipeline for weekly creation |

**Total**: 9 pts

**Theme**: Report UX and Stoic journal enhancement. Under velocity; buffer for spillover or US-016/US-018.

**Success Criteria**: Reports generate faster (measurable); progress messages in chat; Stoic "What I Learned" + /learnings command.

**Scope Reduction**: Drop US-042 → 5 pts (report speed only); or drop US-043 → 4 pts (Stoic only).

---

### Sprint 18: Duplicate Check & Process
**Duration**: 2026-06-30 – 2026-07-13 (2 weeks)  
**Target**: 13 pts

| Item | Points | Rationale |
|------|--------|-----------|
| US-040 | 8 | Check existing task/note, offer update/append — reduces duplicates across all flows |
| US-041 | 5 | Commit style + Document sync — process docs; complements US-036 |

**Total**: 13 pts

**Theme**: Data hygiene (duplicate detection) and project process maturity.

**Success Criteria**: Duplicate check before note/task creation; Update/Append/New flow; commit-style and document-sync process docs.

**Scope Reduction**: Drop US-041 → 8 pts (duplicate check only); or drop US-040 → 5 pts (process docs only).

---

### Sprint 19+: AI & Brain Dump
**Duration**: 2 weeks each  
**Target**: ~13 pts/sprint

| Sprint | Items | Points |
|--------|-------|--------|
| 19 | US-038 (AI Identity, User Profile, Chat History) | 8 |
| 20 | US-035 (World-class brain dump) | 13 |

---

## Dependency Graph

```
DEF-022, DEF-023 (bugs)     → Sprint 15 (stability)
        ↓
US-044 (/project_new)     → Sprint 15 (enables US-034)
        ↓
US-034 (Project sync)     → Sprint 16
        ↓
US-039 (Star)             → Sprint 15 (independent)
US-043 (Report speed)     → Sprint 17 (independent)
US-042 (Stoic learnings)  → Sprint 17 (US-019 ✅)
US-040 (Duplicate check)  → Sprint 18 (US-026 ✅)
US-038 (AI identity)     → Sprint 19 (independent)
US-041 (Process docs)     → Sprint 18 (US-036 ✅)
US-035 (Brain dump)       → Sprint 20 (independent)
```

---

## Alternative: Bug-Only Sprint 15

If production stability is **critical** and features must wait, Sprint 15 could focus exclusively on defect fixes:

| Item | Points |
|------|--------|
| DEF-022 | 2 |
| DEF-023 | 2 |

**Total**: 4 pts. US-044 and US-039 would move to Sprint 16 (alongside US-034, or Sprint 17). Use when /find and /ask are blocking users and must be fixed immediately with no feature work.

---

## Recommendation

1. **Sprint 15**: DEF-022, DEF-023, US-044, US-039 — stability + project foundation
2. **Sprint 16**: US-034 — project sync (single large feature)
3. **Sprint 17**: US-043, US-042 — reports + Stoic
4. **Sprint 18**: US-040, US-041 — duplicate check + process docs

This order ensures:
- Broken commands are fixed before new features
- Project creation exists before project sync
- Quick wins (US-039) ship early
- Report improvements and Stoic enhancement are grouped
- Duplicate detection improves data quality before AI personalization

---

## Quality Checklist (World-Class Sprint Planning)

- [x] **Clear sprint goals** — Each sprint has a measurable, outcome-focused goal
- [x] **Defect fixes prioritized** — Stability before features (Sprints 14–15)
- [x] **Dependency order** — US-044 before US-034; dependencies explicit
- [x] **Task breakdowns** — Sprint 15 has tasks per story (T-001–T-014)
- [x] **Definition of Done** — Referenced; success criteria per sprint
- [x] **Scope reduction options** — Fallback plans if velocity or capacity changes
- [x] **Dates** — Sprint 15–18 have explicit date ranges
- [x] **Pre-sprint checklist** — Doc-code review, backlog refinement

---

**Next Steps**:
1. Review and approve this plan
2. Run doc-code review before Sprint 15 kickoff
3. Create `sprint-16-project-sync.md` when Sprint 15 starts
4. Update `product-backlog.md` sprint assignments as work completes
