"""Tests for photo handler (FR-030): note creation, caption, download, progress."""

from __future__ import annotations

import base64
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.handlers import photo as photo_module


@pytest.mark.asyncio
async def test_photo_rejects_too_large_image(mock_orch):
    """Images over 20 MB are rejected with a clear message."""
    huge = _TEST_IMAGE_BYTES * 2000  # ~2MB+ of padding; make it > 20MB
    huge = b"\xff\xd8\xff" + b"\x00" * (21 * 1024 * 1024)  # ~21 MB
    update, message, _ = _make_update_with_photo(image_bytes=huge)
    message.reply_text = AsyncMock()

    with patch("src.handlers.photo.check_whitelist", return_value=True):
        await photo_module._handle_photo(mock_orch, update, MagicMock())

    message.reply_text.assert_called_once()
    call_text = message.reply_text.call_args[0][0]
    assert "too large" in call_text.lower()
    assert "20" in call_text


@pytest.mark.asyncio
async def test_photo_rejects_too_small_image(mock_orch):
    """Images under 100 bytes are rejected with a clear message."""
    tiny = b"\xff\xd8\xff"  # 3 bytes
    update, message, _ = _make_update_with_photo(image_bytes=tiny)
    message.reply_text = AsyncMock()

    with patch("src.handlers.photo.check_whitelist", return_value=True):
        await photo_module._handle_photo(mock_orch, update, MagicMock())

    message.reply_text.assert_called_once()
    call_text = message.reply_text.call_args[0][0]
    assert "too small" in call_text.lower() or "empty" in call_text.lower()


def test_detect_image_mime():
    """MIME detection from magic bytes for Telegram photos (JPEG, PNG, WebP)."""
    assert photo_module._detect_image_mime(b"\xff\xd8\xff\xe0\x00\x10JFIF") == "image/jpeg"
    assert photo_module._detect_image_mime(b"\x89PNG\r\n\x1a\n") == "image/png"
    assert photo_module._detect_image_mime(b"RIFF\x00\x00\x00\x00WEBP") == "image/webp"
    assert photo_module._detect_image_mime(b"unknown") == "image/jpeg"  # fallback


# Standard baseline JPEG (works across decoders including Gemini) — no text, for integration test
_MINIMAL_JPEG = base64.b64decode(
    "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT"
    "/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAAAAAAAAAAAAAAD/2gAIAQEAAD8AKp//2Q=="
)

# Min size is 100 bytes; use padded JPEG header for unit tests
_TEST_IMAGE_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100


def _make_update_with_photo(
    user_id: int = 12345,
    image_bytes: bytes | None = None,
    caption: str | None = None,
) -> tuple[MagicMock, MagicMock, MagicMock]:
    """Build mock Update with photo, message, and status_msg for testing."""
    if image_bytes is None:
        image_bytes = _TEST_IMAGE_BYTES
    user = MagicMock()
    user.id = user_id

    photo_file = AsyncMock()
    photo_file.download_as_bytearray = AsyncMock(return_value=bytearray(image_bytes))

    photo = MagicMock()
    photo.get_file = AsyncMock(return_value=photo_file)

    message = AsyncMock()
    message.photo = [photo]  # photo[-1] gets largest
    message.caption = caption
    message.reply_text = AsyncMock()

    update = MagicMock()
    update.effective_user = user
    update.message = message

    return update, message, photo_file


@pytest.fixture
def mock_orch():
    """Orchestrator with mocked dependencies."""
    orch = MagicMock()
    orch.logging_service = MagicMock()
    orch.joplin_client = MagicMock()
    orch.joplin_client.get_folder = AsyncMock(return_value={"title": "Inbox"})
    return orch


@pytest.mark.asyncio
async def test_photo_flow_creates_resource_and_embeds_in_body(mock_orch):
    """create_resource is called; create_note_in_joplin receives body with ## Original Image embed."""
    update, message, _ = _make_update_with_photo()
    status_msg = AsyncMock()
    message.reply_text = AsyncMock(return_value=status_msg)
    status_msg.edit_text = AsyncMock()

    ocr_result = {
        "text": "Hello",
        "type": "document",
        "summary": "A doc",
        "suggested_title": "Test",
        "structured_data": None,
    }
    note_data = {"title": "Test", "parent_id": "folder123", "tags": []}

    mock_orch.joplin_client.create_resource = AsyncMock(return_value={"id": "res123"})

    with (
        patch("src.handlers.photo.check_whitelist", return_value=True),
        patch("src.ocr_service.extract_text_from_image", new_callable=AsyncMock, return_value=ocr_result),
        patch.object(mock_orch.llm_orchestrator, "process_message", new_callable=AsyncMock) as mock_llm,
        patch("src.handlers.core.create_note_in_joplin", new_callable=AsyncMock) as mock_create,
    ):
        mock_llm.return_value = MagicMock(status="OK", note=note_data)
        mock_create.return_value = {"note_id": "n1", "folder_id": "folder123"}

        await photo_module._handle_photo(mock_orch, update, MagicMock())

    mock_orch.joplin_client.create_resource.assert_called_once()
    mock_create.assert_called_once()
    call_args, call_kwargs = mock_create.call_args
    note_data = call_args[1]
    assert call_kwargs.get("image_data_url") is None
    body = note_data.get("body", "")
    assert "## Original Image" in body
    assert "](:/res123)" in body


@pytest.mark.asyncio
async def test_photo_caption_included_in_synthetic_message(mock_orch):
    """Caption is prepended to synthetic_message passed to LLM."""
    update, message, _ = _make_update_with_photo(caption="Meeting notes from Q1")
    status_msg = AsyncMock()
    message.reply_text = AsyncMock(return_value=status_msg)
    status_msg.edit_text = AsyncMock()

    ocr_result = {
        "text": "Extracted text",
        "type": "whiteboard",
        "summary": "Board",
        "suggested_title": "Board",
        "structured_data": None,
    }
    note_data = {"title": "Board", "parent_id": "f1", "tags": []}

    with (
        patch("src.handlers.photo.check_whitelist", return_value=True),
        patch("src.ocr_service.extract_text_from_image", new_callable=AsyncMock, return_value=ocr_result),
        patch.object(mock_orch.llm_orchestrator, "process_message", new_callable=AsyncMock) as mock_llm,
        patch("src.handlers.core.create_note_in_joplin", new_callable=AsyncMock, return_value={"note_id": "n1", "folder_id": "f1"}),
    ):
        mock_llm.return_value = MagicMock(status="OK", note=note_data)
        await photo_module._handle_photo(mock_orch, update, MagicMock())

    mock_llm.assert_called_once()
    synthetic = mock_llm.call_args[0][0]
    assert "User caption: Meeting notes from Q1" in synthetic
    assert "Extracted text" in synthetic


@pytest.mark.asyncio
async def test_photo_download_from_telegram_passed_to_ocr(mock_orch):
    """Image bytes from Telegram download are passed to extract_text_from_image."""
    image_bytes = _TEST_IMAGE_BYTES
    update, message, photo_file = _make_update_with_photo(image_bytes=image_bytes)
    status_msg = AsyncMock()
    message.reply_text = AsyncMock(return_value=status_msg)
    status_msg.edit_text = AsyncMock()

    ocr_result = {
        "text": "x",
        "type": "screenshot",
        "summary": "s",
        "suggested_title": "t",
        "structured_data": None,
    }

    with (
        patch("src.handlers.photo.check_whitelist", return_value=True),
        patch("src.ocr_service.extract_text_from_image", new_callable=AsyncMock) as mock_ocr,
        patch.object(mock_orch.llm_orchestrator, "process_message", new_callable=AsyncMock) as mock_llm,
        patch("src.handlers.core.create_note_in_joplin", new_callable=AsyncMock, return_value={"note_id": "n1", "folder_id": "f1"}),
    ):
        mock_ocr.return_value = ocr_result
        mock_llm.return_value = MagicMock(status="OK", note={"title": "t", "parent_id": "f1", "tags": []})
        await photo_module._handle_photo(mock_orch, update, MagicMock())

    mock_ocr.assert_called_once()
    assert mock_ocr.call_args[0][0] == image_bytes
    assert mock_ocr.call_args[1].get("mime_type") == "image/jpeg"


@pytest.mark.asyncio
async def test_photo_progress_indicator_updates(mock_orch):
    """Status message shows Processing → Extracting → Classifying → Creating note."""
    update, message, _ = _make_update_with_photo()
    status_msg = AsyncMock()
    message.reply_text = AsyncMock(return_value=status_msg)
    status_msg.edit_text = AsyncMock()

    ocr_result = {
        "text": "x",
        "type": "document",
        "summary": "s",
        "suggested_title": "t",
        "structured_data": None,
    }

    with (
        patch("src.handlers.photo.check_whitelist", return_value=True),
        patch("src.ocr_service.extract_text_from_image", new_callable=AsyncMock, return_value=ocr_result),
        patch.object(mock_orch.llm_orchestrator, "process_message", new_callable=AsyncMock),
        patch("src.handlers.core.create_note_in_joplin", new_callable=AsyncMock),
    ):
        mock_orch.llm_orchestrator.process_message.return_value = MagicMock(
            status="OK", note={"title": "t", "parent_id": "f1", "tags": []}
        )
        with patch("src.handlers.core.create_note_in_joplin", AsyncMock(return_value={"note_id": "n1", "folder_id": "f1"})):
            await photo_module._handle_photo(mock_orch, update, MagicMock())

    message.reply_text.assert_called_once_with("🔍 Processing image... (/photo_cancel to cancel)")
    edit_calls = [c[0][0] for c in status_msg.edit_text.call_args_list]
    assert any("🔍 Extracting text" in c for c in edit_calls)
    assert "🧠 Classifying content..." in edit_calls
    assert "📝 Creating note..." in edit_calls


@pytest.mark.asyncio
@pytest.mark.manual
async def test_photo_ocr_with_real_image():
    """
    Integration test: send real image bytes through OCR to Gemini API.
    Run manually only: pytest tests/test_photo_handler.py -m manual -v
    Skips if GEMINI_API_KEY not set. Verifies end-to-end OCR works.
    """
    from src.ocr_service import check_gemini_api_key_available, extract_text_from_image
    from src.settings import get_settings

    get_settings.cache_clear()
    available, _ = check_gemini_api_key_available()
    if not available:
        pytest.skip("GEMINI_API_KEY not set. Add to .env to run this integration test.")

    result = await extract_text_from_image(_MINIMAL_JPEG, mime_type="image/jpeg")
    assert result is not None
    assert "text" in result
    assert "type" in result
    assert "summary" in result
    assert "suggested_title" in result
    # 1x1 pixel has no text — Gemini should return empty or "image" type
    assert result["type"] in ("image", "other", "document", "screenshot", "whiteboard", "handwritten", "receipt", "business_card")
