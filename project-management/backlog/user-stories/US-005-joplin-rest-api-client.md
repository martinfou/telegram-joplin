# User Story: US-005 - Joplin REST API Client

**Status**: ⏳ In Progress  
**Priority**: 🟠 High  
**Story Points**: 5  
**Created**: 2026-01-20  
**Updated**: 2026-01-20  
**Assigned Sprint**: Sprint 2

## Description

Create a REST client module to abstract interactions with the Joplin Data API, including fetching tags, creating notes, applying tags, and updating the centralized log.

## User Story

As a developer, I want a reliable client to interact with Joplin's REST API so that the bot can create and manage notes programmatically.

## Acceptance Criteria

- [ ] Client can fetch existing Joplin tags
- [ ] Client can create new notes in specified folders
- [ ] Client can apply tags to notes (create tags if they don't exist)
- [ ] Client can update the AI-Decision-Log note with new entries
- [ ] Client handles API errors and timeouts gracefully
- [ ] Client includes port availability check before operations

## Business Value

Enables the bot to store notes in Joplin, which is the core functionality of the system.

## Technical Requirements

- Support both requests and httpx libraries
- Handle authentication (if needed)
- Implement retry logic for API calls
- Validate responses and handle edge cases
- Base URL: http://localhost:41184

## Reference Documents

- requirement.md - Implementation Modules, Joplin REST Client section
- requirement.md - Error Handling & Security, Port 41184 Check

## Technical References

- Class: JoplinClient
- Methods: fetch_tags(), create_note(), apply_tags(), append_log()
- File: src/joplin_client.py
- API: Joplin Data API v1

## Dependencies

- None (can be developed independently)

## Notes

The client should abstract the complexity of Joplin's API endpoints and provide clean methods for the orchestrator to use.

## History

- 2026-01-20 - Created
- 2026-01-20 - Status changed to ⏳ In Progress, Assigned to Sprint 2
