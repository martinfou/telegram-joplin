"""Tests for OCR service (FR-030)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.ocr_service import (
    _mask_api_key,
    check_gemini_api_key_available,
    extract_text_from_image,
)


@pytest.mark.asyncio
async def test_extract_returns_none_when_no_api_key():
    with patch("src.ocr_service.get_settings") as mock_settings:
        mock_settings.return_value = type("Settings", (), {"google": type("G", (), {"gemini_api_key": ""})()})()
        result = await extract_text_from_image(b"fake_image_bytes")
    assert result is None


@pytest.mark.asyncio
async def test_extract_returns_fallback_on_empty_text():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(
        return_value={
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": ""}],
                    }
                }
            ]
        }
    )

    with (
        patch("src.ocr_service.get_settings") as mock_settings,
        patch("src.ocr_service.httpx.AsyncClient") as mock_client,
    ):
        mock_settings.return_value = type("Settings", (), {"google": type("G", (), {"gemini_api_key": "key123"})()})()
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)

        result = await extract_text_from_image(b"fake_bytes")

    assert result is not None
    assert result["text"] == ""
    assert result["type"] == "image"
    assert result["summary"] == "Image with no text"
    assert result["suggested_title"] == "Photo capture"


@pytest.mark.asyncio
async def test_extract_parses_valid_json_response():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(
        return_value={
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '{"text": "Hello world", "type": "document", "summary": "A doc", "suggested_title": "My Doc", "structured_data": null}',
                            }
                        ],
                    }
                }
            ]
        }
    )

    with (
        patch("src.ocr_service.get_settings") as mock_settings,
        patch("src.ocr_service.httpx.AsyncClient") as mock_client,
    ):
        mock_settings.return_value = type("Settings", (), {"google": type("G", (), {"gemini_api_key": "key123"})()})()
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_resp)

        result = await extract_text_from_image(b"fake_bytes")

    assert result is not None
    assert result["text"] == "Hello world"
    assert result["type"] == "document"
    assert result["summary"] == "A doc"
    assert result["suggested_title"] == "My Doc"
    assert result["structured_data"] is None


def test_mask_api_key():
    """Mask shows first 4 and last 4 chars, hides middle."""
    assert _mask_api_key("AIzaSyB1234567890abcdefghijk") == "AIza...hijk"
    assert _mask_api_key("short") == "(too short or empty)"
    assert _mask_api_key("") == "(too short or empty)"
    assert _mask_api_key("123456789012") == "1234...9012"


def test_gemini_api_key_available_when_configured():
    """
    Verify GEMINI_API_KEY is resolvable from settings or env.
    Run locally with .env containing GEMINI_API_KEY to verify production config.
    Skips when key not set (e.g. CI); passes and prints masked key when configured.
    """
    from src.settings import get_settings

    get_settings.cache_clear()
    available, masked_repr = check_gemini_api_key_available()
    if not available:
        pytest.skip(
            "GEMINI_API_KEY not set. Add to .env or: fly secrets set GEMINI_API_KEY=..."
        )
    assert "..." in masked_repr or len(masked_repr) > 8
    print(f"\n✓ GEMINI_API_KEY resolved: {masked_repr}")
