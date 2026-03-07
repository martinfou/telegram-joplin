# Feature Request: FR-047 - Photo OCR: Retry on Transient Failures

**Status**: ⭕ Not Started
**Priority**: 🟡 Medium
**Story Points**: 2
**Created**: 2026-03-06
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog
**Parent**: [FR-030](FR-030-photo-ocr-capture.md) Photo OCR Capture

## Description

On network timeouts or 5xx errors from the Gemini API, perform a single automatic retry before surfacing an error to the user. Reduces user frustration from transient failures.

## User Story

As a user sending a photo for OCR,
I want the bot to retry once if the API fails temporarily,
so that I don't have to resend the photo for flaky network or server errors.

## Acceptance Criteria

- [ ] On `httpx.TimeoutException` or 5xx response, retry once with short delay (e.g. 2–3 s)
- [ ] On second failure, show user-facing error as today
- [ ] Do NOT retry on 400 (unprocessable) or 429 (rate limit) — existing behavior
- [ ] Log retry attempts for debugging
- [ ] Total wait time remains reasonable (e.g. 60s timeout + one retry)

## Business Value

Improves perceived reliability. Many OCR failures are transient (network blips, Gemini overload). One retry often succeeds without user action.

## Dependencies

- FR-030 (Photo OCR Capture) ✅
