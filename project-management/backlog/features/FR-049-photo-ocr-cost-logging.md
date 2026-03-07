# Feature Request: FR-049 - Photo OCR: Cost Logging

**Status**: ⭕ Not Started
**Priority**: 🟢 Low
**Story Points**: 2
**Created**: 2026-03-06
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog
**Parent**: [FR-030](FR-030-photo-ocr-capture.md) Photo OCR Capture

## Description

Log estimated token usage for OCR calls to help with cost monitoring and optimization. Gemini API responses may include usage metadata; capture and log it.

## User Story

As a developer or operator running the bot,
I want to see estimated token usage for OCR calls in logs,
so that I can monitor costs and optimize if needed.

## Acceptance Criteria

- [ ] Extract usage metadata from Gemini API response (input_tokens, output_tokens if available)
- [ ] Log usage per OCR call (e.g. `logger.info("OCR usage: input=%d output=%d", ...)`)
- [ ] Optionally aggregate in logging service for reporting
- [ ] No PII or sensitive data in logs

## Business Value

Enables cost visibility. Helps decide if resizing, batching, or model changes are needed. Useful for multi-user or high-volume deployments.

## Dependencies

- FR-030 (Photo OCR Capture) ✅
