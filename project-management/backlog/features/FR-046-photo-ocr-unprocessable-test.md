# Feature Request: FR-046 - Photo OCR: Test for OCRUnprocessableImageError

**Status**: ⭕ Not Started
**Priority**: 🟡 Medium
**Story Points**: 1
**Created**: 2026-03-06
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog
**Parent**: [FR-030](FR-030-photo-ocr-capture.md) Photo OCR Capture

## Description

Add a unit test that mocks a 400 "Unable to process input image" response from the Gemini API and asserts the correct user-facing message is shown: "Unable to process this image. Please try a different photo (JPEG or PNG)."

## User Story

As a developer maintaining the photo OCR feature,
I want a test that verifies the unprocessable-image error path,
so that regressions are caught and the user message stays correct.

## Acceptance Criteria

- [ ] Unit test mocks `extract_text_from_image` or httpx to return 400 with "Unable to process" in body
- [ ] Test asserts `OCRUnprocessableImageError` is raised (or equivalent)
- [ ] Test asserts user receives: "Unable to process this image. Please try a different photo (JPEG or PNG)."
- [ ] Test runs in CI (not manual-only)

## Business Value

Ensures the specific Gemini 400 error path is covered. Prevents accidental changes to the user-facing message. Improves test coverage for error handling.

## Dependencies

- FR-030 (Photo OCR Capture) ✅
