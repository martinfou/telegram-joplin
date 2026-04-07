# User Story: US-007 - Conversation State Management

**Status**: ⏳ In Progress  
**Priority**: 🟠 High  
**Story Points**: 3  
**Created**: 2026-01-20  
**Updated**: 2026-01-20  
**Assigned Sprint**: Sprint 2

## Description

Implement a state management system to track conversation context for each user, enabling the bot to ask follow-up questions and maintain context across messages.

## User Story

As a user, I want the bot to remember our conversation and ask clarifying questions so that it can create accurate notes even when my initial message is unclear.

## Acceptance Criteria

- [ ] State tracks pending notes per user
- [ ] State merges new replies with previous context
- [ ] State clears after successful note creation
- [ ] State persists across bot restarts (SQLite or similar)
- [ ] State handles multiple concurrent users
- [ ] State includes timeout for abandoned conversations

## Business Value

Enables the "talk back" functionality that improves note accuracy by allowing clarifications.

## Technical Requirements

- Support in-memory dict for simple cases
- SQLite backend for persistence
- Thread-safe for concurrent users
- Automatic cleanup of old states
- State includes message history and pending decisions

## Reference Documents

- requirement.md - Technical Implementation Plan, Stateful Orchestrator pattern
- requirement.md - Telegram Orchestrator, Context Building section

## Technical References

- Class: StateManager
- Methods: get_state(), update_state(), clear_state()
- File: src/state_manager.py

## Dependencies

- None (can be developed independently)

## Notes

Simple but important for user experience. Start with dict, upgrade to SQLite if persistence needed.

## History

- 2026-01-20 - Created
- 2026-01-20 - Status changed to ⏳ In Progress, Assigned to Sprint 2
