# Sprint 7: GTD Expert Persona (US-017)

**Sprint Goal**: Implement an interactive "GTD Expert" persona to guide users through 15-minute high-speed capture sessions (Mindsweep).

**Status**: ⏳ In Progress - Sprint Planning & Initial Research

**Duration**: 2026-01-24 - 2026-01-31 (1 week - Accelerated)
**Team Velocity**: 8 points (full feature)
**Sprint Planning Date**: 2026-01-24
**Sprint Start Date**: 2026-01-24
**Sprint Review Date**: 2026-01-31
**Sprint Retrospective Date**: 2026-01-31

## Sprint Overview

**Focus Areas**:
- Stateful multi-turn conversation orchestration
- Specialized "GTD Coach" persona prompt engineering
- High-speed interactive capture methodology
- Paperwork-focused deep dive phase
- Real-time Joplin note & Google Task generation
- Session summary and categorization

**Key Deliverables**:
- GTD Expert persona prompt definition
- `BrainDumpHandler` in `telegram_orchestrator.py`
- Session state management (Phase tracking)
- Final capture summary generation
- Automated Joplin note creation for "Mindsweep" results
- Integration with Google Tasks for action items

**Dependencies**:
- Conversation state management (✅ Complete - US-007)
- LLM Integration (✅ Complete - US-006)
- Joplin REST client (✅ Complete - US-005)

**Risks & Blockers**:
- Context window/memory management for long sessions (Low risk)
- LLM categorization accuracy for "Paperwork" (Medium risk - mitigated by prompt tuning)
- User engagement/momentum maintenance (Mitigated by punchy response design)

---

## User Stories

### Story 1: Interactive Mindsweep Session - 8 Points

**User Story**: As a busy and overwhelmed user, I want a GTD expert to guide me through a 15-minute quick capture session, so that I can systematically empty my brain and reduce my anxiety.

**Acceptance Criteria**:
- [ ] Bot initiates session via `/braindump` command
- [ ] Bot asks ONE short, punchy question at a time
- [ ] Session follows 4 distinct phases (Pressure Release, Quick Sweep, Deep Dive: Paperwork, Stragglers)
- [ ] Bot acknowledges input briefly to maintain momentum
- [ ] User can skip topics easily
- [ ] Final Output is a single organized Joplin note grouped by category
- [ ] Action items are automatically funneled to Google Tasks
- [ ] Persona follows "focused but friendly coach" model

**Reference Documents**:
- [US-017: GTD Expert Persona](../backlog/user-stories/US-017-gtd-expert-persona.md)
- [GTD + Second Brain workflow](../../docs/for-users/gtd-second-brain-workflow.md)

**Technical References**:
- File: `src/telegram_orchestrator.py` - Command handlers and conversation state
- File: `src/llm_orchestrator.py` - Persona switching and prompt management
- File: `src/state_manager.py` - Session persistent state

**Story Points**: 8

**Priority**: 🟠 High

**Status**: ⏳ In Progress

**Backlog Reference**: [US-017](../backlog/user-stories/US-017-gtd-expert-persona.md)

**Tasks**:

| Task ID | Task Description | Class/Method Reference | Document Reference | Status | Points | Assignee |
|---------|------------------|------------------------|---------------------|--------|--------|----------|
| T-001 | Design GTD Expert LLM Persona & Prompt | `prompts/gtd_expert.txt` | US-017 Persona | ⭕ | 1.5 | Claude Code |
| T-002 | Implement `/braindump` command & session start | `telegram_orchestrator.py` | US-017 Commands | ⭕ | 1 | Claude Code |
| T-003 | Create session state machine (4 phases) | `state_manager.py` | US-017 Logic | ⭕ | 2 | Claude Code |
| T-004 | Implement multi-turn capture handlers | `telegram_orchestrator.py` | US-017 Flow | ⭕ | 1.5 | Claude Code |
| T-005 | Implement summary generation & Joplin export | `llm_orchestrator.py` | US-017 Output | ⭕ | 1 | Claude Code |
| T-006 | Add Google Tasks integration for action items | `task_service.py` | US-017 Integration | ⭕ | 1 | Claude Code |

**Total Task Points**: 8

---

## Technical Implementation Plan

### Architecture Overview

```
User → /braindump
    ↓
telegram_orchestrator.py (Init BrainDumpState)
    ↓
state_manager.py (Track Phase: Pressure Release → Quick Sweep → Paperwork → Stragglers)
    ↓
llm_orchestrator.py (Use GTD Persona Prompt)
    ↓
Joplin / Google Tasks (Final Sync)
```

---

## Success Criteria for Sprint 7

- ✅ Users can complete a full 15-minute mindsweep without technical friction
- ✅ Note generated in Joplin is correctly categorized
- ✅ Command `/braindump` is responsive and informative
- ✅ AI maintains coach-like behavior throughout
- ✅ Paperwork items are correctly identified and emphasized

---

**Last Updated**: 2026-01-24
**Version**: 1.0
**Status**: Sprint Planning - Active Development
