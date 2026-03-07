# Feature Request: FR-045 - Photo OCR: Folder Quick-Reply for NEED_INFO

**Status**: ⭕ Not Started
**Priority**: 🟡 Medium
**Story Points**: 3
**Created**: 2026-03-06
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog
**Parent**: [FR-030](FR-030-photo-ocr-capture.md) Photo OCR Capture

## Description

When the LLM returns NEED_INFO and asks for a folder (e.g. "Which folder should this go in?"), offer an inline keyboard with common folders (Inbox, Projects, Resources, Areas, Archive) so users can tap instead of typing.

## User Story

As a user capturing a photo to Joplin,
I want to select a folder with one tap when the bot asks,
so that I can complete the capture faster without typing folder names.

## Acceptance Criteria

- [ ] When photo capture NEED_INFO asks for folder, show inline keyboard with common folders
- [ ] Folders: Inbox, Projects, Resources, Areas, Archive (or user's actual top-level folders)
- [ ] Tapping a button completes the flow with that folder
- [ ] User can still type a folder name if preferred
- [ ] Works for both photo capture and general note NEED_INFO flows (if applicable)

## Business Value

Reduces friction for the most common clarification. One-tap selection is faster than typing and reduces typos. Aligns with Telegram's inline keyboard UX patterns.

## Dependencies

- FR-030 (Photo OCR Capture) ✅
