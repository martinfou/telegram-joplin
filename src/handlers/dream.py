"""
Dream analysis handlers: /dream, /dream_done, /dream_cancel.

Guided flow: user describes a dream, chooses a framework (Jungian, Gestalt, Adlerian),
then receives an interpretation, optional life links, and Joplin save.
Sprint 11 Story 3 - FR-025.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import logging
import re
from io import BytesIO
from typing import TYPE_CHECKING, Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

from src.handlers.core import _schedule_joplin_sync
from src.security_utils import check_whitelist, format_error_message, split_message_for_telegram
from src.timezone_utils import get_user_timezone_aware_now

if TYPE_CHECKING:
    from src.telegram_orchestrator import TelegramOrchestrator

logger = logging.getLogger(__name__)

# Pending image generation tasks (user_id -> Task). Not persisted in state.
_pending_dream_image_tasks: dict[int, asyncio.Task] = {}

DREAM_JOURNAL_PATH = ["01 - Areas", "📓 Journaling", "Dream Journal"]

# Second tag for search (first tag is always dream-journal)
_FRAMEWORK_JOPLIN_TAGS: dict[str, str] = {
    "jungian": "jungian",
    "gestalt": "gestalt",
    "adlerian": "adlerian",
}

DREAM_DISCLAIMER = (
    "\n\n🌙 *Note: This analysis is for self-reflection and personal growth. "
    "It is not a substitute for professional psychological support. "
    "If your dreams are causing distress, please consult a qualified therapist.*"
)

DREAM_FRAMEWORK_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Jungian", callback_data="dream_fw_jungian"),
            InlineKeyboardButton("Gestalt", callback_data="dream_fw_gestalt"),
        ],
        [
            InlineKeyboardButton("Adlerian", callback_data="dream_fw_adlerian"),
        ],
    ]
)


def _framework_display_name(key: str) -> str:
    return {
        "jungian": "Jungian",
        "gestalt": "Gestalt (Perls)",
        "adlerian": "Adlerian",
    }.get(key, key)


def _persona_for_framework(key: str) -> str:
    return {
        "jungian": "jungian_analyst",
        "gestalt": "dream_gestalt",
        "adlerian": "dream_adlerian",
    }[key]


def _parse_framework_from_user_text(text_lower: str) -> str | None:
    t = text_lower.strip()
    if t in ("jungian", "jung"):
        return "jungian"
    if t in ("gestalt", "perls"):
        return "gestalt"
    if t in ("adlerian", "adler"):
        return "adlerian"
    return None


def _analysis_user_prompt(dream_text: str, key: str) -> str:
    """User message sent to the LLM for the dream text (framework-specific)."""
    if key == "jungian":
        return (
            f"Analyze this dream from a Jungian perspective. "
            f"Provide: Key Symbols, Archetypes Present, Shadow Elements, Overall Theme.\n\n"
            f"Dream:\n{dream_text}\n\n"
            f"At the very end of your response, add exactly one line:\n"
            f"**Dream Title:** [a short, clever 3-7 word phrase that captures the dream's essence]"
        )
    if key == "gestalt":
        return (
            f"Analyze this dream using your Gestalt / Perls instructions.\n\n"
            f"Dream:\n{dream_text}\n\n"
            f"At the very end of your response, add exactly one line:\n"
            f"**Dream Title:** [a short, clever 3-7 word phrase that captures the dream's essence]"
        )
    if key == "adlerian":
        return (
            f"Analyze this dream using your Adlerian / Individual Psychology instructions.\n\n"
            f"Dream:\n{dream_text}\n\n"
            f"At the very end of your response, add exactly one line:\n"
            f"**Dream Title:** [a short, clever 3-7 word phrase that captures the dream's essence]"
        )
    raise ValueError(f"Unknown framework: {key}")


def _strip_dream_title_from_analysis(analysis_text: str) -> str:
    """Remove the Dream Title line from analysis so it's not duplicated in the note body."""
    return re.sub(
        r"\n*\*\*Dream Title:\*\*[^\n]*(?:\n|$)",
        "\n",
        analysis_text,
        flags=re.IGNORECASE,
    ).strip()


def _extract_dream_title(analysis_text: str, dream_text: str) -> str:
    """Extract short clever title from analysis, or derive from dream text."""
    # Look for **Dream Title:** or Dream Title: followed by the title
    match = re.search(
        r"\*\*Dream Title:\*\*\s*(.+?)(?:\n|$)",
        analysis_text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        match = re.search(r"Dream Title:\s*(.+?)(?:\n|$)", analysis_text, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        # Remove markdown, limit length
        title = re.sub(r"\*+", "", title).strip()
        if len(title) <= 60:
            return title
    # Fallback: first ~40 chars of dream, cleaned
    first_line = dream_text.split("\n")[0].strip()[:50]
    return first_line + "…" if len(first_line) >= 50 else first_line or "Dream"


def _extract_symbols_from_analysis(analysis_text: str) -> list[str]:
    """Extract symbol names from Key Symbols section (• Symbol - Interpretation)."""
    symbols: list[str] = []
    in_section = False
    for line in analysis_text.splitlines():
        line = line.strip()
        if "**Key Symbols:**" in line or "Key Symbols:" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("**") and ":" in line:
                break
            if line.startswith("•") or line.startswith("-"):
                part = line.lstrip("•- ").split(" - ", 1)[0].strip()
                if part and len(part) < 80:
                    symbols.append(part)
    return symbols[:5]


def _build_dream_note_body(
    dream_text: str,
    analysis: str,
    associations: str,
    resource_id: str | None,
    user_id: int,
    orch: TelegramOrchestrator,
    framework_heading: str = "Jungian",
) -> str:
    """Build dream journal note body. Image goes right after title (at top)."""
    lines: list[str] = []
    # Image first, right after the note title
    if resource_id:
        lines.extend([
            "![Dream symbolic image](:/" + resource_id + ")",
            "",
        ])
    lines.extend(
        [
            "## The Dream",
            "",
            dream_text,
            "",
            f"## {framework_heading} analysis",
            "",
            analysis,
            "",
        ]
    )
    if associations:
        lines.extend(["## Life Associations", "", associations, ""])
    lines.extend(["---", "*AI-assisted dream reflection.*"])
    return "\n".join(lines)


async def _run_dream_interpretation(
    orch: TelegramOrchestrator,
    user_id: int,
    message: Any,
    dream_text: str,
    framework_key: str,
) -> None:
    """Run LLM analysis + background symbolic image; send results and move to association_prompt."""
    state = orch.state_manager.get_state(user_id) or {}
    state["dream_framework"] = framework_key
    state["phase"] = "analyzing"
    orch.state_manager.update_state(user_id, state)
    display = _framework_display_name(framework_key)
    logger.info(
        "Dream: user=%d starting analysis (framework=%s, dream len=%d)",
        user_id,
        framework_key,
        len(dream_text),
    )

    status_msg = await message.reply_text(
        f"🔮 Analyzing your dream ({display})... This may take 30–60 seconds."
    )
    from src.dream_image import generate_dream_image

    async def _send_progress_updates() -> None:
        updates = [
            (15, f"📖 Reading your dream ({display})..."),
            (30, "🔍 Shaping the interpretation..."),
            (45, "🎨 Almost done, preparing your analysis..."),
        ]
        for delay, progress_text in updates:
            await asyncio.sleep(delay)
            try:
                await message.chat.send_action("typing")
                await status_msg.edit_text(progress_text)
            except Exception:
                pass

    analysis_prompt = _analysis_user_prompt(dream_text, framework_key)
    persona = _persona_for_framework(framework_key)
    analysis_response = None
    progress_task = asyncio.create_task(_send_progress_updates())
    try:
        analysis_response = await orch.llm_orchestrator.process_message(
            analysis_prompt,
            persona=persona,
        )
    except Exception as exc:
        progress_task.cancel()
        logger.error("Dream analysis LLM failed: %s", exc)
        state = orch.state_manager.get_state(user_id) or {}
        state["phase"] = "framework_choice"
        orch.state_manager.update_state(user_id, state)
        await message.reply_text(format_error_message("Analysis failed. Please try another framework or try again."))
        return
    finally:
        progress_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await progress_task

    with contextlib.suppress(Exception):
        await status_msg.edit_text("📖 Preparing your analysis...")

    analysis = ""
    if analysis_response and analysis_response.question:
        analysis = analysis_response.question
    elif analysis_response and analysis_response.note and analysis_response.note.get("body"):
        analysis = analysis_response.note["body"]
    if not analysis:
        analysis = "Analysis could not be generated. Please try again with more detail."

    state = orch.state_manager.get_state(user_id) or {}
    state["interpretation"] = analysis
    symbols = _extract_symbols_from_analysis(analysis)
    symbols = symbols or ["dream", "symbol", "unconscious"]

    state["dream_image_url"] = None
    state["phase"] = "association_prompt"
    orch.state_manager.update_state(user_id, state)

    async def _generate_and_send_image() -> None:
        try:
            image_url = await generate_dream_image(dream_text, symbols)
            st = orch.state_manager.get_state(user_id) or {}
            st["dream_image_url"] = image_url
            orch.state_manager.update_state(user_id, st)
            if image_url:
                try:
                    data = image_url.split(",", 1)[1] if "," in image_url else ""
                    if data:
                        image_bytes = base64.b64decode(data)
                        await message.reply_photo(photo=BytesIO(image_bytes))
                except Exception as exc:
                    logger.warning("Failed to send dream image: %s", exc)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.warning("Dream image generation failed: %s", exc)
        finally:
            _pending_dream_image_tasks.pop(user_id, None)

    _pending_dream_image_tasks[user_id] = asyncio.create_task(_generate_and_send_image())

    msg = f"📖 {display} analysis\n\n{analysis}\n\n---\n\n"
    msg += "Would you like to explore how this dream connects to your current life? (yes/no)"
    msg += DREAM_DISCLAIMER
    for chunk in split_message_for_telegram(msg):
        await message.reply_text(chunk)
    await message.reply_text("🎨 Creating your symbolic image... (will arrive shortly)")
    logger.info("Dream: user=%d analysis sent, image generating in background", user_id)


async def handle_dream_message(
    orch: TelegramOrchestrator,
    user_id: int,
    text: str,
    message: Any,
) -> None:
    """Handle incoming message when user is in DREAM_ANALYST session."""
    logger.debug("Dream message: user=%d phase=checking", user_id)
    state = orch.state_manager.get_state(user_id)
    if not state or state.get("active_persona") != "DREAM_ANALYST":
        return

    phase = state.get("phase", "dream_description")
    logger.debug("Dream message: user=%d phase=%s len=%d", user_id, phase, len(text or ""))
    text_lower = text.strip().lower()

    if phase == "dream_description":
        if len(text.strip()) < 20:
            await message.reply_text(
                "Please share more detail about your dream. "
                "The richer your description, the more meaningful the analysis. "
                "What happened? Who was there? What did you see, hear, feel?"
            )
            return

        state["dream_text"] = text.strip()
        state["phase"] = "framework_choice"
        state["dream_framework"] = ""
        orch.state_manager.update_state(user_id, state)
        logger.info("Dream: user=%d dream captured, awaiting framework (len=%d)", user_id, len(text.strip()))
        await message.reply_text(
            "Which dream framework should I use for the interpretation?\n\n"
            "• Jungian — symbols, archetypes, shadow, compensation\n"
            "• Gestalt (Perls) — figures as parts of you; experiments and dialogue\n"
            "• Adlerian — life goals, striving, social interest, rehearsal\n\n"
            "Tap a button, or type: jungian, gestalt, or adlerian.",
            reply_markup=DREAM_FRAMEWORK_KEYBOARD,
        )
        return

    if phase == "framework_choice":
        fw = _parse_framework_from_user_text(text_lower)
        if not fw:
            await message.reply_text(
                "Please choose a framework with the buttons, or type: "
                "jungian, gestalt, or adlerian."
            )
            return
        dream_text = (state.get("dream_text") or "").strip()
        if not dream_text:
            state["phase"] = "dream_description"
            orch.state_manager.update_state(user_id, state)
            await message.reply_text("I lost the dream text. Please describe your dream again.")
            return
        await _run_dream_interpretation(orch, user_id, message, dream_text, fw)
        return

    if phase == "association_prompt":
        if text_lower in ("yes", "y"):
            state["phase"] = "association"
            orch.state_manager.update_state(user_id, state)
            await message.reply_text(
                "Let's connect this dream to your waking life.\n\n"
                "🔮 Reflection Questions:\n\n"
                "1. What current situation in your life feels similar to something in the dream?\n"
                "2. Which part of the analysis (image, figure, or theme) resonates most with you right now?\n"
                "3. Is there something you're avoiding or seeking that the dream might point to?\n\n"
                "Take your time. Share what resonates. When you're done, type /dream_done to save."
            )
        elif text_lower in ("no", "n"):
            state["phase"] = "ready_to_save"
            state["associations"] = ""
            orch.state_manager.update_state(user_id, state)
            await message.reply_text(
                "No problem. Type /dream_done when you're ready to save this analysis."
            )
        else:
            await message.reply_text("Please reply with yes or no.")

        return

    if phase == "association":
        state["associations"] = state.get("associations", "") + "\n\n" + text.strip()
        state["phase"] = "ready_to_save"
        orch.state_manager.update_state(user_id, state)
        await message.reply_text(
            "Thank you for sharing. Type /dream_done to save this analysis to your Dream Journal."
        )


async def _save_dream_to_joplin(orch: TelegramOrchestrator, user_id: int, state: dict) -> bool:
    """Save dream analysis to Joplin. Returns True on success."""
    # If image is still generating, wait up to 15s for it
    task = _pending_dream_image_tasks.get(user_id)
    if task and not task.done():
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=15.0)
            state = orch.state_manager.get_state(user_id) or state
        except TimeoutError:
            logger.debug("Dream image still generating at save time; saving without image")
    _pending_dream_image_tasks.pop(user_id, None)

    dream_text = state.get("dream_text", "")
    interpretation = state.get("interpretation", "")
    associations = state.get("associations", "").strip()
    image_url = state.get("dream_image_url")

    if not dream_text or not interpretation:
        return False

    resource_id: str | None = None
    if image_url and "," in image_url:
        try:
            header, b64_data = image_url.split(",", 1)
            mime = "image/png"
            if "image/" in header:
                mime = header.split(":", 1)[1].split(";", 1)[0].strip()
            image_bytes = base64.b64decode(b64_data)
            resource = await orch.joplin_client.create_resource(
                image_bytes,
                filename="dream_symbolic.png",
                mime_type=mime,
            )
            resource_id = resource.get("id")
        except Exception as exc:
            logger.warning("Failed to create dream image resource: %s", exc)

    now = get_user_timezone_aware_now(user_id, orch.logging_service)
    date_str = now.strftime("%Y-%m-%d")
    dream_title = _extract_dream_title(interpretation, dream_text)
    interpretation_clean = _strip_dream_title_from_analysis(interpretation)
    title = f"{date_str} - {dream_title}"

    fw = state.get("dream_framework") or "jungian"
    framework_heading = _framework_display_name(fw)
    body = _build_dream_note_body(
        dream_text,
        interpretation_clean,
        associations,
        resource_id,
        user_id,
        orch,
        framework_heading=framework_heading,
    )

    folder_id = await orch.joplin_client.get_or_create_folder_by_path(DREAM_JOURNAL_PATH)
    note_id = await orch.joplin_client.create_note(
        folder_id, title, body, image_data_url=None
    )
    second = _FRAMEWORK_JOPLIN_TAGS.get(fw, "jungian")
    await orch.joplin_client.apply_tags(note_id, ["dream-journal", second])
    _schedule_joplin_sync()
    return True


def register_dream_handlers(application: Any, orch: TelegramOrchestrator) -> None:
    """Register dream analysis handlers."""

    async def dream_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Dream command received")
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            logger.warning("Dream command: missing user or message")
            return
        if not check_whitelist(user.id):
            logger.info("Dream command: user %d not whitelisted", user.id)
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        state = {
            "active_persona": "DREAM_ANALYST",
            "phase": "dream_description",
            "dream_text": "",
            "dream_framework": "",
            "dream_image_url": "",
            "interpretation": "",
            "associations": "",
        }
        try:
            orch.state_manager.update_state(user.id, state)
            logger.info("Dream command: state updated for user %d", user.id)
        except Exception as exc:
            logger.error("Dream command: state update failed for user %d: %s", user.id, exc, exc_info=True)
            await msg.reply_text(format_error_message("Could not start dream session. Please try again."))
            return

        # BF-017: Use plain text for welcome — Markdown parse_mode can cause BadRequest
        # (similar to BF-010, BF-014). Plain text avoids parse errors entirely.
        welcome = (
            "🌙 Welcome to Dream Analysis\n\n"
            "Take a moment to recall your dream...\n\n"
            "When you're ready, describe everything you remember:\n"
            "• What happened?\n"
            "• Who was there?\n"
            "• What did you see, hear, feel?\n"
            "• Any symbols, colors, or unusual elements?\n\n"
            "After that, you'll choose an approach: Jungian, Gestalt (Perls), or Adlerian.\n\n"
            "Take your time. The more detail, the richer the analysis.\n\n"
            "Type /dream_cancel to cancel anytime."
        )
        await msg.reply_text(welcome)
        logger.info("Dream session started for user %d", user.id)

    async def dream_done_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Dream done command received")
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            logger.warning("Dream done: missing user or message")
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        state = orch.state_manager.get_state(user.id)
        logger.debug("Dream done: user=%d state=%s", user.id, "present" if state else "none")
        if not state or state.get("active_persona") != "DREAM_ANALYST":
            await msg.reply_text("You don't have an active dream session. Use /dream to start one.")
            return

        ph = state.get("phase")
        if ph == "dream_description":
            await msg.reply_text("Please describe your dream first before saving.")
            return
        if ph == "framework_choice":
            await msg.reply_text(
                "Choose a framework with the buttons (or type jungian / gestalt / adlerian) "
                "and wait for the analysis before saving."
            )
            return
        if ph == "analyzing":
            await msg.reply_text("Your dream is still being analyzed. Please wait for the result.")
            return

        try:
            logger.info("Dream done: user=%d saving to Joplin", user.id)
            await msg.reply_text("📝 Saving to your Dream Journal...")
            ok = await _save_dream_to_joplin(orch, user.id, state)
            orch.state_manager.clear_state(user.id)
            if ok:
                await msg.reply_text(
                    "✅ Dream analysis saved to your Dream Journal. "
                    "Syncing to your other devices…"
                )
                logger.info("Dream done: user=%d saved successfully", user.id)
            else:
                await msg.reply_text(format_error_message("Failed to save. Please try again."))
                logger.warning("Dream done: user=%d save returned False", user.id)
        except Exception as exc:
            logger.error("Dream save failed for user %d: %s", user.id, exc, exc_info=True)
            await msg.reply_text(format_error_message("Failed to save. Please try again."))

    async def dream_cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Dream cancel command received")
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        state = orch.state_manager.get_state(user.id)
        if state and state.get("active_persona") == "DREAM_ANALYST":
            task = _pending_dream_image_tasks.pop(user.id, None)
            if task and not task.done():
                task.cancel()
            orch.state_manager.clear_state(user.id)
            await msg.reply_text("Dream session cancelled. Nothing was saved.")
        else:
            await msg.reply_text("No active dream session to cancel.")

    async def dream_framework_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        user = query.from_user
        if not user or not check_whitelist(user.id):
            await query.answer(text="Not authorized", show_alert=True)
            return

        data = (query.data or "").strip()
        mapping = {
            "dream_fw_jungian": "jungian",
            "dream_fw_gestalt": "gestalt",
            "dream_fw_adlerian": "adlerian",
        }
        fw = mapping.get(data)
        if not fw:
            await query.answer()
            return

        state = orch.state_manager.get_state(user.id)
        if not state or state.get("active_persona") != "DREAM_ANALYST":
            await query.answer(text="No active dream session.", show_alert=True)
            return
        if state.get("phase") != "framework_choice":
            await query.answer(text="Not waiting for a framework choice.", show_alert=True)
            return

        dream_text = (state.get("dream_text") or "").strip()
        if not dream_text:
            await query.answer(text="Missing dream text. Start again with /dream.", show_alert=True)
            return

        msg = query.message
        if not isinstance(msg, Message):
            logger.warning(
                "Dream framework callback: expected Message, got %s",
                type(msg).__name__ if msg is not None else "None",
            )
            await query.answer(text="Please try again from /dream.", show_alert=True)
            return

        await query.answer()

        with contextlib.suppress(Exception):
            await msg.edit_reply_markup(reply_markup=None)

        await _run_dream_interpretation(orch, user.id, msg, dream_text, fw)

    application.add_handler(CallbackQueryHandler(dream_framework_callback, pattern="^dream_fw_"))
    application.add_handler(CommandHandler("dream", dream_cmd))
    application.add_handler(CommandHandler("dream_done", dream_done_cmd))
    application.add_handler(CommandHandler("dream_cancel", dream_cancel_cmd))
    logger.info("Dream handlers registered")
