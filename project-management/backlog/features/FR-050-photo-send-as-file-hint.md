# Feature Request: FR-050 - Photo OCR: "Send as File" Hint in Help

**Status**: ⭕ Not Started
**Priority**: 🟢 Low
**Story Points**: 1
**Created**: 2026-03-06
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog
**Parent**: [FR-030](FR-030-photo-ocr-capture.md) Photo OCR Capture

## Description

Add a short note in `/helpme` (and possibly in photo-related error messages) that for documents where quality matters, sending as a file instead of a photo can preserve quality. Telegram compresses photos; files are sent without compression.

## User Story

As a power user capturing documents or fine print,
I want to know that sending as a file preserves quality,
so that I can get better OCR results when needed.

## Acceptance Criteria

- [ ] Add one-line hint to `/helpme` in the photo capture section
- [ ] Example: "💡 Tip: For documents with fine print, send as file (not photo) to preserve quality."
- [ ] Optionally surface in "Unable to process" or low-quality OCR feedback
- [ ] Verify bot can handle document/file messages (or document support as separate scope)

## Business Value

Helps power users get better results without changing core behavior. Low effort, high value for users who hit quality limits.

## Dependencies

- FR-030 (Photo OCR Capture) ✅
- Note: May require document handler if bot doesn't already accept files
