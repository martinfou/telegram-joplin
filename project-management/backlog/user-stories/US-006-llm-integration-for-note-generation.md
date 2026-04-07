# User Story: US-006 - LLM Integration for Note Generation

**Status**: ⏳ In Progress  
**Priority**: 🟠 High  
**Story Points**: 8  
**Created**: 2026-01-20  
**Updated**: 2026-01-20  
**Assigned Sprint**: Sprint 2

## Description

Implement the LLM orchestrator that uses structured outputs (Pydantic models) to parse user messages and generate Joplin note data, including title, body, folder, and tags.

## User Story

As a user, I want the bot to intelligently understand my messages and create appropriate notes in Joplin so that I don't have to manually specify all note details.

## Acceptance Criteria

- [ ] LLM uses Pydantic schema to enforce structured output
- [ ] LLM can determine if message needs clarification (confidence < 0.8)
- [ ] LLM generates note title, body, parent_id, and tags from message
- [ ] LLM includes log entry for decision tracking
- [ ] System prompt implements TCREI methodology
- [ ] Handles existing Joplin tags as context

## Business Value

Provides the "intelligence" component that makes the bot useful by automating note creation from natural language input.

## Technical Requirements

- Use OpenAI or LangChain with Structured Outputs
- Implement JoplinNoteSchema Pydantic model
- Response time < 10 seconds for LLM calls
- Handle API rate limits and errors
- Support context from existing tags

## Reference Documents

- requirement.md - Implementation Modules, LLM Logic section
- requirement.md - Step-by-Step Execution Plan, Prompt Engineering step

## Technical References

- Class: LLMOrchestrator
- Method: process_message()
- File: src/llm_orchestrator.py
- Schema: JoplinNoteSchema (Pydantic)

## Dependencies

- US-005: Joplin REST API Client (for tag fetching)

## Notes

The LLM component is crucial for the user experience. The TCREI prompt engineering should ensure high-quality note generation.

## History

- 2026-01-20 - Created
- 2026-01-20 - Status changed to ⏳ In Progress, Assigned to Sprint 2
