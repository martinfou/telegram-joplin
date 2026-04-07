---
template_version: 1.1.0
last_updated: 2026-01-24
compatible_with: [defect-fix, sprint-planning, product-backlog]
requires: [markdown-support]
---

# User Story: US-017 - GTD Expert Persona for 15-Minute Brain Dumping

**Status**: ⏳ In Progress  
**Priority**: 🟠 High  
**Story Points**: 8 (Fibonacci: 1, 2, 3, 5, 8, 13)  
**Created**: 2026-01-24  
**Updated**: 2026-01-24  
**Assigned Sprint**: Sprint 7

## Description

Implement a specialized "GTD Expert" persona for the Telegram bot based on a 15-minute "Mindsweep" methodology. This feature will guide users through a high-speed capture session to empty their heads of all "open loops"—tasks, commitments, ideas, and worries. The bot acts as a warm but brisk coach, asking punchy questions one at a time and waiting for responses without editorializing.

## User Story

As a busy and overwhelmed user, 
I want a GTD expert to guide me through a 15-minute quick capture session, 
so that I can systematically empty my brain, especially focusing on often-forgotten paperwork, and reduce my anxiety.

## Acceptance Criteria

### Session Initiation & Flow
- [ ] Bot initiates session via `/braindump` or `/capture` command.
- [ ] Bot asks ONE short, punchy question at a time and waits for user input.
- [ ] Bot acknowledges input briefly ("Got it," "Noted") to maintain momentum.
- [ ] User can skip topics by saying "nothing" or "nothing else."

### Guided Phases
The session must follow these logic phases (internal state):
1. **Pressure Release (2-3 min)**: Focus on top-of-mind stressors and overdue items.
2. **Quick Sweep (8-10 min)**: Systematic check of Work, Home, Errands, Finances, Health.
3. **Deep Dive: Paperwork**: Extra emphasis on taxes, renewals, contracts, and documents with deadlines.
4. **Stragglers (2-3 min)**: Open-ended prompts like "What else?".

### Capture & Output
- [ ] Bot processes items in real-time or batches them at the end.
- [ ] **Final Output**: A single organized list grouped by category (Work, Home, Paperwork, etc.) delivered at the end of the session.
- [ ] Items are stored in Joplin as a structured note and action items are funneled to Google Tasks.

### Tone & Persona
- [ ] Persona follows the "focused but friendly coach" model.
- [ ] Tone is warm but brisk; avoid therapy-like processing; focus on capture.

## Business Value

- High user engagement through a timed, interactive experience.
- Addresses a specific user pain point (forgetting paperwork/deadlines).
- Reduces cognitive load by providing the structure for the "Mindsweep."

## Technical Requirements

- **Stateful Conversation**: Needs a state machine or conversation manager to track session phases and question indices.
- **Timer/Session Logic**: Session should aim for ~15 minutes (or a specific set of prompts).
- **Categorization Logic**: LLM must be prompt-tuned to categorize items into predefined buckets (Work, Home, Paperwork, etc.).
- **batching**: Capture multiple entries and generate a summary note in Joplin.

## Reference Documents

- [GTD + Second Brain workflow](../../../docs/for-users/gtd-second-brain-workflow.md) (reference for capture mindset; original TCREI prompt is local/supplementary)
- [Backlog Management Process](../../docs/processes/backlog-management-process.md)

## Technical References

- Class: `ConversationState` (for tracking session state)
- File: `src/handlers/braindump.py` (brain dump handlers)
- LLM Prompt: `src/prompts/gtd_expert.txt`

## Dependencies

- US-007 (Conversation State Management) must be fully functional.
- US-006 (LLM Integration for Note Generation) must support sequential multi-turn processing.

## Notes

- The questions should be randomized or selected from a larger pool to keep the experience fresh.
- Consider adding "Triggers" (e.g., "Think about your boss", "Think about your health") to deeper the dump.

## History

- 2026-01-24 - Created
