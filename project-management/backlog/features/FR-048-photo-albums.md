# Feature Request: FR-048 - Photo OCR: Photo Albums Support

**Status**: ⭕ Not Started
**Priority**: 🟢 Low
**Story Points**: 5
**Created**: 2026-03-06
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog
**Parent**: [FR-030](FR-030-photo-ocr-capture.md) Photo OCR Capture

## Description

Telegram supports sending multiple photos at once (photo albums). Extend photo capture to handle albums: either one note per photo or one note with multiple images, depending on content/context.

## User Story

As a user who captures multiple related photos (e.g. whiteboard + close-up, receipt front + back),
I want to send them as an album and have them processed together,
so that I don't have to send each photo separately.

## Acceptance Criteria

- [ ] Detect when user sends a photo album (multiple photos in one message)
- [ ] Process each photo with OCR
- [ ] Option A: Create one note per photo (simpler)
- [ ] Option B: Create one note with multiple images when content is related (e.g. receipt front+back)
- [ ] Show progress for multi-photo processing (e.g. "Processing 2 of 5...")
- [ ] Handle partial failures (some photos succeed, some fail)

## Business Value

Extends capture modality for power users. Reduces friction when capturing multi-page documents or related images. Aligns with how users naturally share photos in Telegram.

## Dependencies

- FR-030 (Photo OCR Capture) ✅
