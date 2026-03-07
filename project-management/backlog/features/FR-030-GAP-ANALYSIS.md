# FR-030 Gap Analysis: Photo OCR Capture — Acceptance Criteria vs Implementation

**Date**: 2026-03-06  
**Updated**: 2026-03-06 — Implemented 4 missing unit tests  
**Feature**: FR-030 - Photo/Screenshot OCR Capture  
**Status**: Feature marked ✅ Completed in backlog

## Summary

| Category | Implemented | Partial | Not Done |
|----------|-------------|---------|----------|
| Core Flow | 7 | 0 | 0 |
| Unit Tests | 6 | 0 | 0 |

---

## Acceptance Criteria vs Implementation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Sending a photo triggers OCR processing | ✅ Done | `src/handlers/photo.py`: `MessageHandler(filters.PHOTO, handler)` registers; `_handle_photo` calls `extract_text_from_image(image_data)` |
| 2 | Extracted text is included in the note body | ✅ Done | `_build_photo_note_body` adds `## Extracted Text` + `text` when present (`src/handlers/photo.py:52-54`) |
| 3 | Original image is attached to the Joplin note | ✅ Done | `image_data_url = _image_bytes_to_data_url(image_data)` passed to `create_note_in_joplin` → `joplin_client.create_note(..., image_data_url=...)`. Joplin API supports `image_data_url` for note creation |
| 4 | LLM classifies/routes the content (folder, tags) based on extracted text | ✅ Done | `llm_orchestrator.process_message(synthetic_message)` with OCR text, summary, type; `note_data` from LLM includes folder, tags |
| 5 | User can add caption to photo for additional context | ✅ Done | `caption = (message.caption or "").strip()`; when present, prepended to `synthetic_message` for classification (`src/handlers/photo.py:78,102-103`) |
| 6 | Works with: screenshots, whiteboard photos, documents, handwritten notes | ✅ Done | OCR prompt requests `type` in `["document","whiteboard","handwritten","screenshot","receipt","business_card","other"]`; Gemini handles all |
| 7 | Handles photos with no text gracefully ("No text detected") | ✅ Done | OCR returns `{"text":"","type":"image","summary":"Image with no text",...}`. Note body now shows "*No text detected*" in Extracted Text section when empty; image still attached |
| 8 | Multiple photos can be sent in sequence | ✅ Done | Each photo is a separate message; handler processes one per message. No blocking; sequential processing works |
| 9 | Processing indicator shown while OCR runs | ✅ Done | `status_msg.reply_text("🔍 Processing image...")` → `edit_text("🔍 Extracting text...")` → `edit_text("🧠 Classifying content...")` → `edit_text("📝 Creating note...")` |

---

## Unit Tests (from FR-030 Testing section)

| Test | Status | Notes |
|------|--------|-------|
| Test OCR extraction (mock provider) | ✅ Done | `test_extract_parses_valid_json_response`, `test_extract_returns_none_when_no_api_key` |
| Test note creation with image attachment | ✅ Done | `test_photo_flow_passes_image_data_url_to_create_note` in `tests/test_photo_handler.py` |
| Test caption integration | ✅ Done | `test_photo_caption_included_in_synthetic_message` |
| Test no-text image handling | ✅ Done | `test_extract_returns_fallback_on_empty_text` |
| Test image download from Telegram | ✅ Done | `test_photo_download_from_telegram_passed_to_ocr` |
| Test progress indicator updates | ✅ Done | `test_photo_progress_indicator_updates` |

---

## Recommended Fixes (Priority Order)

### 1. ~~Align "no text" wording with spec~~ ✅ Done

**Criterion 7**: `_build_photo_note_body` now shows "*No text detected*" in the Extracted Text section when text is empty.

### 2. ~~Add missing unit tests~~ ✅ Done

- **Note creation with image**: `test_photo_flow_passes_image_data_url_to_create_note` — mocks `create_note_in_joplin`, asserts `image_data_url` is passed.
- **Caption integration**: `test_photo_caption_included_in_synthetic_message` — asserts synthetic message includes caption.
- **Image download**: `test_photo_download_from_telegram_passed_to_ocr` — asserts image bytes from mock Telegram download are passed to OCR.
- **Progress indicator**: `test_photo_progress_indicator_updates` — asserts status sequence: Processing → Extracting → Classifying → Creating note.

---

## Files Reviewed

| File | Role |
|------|------|
| `src/handlers/photo.py` | Photo handler, OCR flow, caption, status updates |
| `src/ocr_service.py` | Gemini OCR, no-text fallback |
| `src/handlers/core.py` | `create_note_in_joplin`, image_data_url handling |
| `src/joplin_client.py` | `create_note(image_data_url=...)` |
| `tests/test_ocr_service.py` | OCR unit tests |
| `tests/test_photo_handler.py` | Photo handler unit tests (note creation, caption, download, progress) |

---

## Conclusion

The core feature is **fully implemented**: all 9 acceptance criteria are met, and all 6 unit tests from the FR-030 spec are in place. No remaining gaps.
