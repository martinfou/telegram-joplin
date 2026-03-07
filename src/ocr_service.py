"""
OCR service using Gemini 2.5 Flash for image text extraction.

Extracts text from photos (whiteboards, documents, screenshots, handwritten notes)
and returns structured data including type classification and suggested title.
Uses GEMINI_API_KEY; if missing or request fails, returns None.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import json
import logging
import os
from collections.abc import Awaitable, Callable

import httpx

from src.settings import get_settings

logger = logging.getLogger(__name__)

# Standard multimodal model - image input, text output; 1.5/2.0-flash deprecated
_GEMINI_OCR_MODEL = "gemini-2.5-flash"
_OCR_TIMEOUT_SEC = 60.0
_OCR_STATUS_UPDATE_INTERVAL_SEC = 15.0


class OCRUnprocessableImageError(Exception):
    """Raised when Gemini returns 400 'Unable to process input image'."""

    pass


def _mask_api_key(key: str) -> str:
    """Mask API key for safe logging: show first 4 and last 4 chars, hide middle."""
    if not key or len(key) < 12:
        return "(too short or empty)"
    return f"{key[:4]}...{key[-4:]}"


def check_gemini_api_key_available() -> tuple[bool, str]:
    """
    Check if GEMINI_API_KEY is available from settings or env.
    Returns (available, masked_repr for logging).
    """
    settings = get_settings()
    api_key = settings.google.gemini_api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        return False, "N/A"
    source = "settings" if settings.google.gemini_api_key else "env"
    return True, f"{_mask_api_key(api_key)} (from {source})"
_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"
_MAX_RETRIES_429 = 2
_RETRY_DELAY_SEC = 3.0

_OCR_PROMPT = """Extract all text from this image.

Return a JSON object with:
- "text": The extracted text, preserving structure where possible
- "type": One of "document", "whiteboard", "handwritten", "screenshot", "receipt", "business_card", "other"
- "summary": A one-line summary of what this image contains
- "suggested_title": A good title for a note about this content
- "structured_data": Optional dict with extracted fields (e.g. merchant/amount/date for receipts, name/email/phone for business cards)

If no text is visible, return {"text": "", "type": "image", "summary": "Image with no text", "suggested_title": "Photo capture", "structured_data": null}"""


async def extract_text_from_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
    status_callback: Callable[[str], Awaitable[None]] | None = None,
) -> dict | None:
    """
    Extract text and classify image content using Gemini 2.5 Flash.

    Returns dict with keys: text, type, summary, suggested_title, structured_data.
    Returns None if GEMINI_API_KEY is missing or request fails.
    Raises OCRUnprocessableImageError when Gemini returns 400 "Unable to process input image".
    status_callback: optional async callable(msg) to update user during long OCR (e.g. every 15s).
    """
    settings = get_settings()
    api_key = settings.google.gemini_api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        logger.info(
            "GEMINI_API_KEY not set; skipping OCR. Set GEMINI_API_KEY in .env or environment."
        )
        return None
    logger.info("OCR using Gemini API key: %s", _mask_api_key(api_key))

    b64 = base64.b64encode(image_bytes).decode("ascii")
    url = f"{_GEMINI_BASE}/models/{_GEMINI_OCR_MODEL}:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": _OCR_PROMPT},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64,
                        }
                    },
                ]
            }
        ],
        "generationConfig": {"responseMimeType": "application/json"},
    }

    async def _do_request() -> dict:
        async with httpx.AsyncClient(timeout=_OCR_TIMEOUT_SEC) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 400:
                err_text = (resp.text or "").lower()
                if "unable to process" in err_text and "image" in err_text:
                    raise OCRUnprocessableImageError()
            if resp.status_code == 429:
                raise httpx.HTTPStatusError(
                    "429 Too Many Requests (Gemini rate limit)",
                    request=resp.request,
                    response=resp,
                )
            resp.raise_for_status()
            return resp.json()

    async def _periodic_status() -> None:
        if not status_callback:
            return
        while True:
            await asyncio.sleep(_OCR_STATUS_UPDATE_INTERVAL_SEC)
            try:
                await status_callback("⏳ Still extracting text...")
            except asyncio.CancelledError:
                raise
            except Exception:
                pass

    status_task: asyncio.Task | None = None
    if status_callback:
        status_task = asyncio.create_task(_periodic_status())

    last_exc: Exception | None = None
    data: dict | None = None
    for attempt in range(_MAX_RETRIES_429 + 1):
        try:
            data = await _do_request()
            break
        except OCRUnprocessableImageError:
            if status_task:
                status_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await status_task
            raise
        except (httpx.HTTPError, Exception) as exc:
            last_exc = exc
            exc_resp = getattr(exc, "response", None)
            if exc_resp is not None and getattr(exc_resp, "status_code", None) == 429:
                if attempt < _MAX_RETRIES_429:
                    await asyncio.sleep(_RETRY_DELAY_SEC)
                    continue
                logger.warning("Gemini rate limit (429); OCR skipped")
                return None
            err_body = ""
            if exc_resp is not None:
                with contextlib.suppress(Exception):
                    err_body = (getattr(exc_resp, "text", "") or "")[:500]
            logger.warning("OCR failed: %s%s", exc, f" | {err_body}" if err_body else "")
            return None
    else:
        if last_exc:
            logger.warning("OCR failed: %s", last_exc)
        return None

    if status_task:
        status_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await status_task

    if data is None:
        return None

    candidates = data.get("candidates") or []
    if not candidates:
        logger.warning("Gemini OCR response had no candidates")
        return None
    parts = candidates[0].get("content", {}).get("parts") or []
    if not parts:
        return None
    raw_text = parts[0].get("text", "")
    if not raw_text.strip():
        return {"text": "", "type": "image", "summary": "Image with no text", "suggested_title": "Photo capture", "structured_data": None}

    try:
        result = json.loads(raw_text)
        if not isinstance(result, dict):
            return {"text": raw_text, "type": "other", "summary": "Extracted text", "suggested_title": "Photo capture", "structured_data": None}
        result.setdefault("text", "")
        result.setdefault("type", "other")
        result.setdefault("summary", "")
        result.setdefault("suggested_title", "Photo capture")
        result.setdefault("structured_data", None)
        return result
    except json.JSONDecodeError:
        return {"text": raw_text, "type": "other", "summary": "Extracted text", "suggested_title": "Photo capture", "structured_data": None}
