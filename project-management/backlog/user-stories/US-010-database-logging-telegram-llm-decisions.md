# User Story: US-010 - Database for Logging Telegram Conversations and LLM Decisions

**Status**: ⏳ In Progress  
**Priority**: 🟡 Medium  
**Story Points**: 8  
**Created**: 2025-01-27  
**Updated**: 2025-01-27  
**Assigned Sprint**: Sprint 3  

## Description

Create a database to log Telegram conversations, LLM prompts, LLM replies, and decisions made during note creation in Joplin. This will enable debugging when notes are not properly classified and provide a history of each step and decision.

## User Story

As a developer debugging the bot, 
I want a comprehensive log database of all interactions and decisions, 
so that I can trace why a note was placed in a particular folder or troubleshoot classification issues.

## Acceptance Criteria

- [ ] Database schema designed for logging Telegram messages, LLM interactions, and decisions
- [ ] Telegram conversation history stored (user messages, timestamps, user IDs)
- [ ] LLM prompts and responses logged
- [ ] Decision process logged (confidence scores, folder choices, etc.)
- [ ] API endpoints or methods to query the database for debugging
- [ ] Data retention policy implemented (e.g., keep last 30 days)
- [ ] Database migration scripts provided
- [ ] Integration with existing bot without performance impact

## Business Value

Enables effective debugging and improvement of the LLM's decision-making process. Reduces time spent troubleshooting classification errors and improves overall system reliability. Allows for analysis of patterns in misclassifications to refine the AI model.

## Technical Requirements

- Use SQLite for the database
- Implement async database operations to avoid blocking
- Include proper indexing for efficient queries
- Ensure data privacy (no sensitive user data stored)
- Database operations should be fast (< 100ms per log entry)

## Reference Documents

- LLM Orchestrator code - for understanding current logging
- Joplin Client code - for integration points
- Telegram Orchestrator code - for message handling

## Technical References

- File: `src/llm_orchestrator.py` - LLM interaction logging
- File: `src/telegram_orchestrator.py` - Message processing
- File: `src/joplin_client.py` - Note creation decisions
- Method: `LLMOrchestrator.process_message()` - Main processing method

## Dependencies

- Current logging infrastructure must be reviewed
- Database schema design completed
- No dependencies on other features

## Notes

This will replace or enhance the current AI-Decision-Log note in Joplin with a structured database. The database should allow querying by date, user, folder, etc. for debugging purposes.

## History

- 2025-01-27 - Created
- 2025-01-27 - Status changed to ⏳ In Progress, Assigned to Sprint 3</content>
<parameter name="filePath">project-management/backlog/user-stories/US-010-database-logging-telegram-llm-decisions.md
