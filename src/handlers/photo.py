"""
Photo message handler: OCR capture via Gemini, save to Joplin with image attachment.

Sprint 11 Story 1 - FR-030.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from src.security_utils import (
    check_whitelist,
    format_error_message,
    format_success_message,
    handle_api_error,
)
from src.timezone_utils import get_user_timezone_aware_now

if TYPE_CHECKING:
    from src.telegram_orchestrator import TelegramOrchestrator

logger = logging.getLogger(__name__)

PHOTO_OCR_PERSONA = "PHOTO_OCR"
# Pending OCR tasks (user_id -> Task). Cancellable via /photo_cancel.
_pending_photo_ocr_tasks: dict[int, asyncio.Task] = {}


def _detect_image_mime(data: bytes) -> str:
    """Detect MIME type from image magic bytes. Telegram sends JPEG, PNG, or WebP."""
    if len(data) >= 3:
        if data[:3] == b"\xff\xd8\xff":
            return "image/jpeg"
        if data[:4] == b"\x89PNG":
            return "image/png"
        if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            return "image/webp"
    return "image/jpeg"


def _image_bytes_to_data_url(data: bytes, mime_type: str | None = None) -> str:
    """Convert image bytes to data URL for Joplin."""
    if mime_type is None:
        mime_type = _detect_image_mime(data)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


_MIN_IMAGE_SIZE_BYTES = 100
_MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB
_PHOTO_OCR_STATE_EXPIRY_HOURS = 24


def _is_photo_ocr_state_expired(orch: TelegramOrchestrator, user_id: int) -> bool:
    """Return True if PHOTO_OCR state is older than expiry (24h)."""
    updated_at = orch.state_manager.get_state_updated_at(user_id)
    if not updated_at:
        return True
    try:
        # SQLite format: "YYYY-MM-DD HH:MM:SS"
        dt = datetime.strptime(updated_at.replace("Z", ""), "%Y-%m-%d %H:%M:%S")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        age_hours = (datetime.now(UTC) - dt).total_seconds() / 3600
        return age_hours >= _PHOTO_OCR_STATE_EXPIRY_HOURS
    except (ValueError, TypeError):
        return False


def _build_photo_note_body(
    ocr_result: dict, user_id: int, orch: TelegramOrchestrator, resource_id: str | None = None
) -> str:
    """Build note body from OCR result. Optionally append ## Original Image with embedded resource."""
    now = get_user_timezone_aware_now(user_id, orch.logging_service)
    date_str = now.strftime("%Y-%m-%d")
    text = (ocr_result.get("text") or "").strip()
    summary = (ocr_result.get("summary") or "").strip()
    img_type = (ocr_result.get("type") or "other").replace("_", " ").title()
    structured = ocr_result.get("structured_data")

    lines = [
        "📷 *Captured from photo*",
        "",
        f"**Type:** {img_type}",
        "",
    ]
    if summary:
        lines.extend(["**Summary:**", summary, ""])
    lines.extend(["## Extracted Text", ""])
    if text:
        lines.append(text)
    else:
        lines.append("*No text detected*")
    lines.append("")
    if structured and isinstance(structured, dict):
        lines.append("## Structured Data")
        for k, v in structured.items():
            if v is not None and str(v).strip():
                lines.append(f"- **{k}:** {v}")
        lines.append("")
    if resource_id:
        lines.append("## Original Image")
        lines.append("")
        lines.append(f"![Captured image](:/{resource_id})")
        lines.append("")
    lines.append("---")
    lines.append(f"*Captured via photo on {date_str}*")
    return "\n".join(lines)


def _data_url_to_filename(mime_type: str) -> str:
    """Return a sensible filename for the given MIME type."""
    ext = "jpg"
    if "png" in mime_type:
        ext = "png"
    elif "webp" in mime_type:
        ext = "webp"
    return f"capture.{ext}"


async def _handle_photo(orch: TelegramOrchestrator, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process photo: OCR, classify, create note with image."""
    user = update.effective_user
    message = update.message
    if not user or not message or not message.photo:
        return

    user_id = user.id
    if not check_whitelist(user_id):
        await message.reply_text("❌ Sorry, you're not authorized to use this bot.")
        return

    # US-057: health screenshot → OCR → same parse path as paste (caption /health_import or pending)
    from src.handlers.health import try_health_import_from_photo

    if await try_health_import_from_photo(orch, update, context):
        return

    caption = (message.caption or "").strip()
    photo = message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = await photo_file.download_as_bytearray()
    image_data = bytes(image_bytes)
    mime_type = _detect_image_mime(image_data)

    if len(image_data) < _MIN_IMAGE_SIZE_BYTES:
        await message.reply_text(
            format_error_message(
                "Image is too small or empty. Please send a valid photo (JPEG, PNG, or WebP)."
            )
        )
        return

    if len(image_data) > _MAX_IMAGE_SIZE_BYTES:
        size_mb = len(image_data) / (1024 * 1024)
        await message.reply_text(
            format_error_message(
                f"Image is too large ({size_mb:.1f} MB). Maximum size is 20 MB. "
                "Try a smaller or compressed photo."
            )
        )
        return

    logger.info("Photo capture: image_size_bytes=%d", len(image_data))

    status_msg = await message.reply_text("🔍 Processing image... (/photo_cancel to cancel)")
    t0 = time.monotonic()
    try:
        await status_msg.edit_text("🔍 Extracting text... (/photo_cancel to cancel)")

        async def _status_cb(msg: str) -> None:
            await status_msg.edit_text(msg)

        from src.ocr_service import extract_text_from_image

        async def _run_ocr() -> dict | None:
            return await extract_text_from_image(
                image_data, mime_type=mime_type, status_callback=_status_cb
            )

        ocr_task = asyncio.create_task(_run_ocr())
        _pending_photo_ocr_tasks[user_id] = ocr_task
        try:
            ocr_result = await ocr_task
        finally:
            _pending_photo_ocr_tasks.pop(user_id, None)
        ocr_time_ms = int((time.monotonic() - t0) * 1000)
        logger.info("Photo capture: image_size_bytes=%d, ocr_time_ms=%d", len(image_data), ocr_time_ms)

        if not ocr_result:
            await status_msg.edit_text(
                "❌ OCR failed. Set GEMINI_API_KEY in .env to enable photo capture. "
                "If already set, try a clearer photo (JPEG or PNG)."
            )
            return

        await status_msg.edit_text("🧠 Classifying content...")
        synthetic_message = (
            f"[Photo capture - {ocr_result.get('type', 'image')}]\n\n"
            f"Summary: {ocr_result.get('summary', '')}\n\n"
            f"Extracted text:\n{ocr_result.get('text', '')}"
        )
        if caption:
            synthetic_message = f"User caption: {caption}\n\n{synthetic_message}"

        llm_response = await orch.llm_orchestrator.process_message(synthetic_message)
        if not llm_response or llm_response.status == "ERROR":
            await status_msg.edit_text(
                format_error_message("Could not classify the image content. Please try again.")
            )
            return
        if llm_response.status == "NEED_INFO" and llm_response.question:
            image_data_url = _image_bytes_to_data_url(image_data, mime_type)

            # US-045: fetch top folders for quick-reply keyboard
            folder_choices: list[dict] = []
            try:
                all_folders = await orch.joplin_client.get_folders()
                folder_choices = [f for f in all_folders if f.get("title")][:8]
            except Exception:
                pass

            orch.state_manager.update_state(
                user_id,
                {
                    "active_persona": PHOTO_OCR_PERSONA,
                    "ocr_result": ocr_result,
                    "synthetic_message": synthetic_message,
                    "image_data_url": image_data_url,
                    "mime_type": mime_type,
                    "caption": caption,
                    "folder_choices": folder_choices,
                },
            )

            reply_markup = None
            if folder_choices:
                keyboard = [
                    [InlineKeyboardButton(f"📁 {f['title']}", callback_data=f"photo_folder_{i}")]
                    for i, f in enumerate(folder_choices)
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

            await status_msg.edit_text(f"🤔 {llm_response.question}", reply_markup=reply_markup)
            return

        note_data = llm_response.note
        if not note_data:
            await status_msg.edit_text(format_error_message("No note data from classifier."))
            return

        title = (note_data.get("title") or ocr_result.get("suggested_title") or "Photo capture").strip()

        await status_msg.edit_text("📝 Creating note...")
        t1 = time.monotonic()
        resource_id: str | None = None
        try:
            resource = await orch.joplin_client.create_resource(
                image_data,
                filename=_data_url_to_filename(mime_type),
                mime_type=mime_type,
            )
            resource_id = resource.get("id")
        except Exception as exc:
            logger.warning("Failed to create image resource: %s", exc)

        body = _build_photo_note_body(ocr_result, user_id, orch, resource_id=resource_id)
        note_data = dict(note_data)
        note_data["title"] = title
        note_data["body"] = body

        from src.handlers.core import create_note_in_joplin

        result = await create_note_in_joplin(
            orch,
            note_data,
            url_context=None,
            message=status_msg,
            image_data_url=None,
        )
        upload_time_ms = int((time.monotonic() - t1) * 1000)
        logger.info(
            "Photo capture: image_size_bytes=%d, ocr_time_ms=%d, upload_time_ms=%d",
            len(image_data),
            ocr_time_ms,
            upload_time_ms,
        )

        if result and "error" not in result:
            from src.handlers.core import _schedule_joplin_sync

            _schedule_joplin_sync()
            folder_id = result.get("folder_id", "")
            folder_name = ""
            if folder_id:
                try:
                    folder = await orch.joplin_client.get_folder(folder_id)
                    folder_name = folder.get("title", "")
                except Exception:
                    pass
            img_type = (ocr_result.get("type") or "image").replace("_", " ").title()
            success_text = f"Saved: {title}\n📁 {folder_name or 'Joplin'}\n📷 {img_type} captured"
            if resource_id:
                success_text += "\n\nIf the image doesn't show, run /sync then sync in Joplin."
            await status_msg.edit_text(format_success_message(success_text))
        elif result and result.get("error") == "folder_not_found":
            await status_msg.edit_text(
                format_error_message(
                    "Could not find folder. Try specifying a folder name in the caption."
                )
            )
        else:
            await status_msg.edit_text(format_error_message("Failed to create note in Joplin."))
    except asyncio.CancelledError:
        _pending_photo_ocr_tasks.pop(user_id, None)
        await status_msg.edit_text("❌ Photo capture cancelled.")
    except Exception as exc:
        _pending_photo_ocr_tasks.pop(user_id, None)
        from src.ocr_service import OCRUnprocessableImageError

        if isinstance(exc, OCRUnprocessableImageError):
            await status_msg.edit_text(
                format_error_message(
                    "Unable to process this image. Please try a different photo (JPEG or PNG)."
                )
            )
        else:
            logger.error("Photo capture failed: %s", exc, exc_info=True)
            await status_msg.edit_text(format_error_message(handle_api_error(exc, "photo capture")))


async def handle_photo_message(
    orch: TelegramOrchestrator, user_id: int, text: str, message: Any
) -> None:
    """Handle user reply when photo capture is in NEED_INFO state."""
    state = orch.state_manager.get_state(user_id)
    if not state or state.get("active_persona") != PHOTO_OCR_PERSONA:
        orch.state_manager.clear_state(user_id)
        return

    if _is_photo_ocr_state_expired(orch, user_id):
        orch.state_manager.clear_state(user_id)
        await message.reply_text(
            format_error_message(
                "Photo capture session expired (24h limit). Please send the photo again."
            )
        )
        return

    ocr_result = state.get("ocr_result")
    synthetic_message = state.get("synthetic_message", "")
    image_data_url = state.get("image_data_url")
    mime_type = state.get("mime_type", "image/jpeg")

    if not ocr_result or not image_data_url:
        orch.state_manager.clear_state(user_id)
        await message.reply_text(format_error_message("Photo capture session expired. Please send the photo again."))
        return

    image_data = b""
    if "," in image_data_url:
        try:
            _, b64 = image_data_url.split(",", 1)
            image_data = base64.b64decode(b64)
        except Exception:
            pass

    combined = f"{synthetic_message}\n\nUser reply: {text.strip()}"
    llm_response = await orch.llm_orchestrator.process_message(combined)

    if not llm_response or llm_response.status == "ERROR":
        await message.reply_text(
            format_error_message("Could not classify the image content. Please try again.")
        )
        return

    if llm_response.status == "NEED_INFO" and llm_response.question:
        orch.state_manager.update_state(user_id, {**state, "synthetic_message": combined})
        await message.reply_text(f"🤔 {llm_response.question}")
        return

    note_data = llm_response.note
    if not note_data:
        orch.state_manager.clear_state(user_id)
        await message.reply_text(format_error_message("No note data from classifier."))
        return

    orch.state_manager.clear_state(user_id)
    status_msg = await message.reply_text("📝 Creating note...")

    title = (note_data.get("title") or ocr_result.get("suggested_title") or "Photo capture").strip()
    resource_id: str | None = None
    if image_data:
        try:
            resource = await orch.joplin_client.create_resource(
                image_data,
                filename=_data_url_to_filename(mime_type),
                mime_type=mime_type,
            )
            resource_id = resource.get("id")
        except Exception as exc:
            logger.warning("Failed to create image resource: %s", exc)

    body = _build_photo_note_body(ocr_result, user_id, orch, resource_id=resource_id)
    note_data = dict(note_data)
    note_data["title"] = title
    note_data["body"] = body

    from src.handlers.core import create_note_in_joplin

    result = await create_note_in_joplin(
        orch, note_data, url_context=None, message=status_msg, image_data_url=None
    )

    if result and "error" not in result:
        from src.handlers.core import _schedule_joplin_sync

        _schedule_joplin_sync()
        folder_id = result.get("folder_id", "")
        folder_name = ""
        if folder_id:
            try:
                folder = await orch.joplin_client.get_folder(folder_id)
                folder_name = folder.get("title", "")
            except Exception:
                pass
        img_type = (ocr_result.get("type") or "image").replace("_", " ").title()
        success_text = f"Saved: {title}\n📁 {folder_name or 'Joplin'}\n📷 {img_type} captured"
        if resource_id:
            success_text += "\n\nIf the image doesn't show, run /sync then sync in Joplin."
        await status_msg.edit_text(format_success_message(success_text))
    elif result and result.get("error") == "folder_not_found":
        await status_msg.edit_text(
            format_error_message(
                "Could not find folder. Try specifying a folder name in your reply."
            )
        )
    else:
        await status_msg.edit_text(format_error_message("Failed to create note in Joplin."))


def _photo_folder_callback(orch: TelegramOrchestrator):
    """US-045: Handle inline folder selection for photo OCR NEED_INFO."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query or not query.data:
            return
        await query.answer()
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        state = orch.state_manager.get_state(user.id)
        if not state or state.get("active_persona") != PHOTO_OCR_PERSONA:
            await query.edit_message_text("❌ Session expired. Send the photo again.")
            return

        folder_choices = state.get("folder_choices", [])
        try:
            idx = int(query.data.split("_")[-1])
            folder = folder_choices[idx]
        except (ValueError, IndexError):
            await query.edit_message_text("❌ Invalid selection. Send the photo again.")
            return

        folder_name = folder.get("title", "")
        await query.edit_message_text(f"📁 Saving to {folder_name}...")
        await handle_photo_message(orch, user.id, f"Save to {folder_name}", query.message)

    return handler


def register_photo_handlers(application: Any, orch: TelegramOrchestrator) -> None:
    """Register photo message handler and /photo_cancel."""
    from src.ocr_service import check_gemini_api_key_available

    available, masked_repr = check_gemini_api_key_available()
    if available:
        logger.info("Photo OCR enabled: GEMINI_API_KEY %s", masked_repr)
    else:
        logger.warning(
            "Photo OCR disabled: GEMINI_API_KEY not set. "
            "Set in .env or fly secrets set GEMINI_API_KEY=..."
        )

    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_photo(orch, update, context)

    async def photo_cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Cancel in-progress photo OCR."""
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        task = _pending_photo_ocr_tasks.pop(user.id, None)
        if task and not task.done():
            task.cancel()
            await msg.reply_text("❌ Photo capture cancelled.")
        else:
            # Also clear NEED_INFO state if user was waiting to reply
            state = orch.state_manager.get_state(user.id)
            if state and state.get("active_persona") == PHOTO_OCR_PERSONA:
                orch.state_manager.clear_state(user.id)
                await msg.reply_text("Photo capture session cancelled. Send a new photo to start fresh.")
            else:
                await msg.reply_text("No active photo capture to cancel.")

    application.add_handler(MessageHandler(filters.PHOTO, handler))
    application.add_handler(CommandHandler("photo_cancel", photo_cancel_cmd))
    application.add_handler(CallbackQueryHandler(_photo_folder_callback(orch), pattern="^photo_folder_"))
    logger.info("Photo handlers registered")
