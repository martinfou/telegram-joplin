"""
Core handlers: /start, /status, /helpme, and message routing.
"""

from __future__ import annotations

import asyncio
import base64
import contextlib
import difflib
import logging
import os
import re
from typing import TYPE_CHECKING, Any

import httpx
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.constants import ChatAction
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from src.constants import is_action_item
from src.exceptions import AppError, GoogleAuthError
from src.handlers.profile import get_user_profile_context
from src.joplin_client import normalize_folder_title_for_match
from src.logging_service import Decision, TelegramMessage
from src.security_utils import (
    check_whitelist,
    format_error_message,
    format_success_message,
    handle_api_error,
    ping_joplin_api,
    validate_message_text,
    validate_note_data,
)
from src.timezone_utils import get_user_timezone_aware_now
from src.url_enrichment import extract_urls, fetch_url_context, template_for_url_type

if TYPE_CHECKING:
    from src.telegram_orchestrator import TelegramOrchestrator

logger = logging.getLogger(__name__)
_sync_task: asyncio.Task | None = None
PROJECT_STATUS_TAGS = {
    "status/planning",
    "status/building",
    "status/blocked",
    "status/done",
}

# Recipe notes go in Resources/🍽️ Recipe (try Resources first, Ressources as fallback for French)
RECIPE_FOLDER_PATHS = (["03 - Resources", "🍽️ Recipe"], ["Ressources", "🍽️ Recipe"])

GREETING_PATTERNS = [
    r"^(hi|hello|hey|howdy|greetings|yo)[\s!?.]*$",
    r"^good\s+(morning|afternoon|evening|day|night)[\s!?.]*$",
    r"^(bonjour|salut|coucou|bonsoir|bonne\s+journée)[\s!?.]*$",
    r"^what'?s?\s+up[\s!?.]*$",
    r"^(hola|buenos\s+días|buenas\s+tardes)[\s!?.]*$",
]


def _is_greeting(text: str) -> bool:
    """Check if text is a simple greeting (avoids triggering note creation)."""
    text_lower = text.strip().lower()
    return any(re.match(pattern, text_lower) for pattern in GREETING_PATTERNS)


PROFILE_QUERY_PATTERNS = [
    r"^who\s+am\s+i\s*[?.!]*$",
    r"^what('s|s| is)\s+my\s+profile\s*[?.!]*$",
    r"^tell\s+me\s+(about\s+)?myself\s*[?.!]*$",
    r"^what\s+do\s+you\s+know\s+about\s+me\s*[?.!]*$",
    r"^my\s+profile\s*[?.!]*$",
]


def _is_profile_query(text: str) -> bool:
    """Check if text is asking about the user's profile (who am i, etc.)."""
    text_lower = text.strip().lower()
    return any(re.match(p, text_lower) for p in PROFILE_QUERY_PATTERNS)


def register_core_handlers(application: Any, orch: TelegramOrchestrator) -> None:
    application.add_handler(CommandHandler("start", _start(orch)))
    application.add_handler(CommandHandler("help", _start(orch)))  # Alias for /start
    application.add_handler(CommandHandler("status", _status(orch)))
    application.add_handler(CommandHandler("status_projects", _project_status(orch)))
    application.add_handler(CommandHandler("project_status", _project_status(orch)))
    application.add_handler(CommandHandler("project_report", _project_report(orch)))
    application.add_handler(CommandHandler("sync", _sync(orch)))
    application.add_handler(CommandHandler("note", _note(orch)))
    application.add_handler(CommandHandler("bookmark", _bookmark(orch)))
    application.add_handler(CommandHandler("learnings", _learnings(orch)))
    application.add_handler(CommandHandler("recipe", _recipe(orch)))
    application.add_handler(CommandHandler("task", _task(orch)))
    application.add_handler(CommandHandler("help_commands", _helpme(orch)))
    application.add_handler(CommandHandler("helpme", _helpme(orch)))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, _message(orch))
    )
    application.add_handler(CallbackQueryHandler(_project_selection_callback(orch), pattern="^project_sel_"))
    application.add_handler(CallbackQueryHandler(_duplicate_task_callback(orch), pattern="^dup_"))


# ---------------------------------------------------------------------------
# Handler factories — each returns an async callback bound to the orchestrator
# ---------------------------------------------------------------------------


def _build_greeting_response(user_id: int, orch: TelegramOrchestrator) -> str:
    """Build greeting message with time-aware salutation and command list."""
    now = get_user_timezone_aware_now(user_id, orch.logging_service)
    hour = now.hour

    if 5 <= hour < 12:
        time_greeting = "Good morning! ☀️"
    elif 12 <= hour < 17:
        time_greeting = "Good afternoon! 👋"
    elif 17 <= hour < 21:
        time_greeting = "Good evening! 🌆"
    else:
        time_greeting = "Hello! 🌙"

    # Use HTML: underscores in /daily_report, /weekly_report, /monthly_report break Markdown.
    # In HTML, _ is not special. Escape < > & for literal display. See BF-010.
    return (
        f"{time_greeting} I'm your Second Brain assistant.\n\n"
        "<b>📝 Capture</b>\n"
        "• Send any text → Save as Joplin note\n"
        "• Send a photo → OCR and save to Joplin (tip: send as File for best quality)\n"
        "• /readlater &lt;url&gt; or /rl &lt;url&gt; → Save to reading queue\n"
        "• /task &lt;text&gt; → Create Google Task\n"
        "• /note &lt;text&gt; → Force note creation\n\n"
        "<b>🔍 Search</b>\n"
        "• /find &lt;query&gt; or /search &lt;query&gt; → Quick note search\n"
        "• /ask &lt;question&gt; → AI answers from your notes (semantic search)\n\n"
        "<b>🧠 Productivity</b>\n"
        "• /braindump → GTD brain dump (standard 15 min); /braindump quick (5 min); /braindump thorough (25 min)\n"
        "• /bookmark &lt;url&gt; → Save URL to Bookmarks folder\n"
        "• /stoic → Guided morning/evening reflection\n"
        "• /learnings → What you learned this week (from Stoic journal)\n"
        "• /dream → Dream analysis (Jungian, Gestalt, or Adlerian)\n"
        "• /habits → Daily habit check-in\n"
        "• /flashcard → Spaced repetition practice from notes\n"
        "• /plan → Weekly planning session\n"
        "• /recipe → Save and organize recipes\n"
        "• /project_new &lt;name&gt; or /pn &lt;name&gt; → Create project with default folders\n\n"
        "<b>💪 Health</b>\n"
        "• /health_import — Then send .csv or screenshot (no caption), or caption /health_import on file/photo; "
        "/health_import_quick &lt;text&gt; to paste\n"
        "• /health_today, /health_week — Summaries from Garmin / FatSecret / Arboleaf data\n"
        "• /health_goal, /health_goals — Targets and weekly adherence\n"
        "• /health_last — Last captured row per source\n\n"
        "<b>📊 Review</b>\n"
        "• /report_daily → Today's priorities\n"
        "• /report_weekly → Weekly productivity review\n"
        "• /report_monthly → Monthly review with insights\n\n"
        "<b>👤 Personalization</b>\n"
        "• /profile → Your about-me (AI uses this for context)\n"
        "• /identity → AI identity (bot persona)\n\n"
        "💡 Type anything to get started, or use a command above!"
    )


def _greeting_to_plain(html_text: str) -> str:
    """Strip HTML tags and unescape entities for plain-text fallback (BF-010)."""
    out = re.sub(r"</?b>", "", html_text)
    return out.replace("&lt;", "<").replace("&gt;", ">")


async def _send_greeting_safe(message: Message, greeting: str) -> None:
    """Send greeting with HTML; fall back to plain text on parse/send error (BF-010)."""
    plain = _greeting_to_plain(greeting)
    try:
        await message.reply_text(greeting, parse_mode="HTML")
    except Exception as exc:
        exc_str = str(exc).lower()
        exc_type = type(exc).__name__
        is_parse_error = (
            "parse" in exc_str
            or "entities" in exc_str
            or "badrequest" in exc_type.lower()
        )
        logger.warning(
            "Greeting send failed (%s), falling back to plain text: %s",
            "parse" if is_parse_error else "other",
            exc,
        )
        try:
            await message.reply_text(plain)
        except Exception as fallback_exc:
            logger.error("Greeting plain fallback also failed: %s", fallback_exc)
            raise exc from fallback_exc


def _start(orch: TelegramOrchestrator):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user:
            return
        if not check_whitelist(user.id):
            await update.message.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        orch.state_manager.clear_state(user.id)

        welcome = _build_greeting_response(user.id, orch)
        await _send_greeting_safe(update.message, welcome)
        logger.info("Started conversation with user %d", user.id)

    return handler


def _status(orch: TelegramOrchestrator):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        joplin_ok = await ping_joplin_api()
        dropbox_sync_ok, dropbox_sync_msg = await _get_joplin_dropbox_sync_status()
        has_pending = orch.state_manager.has_pending_state(user.id)

        google_ok = False
        if orch.task_service:
            try:
                token = orch.logging_service.load_google_token(str(user.id))
                google_ok = token is not None
            except Exception:
                pass

        msg = (
            "🤖 Bot Status:\n\n"
            f"Joplin API: {'✅ Connected' if joplin_ok else '❌ Not accessible'}\n"
            f"Joplin Sync (Dropbox): {'✅ Configured' if dropbox_sync_ok else '❌ Not configured'}"
            f"{f' ({dropbox_sync_msg})' if dropbox_sync_msg else ''}\n"
            f"Pending clarification: {'✅ Yes' if has_pending else '❌ No'}\n"
            f"Google Tasks: {'✅ Configured' if google_ok else '❌ Not configured'}\n"
        )
        if os.environ.get("FLY_APP_NAME"):
            msg += (
                "\n📍 Server Joplin: notes from this bot live in Joplin on Fly, not inside "
                "your Mac app. To see them on Desktop, use the same sync target on both "
                "(Joplin Cloud, Dropbox, etc.) via `joplin config` on the server, or export "
                "from the server profile.\n"
            )
        if not joplin_ok:
            msg += "\n⚠️ Make sure Joplin is running with Web Clipper enabled."
        await update.message.reply_text(msg)

    return handler


def _sync(orch: TelegramOrchestrator):
    """Force a Joplin sync with the configured target (e.g. Dropbox)."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        await update.message.reply_chat_action(ChatAction.TYPING)
        dropbox_ok, sync_target_msg = await _get_joplin_dropbox_sync_status()
        target_label = "Dropbox" if dropbox_ok else sync_target_msg

        if os.environ.get("FLY_APP_NAME") and not dropbox_ok and "None" in sync_target_msg:
            await update.message.reply_text(
                "⚠️ Server Joplin has *no sync target* set (`sync.target=None`). "
                "/sync only runs sync on the *server profile*; it cannot reach your Mac until "
                "you configure the same Joplin sync (Cloud, Dropbox, …) on this server and in "
                "Desktop, or export from the server.",
                parse_mode="Markdown",
            )

        await update.message.reply_text(
            f"🔄 Syncing Joplin with {target_label}… This may take up to a minute."
        )

        profile = os.environ.get("JOPLIN_PROFILE")
        if not profile and os.path.isdir("/app/data/joplin"):
            profile = "/app/data/joplin"
        cmd = ["joplin"] + (["--profile", profile] if profile else []) + ["sync"]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=90)
        except FileNotFoundError:
            await update.message.reply_text(
                format_error_message("Joplin CLI not found; sync unavailable.")
            )
            return
        except TimeoutError:
            await update.message.reply_text(
                format_error_message("Sync timed out after 90 seconds.")
            )
            return
        except Exception as exc:
            logger.exception("Sync command failed")
            await update.message.reply_text(format_error_message(f"Sync failed: {exc}"))
            return

        if proc.returncode == 0:
            await update.message.reply_text(
                f"✅ Sync with {target_label} completed successfully."
            )
        else:
            err = (stderr or stdout).decode("utf-8", errors="ignore").strip()
            await update.message.reply_text(
                format_error_message(f"Sync failed (exit {proc.returncode}): {err or 'unknown error'}")
            )
        logger.info("User %d ran /sync", user.id)

    return handler


def _bookmark(orch: TelegramOrchestrator):
    """Save a URL as a bookmark note in the Bookmarks folder. Usage: /bookmark <url>"""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        parts = (update.message.text or "").strip().split(maxsplit=1)
        url = parts[1].strip() if len(parts) > 1 else ""

        if not url:
            await update.message.reply_text(
                "🔖 *Use /bookmark to save a URL to Joplin*\n\n"
                "Example:\n"
                "  /bookmark https://example.com/article\n\n"
                "The bot fetches the page title and saves it to your Bookmarks folder.",
                parse_mode="Markdown",
            )
            return

        urls = extract_urls(url)
        if not urls:
            await update.message.reply_text(
                format_error_message("Please provide a valid URL. Example: /bookmark https://example.com")
            )
            return

        status_msg = await update.message.reply_text("🔖 Fetching page info...")
        try:
            url_context = await fetch_url_context(urls[0])
        except Exception:
            url_context = None

        title = (url_context or {}).get("title") or urls[0]
        description = (url_context or {}).get("description") or ""
        extracted_text = (url_context or {}).get("extracted_text") or ""

        # Build note body
        body_parts = [f"🔖 **Source:** {urls[0]}", ""]
        if description:
            body_parts += [f"**Summary:** {description}", ""]
        if extracted_text:
            snippet = extracted_text[:500].strip()
            if snippet:
                body_parts += ["## Excerpt", snippet, ""]
        body_parts.append("*Bookmarked via /bookmark*")
        body = "\n".join(body_parts)

        # Find or create Bookmarks folder
        bookmark_folder_id: str | None = None
        try:
            folders = await orch.joplin_client.get_folders()
            bm = next(
                (f for f in folders if normalize_folder_title_for_match(f.get("title", "")) == "bookmarks"),
                None,
            )
            if bm:
                bookmark_folder_id = bm["id"]
            else:
                new_folder = await orch.joplin_client.create_folder("Bookmarks")
                bookmark_folder_id = new_folder.get("id")
        except Exception as exc:
            logger.warning("Could not find/create Bookmarks folder: %s", exc)

        note_data = {
            "title": title,
            "body": body,
            "parent_id": bookmark_folder_id or "Bookmarks",
            "tags": ["bookmark"],
        }

        result = await create_note_in_joplin(orch, note_data, url_context=url_context, message=status_msg)
        if result and "error" not in result:
            await status_msg.edit_text(
                format_success_message(f"Bookmarked: {title}\n🔖 Saved to Bookmarks")
            )
        else:
            await status_msg.edit_text(format_error_message("Failed to save bookmark. Try again."))

    return handler


def _learnings(orch: TelegramOrchestrator):
    """US-042 T-012: Aggregate 'What I Learned Today' from last 7 Stoic Journal entries."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return
        if not update.message:
            return

        await update.message.reply_text("📚 Fetching your learnings from this week...")

        STOIC_PATH = ["01 - Areas", "📓 Journaling", "Stoic Journal"]
        from datetime import datetime, timedelta

        from src.timezone_utils import get_user_timezone_aware_now
        try:
            folder_id = await orch.joplin_client.get_or_create_folder_by_path(STOIC_PATH)
            notes_in_folder = await orch.joplin_client.get_notes_in_folder(folder_id)
        except Exception as exc:
            logger.warning("Could not access Stoic Journal: %s", exc)
            await update.message.reply_text("❌ Could not access Stoic Journal in Joplin.")
            return

        now_local = get_user_timezone_aware_now(user.id, orch.logging_service)
        cutoff = (now_local - timedelta(days=7)).date()
        daily_notes = [
            n for n in notes_in_folder
            if "Daily Stoic Reflection" in n.get("title", "")
            and "Weekly Stoic Review" not in n.get("title", "")
        ]

        import re
        learnings: list[str] = []
        for note_meta in daily_notes[-10:]:
            try:
                full = await orch.joplin_client.get_note(note_meta["id"])
                title = full.get("title", "")
                date_part = title.split(" - ")[0].strip()
                try:
                    note_date = datetime.fromisoformat(date_part).date()
                    if note_date < cutoff:
                        continue
                except ValueError:
                    pass
                body = full.get("body", "")
                match = re.search(r"### 📚 What I Learned Today\s*\n+(.*?)(?=\n- \*\*|\n### |\Z)", body, re.DOTALL)
                if match:
                    text = match.group(1).strip().lstrip("-").strip()
                    if text and text != "-":
                        learnings.append(f"**{date_part}**: {text}")
            except Exception:
                pass

        if not learnings:
            await update.message.reply_text(
                "No learnings found this week. Complete an evening Stoic journal session "
                "and answer the 'What did you learn today?' question to start building your list."
            )
            return

        reply = "📚 *What You Learned This Week*\n\n" + "\n\n".join(learnings)
        if len(reply) > 4000:
            reply = reply[:3990] + "…"
        await update.message.reply_text(reply, parse_mode="Markdown")

    return handler


def _note(orch: TelegramOrchestrator):
    """Create a Joplin note only (no task). Usage: /note <content or URL>."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return
        parts = (update.message.text or "").strip().split(maxsplit=1)
        payload = parts[1].strip() if len(parts) > 1 else ""
        if not payload:
            await update.message.reply_text(
                "📝 *Use /note to save as a Joplin note only*\n\n"
                "Example:\n"
                "  /note https://example.com/article\n"
                "  /note Meeting notes from standup\n\n"
                "Everything after /note is saved as a note (URLs are fetched).",
                parse_mode="Markdown",
            )
            return
        validated = validate_message_text(payload)
        if not validated:
            await update.message.reply_text(format_error_message("Content too long or empty."))
            return
        telegram_msg = TelegramMessage(user_id=user.id, message_text=validated)
        telegram_message_id = orch.logging_service.log_telegram_message(telegram_msg)
        await _handle_new_request(
            orch, user.id, validated, update.message, telegram_message_id, context,
            force_note=True,
        )

    return handler


def _recipe(orch: TelegramOrchestrator):
    """Save as a recipe note. Usage: /recipe <pasted recipe or URL>."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return
        parts = (update.message.text or "").strip().split(maxsplit=1)
        payload = parts[1].strip() if len(parts) > 1 else ""
        if not payload:
            await update.message.reply_text(
                "🍳 *Use /recipe to save a recipe*\n\n"
                "Paste the recipe text or send a URL:\n"
                "  /recipe Gâteau aux carottes...\n"
                "  /recipe https://recettes.qc.ca/recette/...\n\n"
                "The bot will format it as a recipe note with ingredients, steps, and nutrition.",
                parse_mode="Markdown",
            )
            return
        validated = validate_message_text(payload)
        if not validated:
            await update.message.reply_text(format_error_message("Content too long or empty."))
            return
        telegram_msg = TelegramMessage(user_id=user.id, message_text=validated)
        telegram_message_id = orch.logging_service.log_telegram_message(telegram_msg)
        await _handle_new_request(
            orch, user.id, validated, update.message, telegram_message_id, context,
            force_note=True,
            force_recipe=True,
        )

    return handler


def _task(orch: TelegramOrchestrator):
    """Create a Google Task only (no note). Usage: /task <action item>."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return
        parts = (update.message.text or "").strip().split(maxsplit=1)
        payload = parts[1].strip() if len(parts) > 1 else ""
        if not payload:
            await update.message.reply_text(
                "✅ *Use /task to create a Google Task only*\n\n"
                "Example:\n"
                "  /task Call John tomorrow\n"
                "  /task Review PR #42\n\n"
                "Everything after /task becomes a task (no Joplin note).",
                parse_mode="Markdown",
            )
            return
        validated = validate_message_text(payload)
        if not validated:
            await update.message.reply_text(format_error_message("Content too long or empty."))
            return
        telegram_msg = TelegramMessage(user_id=user.id, message_text=validated)
        telegram_message_id = orch.logging_service.log_telegram_message(telegram_msg)
        await _handle_new_request(
            orch, user.id, validated, update.message, telegram_message_id, context,
            force_task=True,
        )

    return handler


async def _get_joplin_dropbox_sync_status() -> tuple[bool, str]:
    """Return whether Joplin sync target is configured to Dropbox (target=7)."""
    profile = os.environ.get("JOPLIN_PROFILE")
    if not profile and os.path.isdir("/app/data/joplin"):
        profile = "/app/data/joplin"

    cmd = ["joplin", "config", "sync.target"]
    if profile:
        cmd = ["joplin", "--profile", profile, "config", "sync.target"]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return False, "Joplin CLI unavailable"

    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=6)
    except TimeoutError:
        proc.kill()
        return False, "status check timeout"

    output = f"{stdout.decode('utf-8', errors='ignore')}\n{stderr.decode('utf-8', errors='ignore')}"
    match = re.search(r"sync\.target\s*=\s*(\d+)", output)
    if not match:
        return False, "unknown target"

    target = int(match.group(1))
    if target == 7:
        return True, "target=Dropbox"
    if target == 0:
        return False, "target=None"
    return False, f"target={target}"


def _helpme(orch: TelegramOrchestrator):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        help_message = (
            "🆘 Help - Available Commands\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📝 **Note vs Task**\n"
            "🔹 /note <content> → Joplin note only (URLs fetched)\n"
            "🔹 /task <item> → Google Task only\n"
            "🔹 Plain message → Bot chooses (note or task by keywords)\n"
            "🔹 Send a photo → OCR and save to Joplin (/photo_cancel to cancel)\n"
            "   💡 Tip: use 'Send as File' in Telegram for best OCR quality (no compression)\n\n"
            "🔍 **Search**\n"
            "🔹 /find <query> or /search <query> → Search notes, reply with number to view\n\n"
            "📚 **Read Later**\n"
            "/readlater <url> or /rl <url> - Save article to reading queue\n"
            "/reading - View queue; /reading done <n> to mark read\n\n"
            "📋 **Commands**\n"
            "/start - Welcome message & quick command list\n"
            "/status - Check if Joplin & Google Tasks are connected\n"
            "/sync - Force Joplin sync with Dropbox (or configured sync target)\n"
            "/project_status - Show counts by project status tags\n"
            "/help_commands - Show this detailed help message\n\n"
            "📌 **Project status tags**\n"
            "Notes in Projects can use tags: status/planning, status/building, status/blocked, status/done. "
            "Use /project_status to see the summary.\n\n"
            "📅 **Google Tasks Management**\n"
            "/tasks_connect - Connect your Google account\n"
            "/tasks_list - View your pending Google Tasks\n"
            "/tasks_status - See sync history & stats\n"
            "/tasks_config - Manage settings (list, project sync, etc.)\n"
            "/tasks_toggle_project_sync - Joplin projects as parent tasks\n"
            "/tasks_sync_projects - Create parent tasks for all project folders\n"
            "/tasks_cleanup [days] - Delete completed tasks older than N days (default: 30)\n\n"
            "📊 **Reports**\n"
            "/report_daily - Get on-demand priority report\n"
            "/report_weekly - Weekly review with trends & metrics\n"
            "/report_monthly - Monthly review with insights\n"
            "/report_set_time HH:MM - Set delivery time\n"
            "/report_toggle_schedule on|off - Enable/disable scheduled reports\n"
            "/report_help - Show all report commands\n\n"
            "🧠 **Productivity**\n"
            "/braindump [quick|thorough] - GTD mind sweep (5/15/25 min); /braindump_stop to end\n"
            "/bookmark <url> - Save URL to Bookmarks folder in Joplin\n"
            "/stoic [morning|evening] - Guided reflection; /stoic_done to save\n"
            "/learnings - What you learned this week (from Stoic evening entries)\n"
            "/dream - Dream analysis (framework choice); /dream_done, /dream_cancel\n"
            "/habits - Daily habit check-in; /habits add|remove|list|stats\n"
            "/flashcard - Spaced repetition; /flashcard from <note>; /flashcard_done\n"
            "/plan - Weekly planning session; /plan_done, /plan_cancel\n\n"
            "💪 **Health** (Garmin / FatSecret / Arboleaf)\n"
            "🔹 /health_import — Then send .csv or screenshot (no caption), or attach with caption /health_import; "
            "optional: /health_import garmin|fatsecret|arboleaf; /health_import cancel\n"
            "🔹 /health_import_quick <text> — Paste summary text from an app\n"
            "🔹 /health_today — Today's merged summary\n"
            "🔹 /health_week — Last 7 days rollup (goals section if you set /health_goal)\n"
            "🔹 /health_goal <metric> <value> — Set a target (e.g. steps 10000, protein_g 160); "
            "delete / delete all\n"
            "🔹 /health_goals — List goals and adherence\n"
            "🔹 /health_last — Last saved row per source\n\n"
            "🏗️ **Joplin Database Organization**\n"
            "/project_new <name> or /pn <name> - Create project with default folders\n"
            "/reorg_status - Check notes, folders, and organization health\n"
            "/reorg_init status|roles - Initialize PARA structure\n"
            "/reorg_preview - See migration plan without changes\n"
            "/reorg_execute - Apply reorganization\n"
            "/reorg_enrich [limit] - Add metadata to notes\n"
            "/reorg_help - Show all reorganization commands\n\n"
            "❓ **Questions?**\n"
            "Just send /status to check connectivity."
        )
        await update.message.reply_text(help_message)
        logger.info("Showed help to user %d", user.id)

    return handler


def _project_status(orch: TelegramOrchestrator):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        try:
            folders = await orch.joplin_client.get_folders()
            by_id = {f.get("id"): f for f in folders if f.get("id")}

            project_root_id = None
            for f in folders:
                norm = normalize_folder_title_for_match(f.get("title") or "")
                if norm in ("projects", "project"):
                    project_root_id = f.get("id")
                    break

            if not project_root_id:
                await update.message.reply_text("❌ I couldn't find folder `Projects`.")
                return

            def in_projects(folder_id: str) -> bool:
                cur = folder_id
                seen: set[str] = set()
                while cur and cur not in seen:
                    if cur == project_root_id:
                        return True
                    seen.add(cur)
                    node = by_id.get(cur)
                    if not node:
                        break
                    cur = node.get("parent_id", "")
                return False

            tags = await orch.joplin_client.fetch_tags()
            tag_id_by_name = {
                (t.get("title") or "").strip().lower(): t.get("id")
                for t in tags
                if t.get("id")
            }

            status_order = [
                "status/planning",
                "status/building",
                "status/blocked",
                "status/done",
            ]
            status_counts = {name: 0 for name in status_order}
            tagged_project_note_ids: set[str] = set()

            for status_name in status_order:
                tag_id = tag_id_by_name.get(status_name)
                if not tag_id:
                    continue
                notes = await orch.joplin_client.get_notes_with_tag(tag_id)
                for note in notes:
                    note_id = note.get("id")
                    parent_id = note.get("parent_id", "")
                    if note_id and parent_id and in_projects(parent_id):
                        status_counts[status_name] += 1
                        tagged_project_note_ids.add(note_id)

            all_notes = await orch.joplin_client.get_all_notes(fields="id,parent_id")
            all_project_note_ids = {
                n.get("id")
                for n in all_notes
                if n.get("id") and n.get("parent_id") and in_projects(n.get("parent_id", ""))
            }
            untagged_count = max(len(all_project_note_ids) - len(tagged_project_note_ids), 0)

            msg = (
                "📊 Project Status Tags\n\n"
                f"🟡 Planning: {status_counts['status/planning']}\n"
                f"🔵 Building: {status_counts['status/building']}\n"
                f"🟠 Blocked: {status_counts['status/blocked']}\n"
                f"✅ Done: {status_counts['status/done']}\n"
                f"⚪ Untagged: {untagged_count}\n"
            )
            await update.message.reply_text(msg)
        except Exception as exc:
            logger.error("Failed to compute project status: %s", exc, exc_info=True)
            await update.message.reply_text("❌ Failed to compute project status right now.")

    return handler


# ---------------------------------------------------------------------------
# US-060: World-Class Project Report
# ---------------------------------------------------------------------------

_STATUS_BADGES = {
    "status/blocked": "🟠 Blocked",
    "status/building": "🔵 Building",
    "status/planning": "🟡 Planning",
    "status/done": "✅ Done",
    "untagged": "⚪ Untagged",
}
_STATUS_ORDER = ["status/blocked", "status/building", "status/planning", "untagged", "status/done"]
_STALL_DAYS = 14
_DONE_THIS_WEEK_DAYS = 7


def _ms_to_days_ago(ms: int) -> int:
    """Convert a millisecond timestamp to days ago (0 = today) using system time.

    Kept for backward compatibility and unit tests; prefer `_ms_to_days_ago_user`.
    """
    import time

    if not ms:
        return 999
    now_ms = int(time.time() * 1000)
    diff_ms = now_ms - ms
    return max(0, diff_ms // 86_400_000)


def _ms_to_days_ago_user(ms: int, user_id: int, orch: TelegramOrchestrator) -> int:
    """Convert a millisecond timestamp to whole days ago (0 = today) in user's timezone."""
    from datetime import UTC, datetime

    if not ms:
        return 999
    now = get_user_timezone_aware_now(user_id, orch.logging_service)
    then = datetime.fromtimestamp(ms / 1000.0, tz=UTC).astimezone(now.tzinfo)
    return max(0, (now.date() - then.date()).days)


async def build_project_portfolio_html(orch: TelegramOrchestrator, user_id: int) -> str:
    """
    Build the project portfolio section HTML (US-060). Used by /project_report and
    optionally by /weekly_report when include_project_portfolio is enabled.
    Returns empty string if no projects or Joplin unavailable.
    """
    cfg = orch.logging_service.get_google_tasks_config(user_id) or {}
    proj_folder_id_override = cfg.get("projects_folder_id")
    if not orch.reorg_orchestrator:
        return ""
    try:
        project_list: list[tuple[str, str]] = await orch.reorg_orchestrator.get_project_folders(
            projects_folder_id=proj_folder_id_override
        )
    except Exception:
        return ""
    if not project_list:
        return ""

    all_notes = await orch.joplin_client.get_all_notes(fields="id,title,parent_id,updated_time")
    notes_by_folder: dict[str, list[dict]] = {}
    for note in all_notes:
        fid = note.get("parent_id") or ""
        notes_by_folder.setdefault(fid, []).append(note)

    tags = await orch.joplin_client.fetch_tags()
    tag_id_by_name = {
        (t.get("title") or "").strip().lower(): t.get("id")
        for t in tags if t.get("id")
    }
    folder_status: dict[str, str] = {}
    for status_name in ["status/blocked", "status/building", "status/planning", "status/done"]:
        tag_id = tag_id_by_name.get(status_name)
        if not tag_id:
            continue
        notes_with_tag = await orch.joplin_client.get_notes_with_tag(tag_id)
        for note in notes_with_tag:
            fid = note.get("parent_id") or ""
            if fid and fid not in folder_status:
                folder_status[fid] = status_name

    tasks_by_project: dict[str, list[dict]] = {}
    last_completed_ms_by_project: dict[str, int] = {}
    if orch.task_service and cfg.get("project_sync_enabled"):
        tasks_by_project, last_completed_ms_by_project = orch.task_service.get_project_task_activity(str(user_id))

    projects: list[dict[str, Any]] = []
    for folder_id, title in project_list:
        notes = notes_by_folder.get(folder_id, [])
        note_count = len(notes)
        last_ms = max((n.get("updated_time") or 0 for n in notes), default=0)
        days_since = _ms_to_days_ago_user(last_ms, user_id, orch) if last_ms else 999
        status = folder_status.get(folder_id, "untagged")
        open_tasks = tasks_by_project.get(folder_id, [])
        task_days_since = _ms_to_days_ago_user(last_completed_ms_by_project.get(folder_id, 0), user_id, orch)
        is_stalled = note_count > 0 and days_since >= _STALL_DAYS and task_days_since >= _STALL_DAYS
        has_next_action = len(open_tasks) > 0
        projects.append({
            "folder_id": folder_id, "title": title, "note_count": note_count,
            "days_since": days_since, "status": status, "open_tasks": open_tasks,
            "is_stalled": is_stalled, "has_next_action": has_next_action,
            "task_days_since": task_days_since,
        })

    def _sort_key(p: dict) -> tuple:
        s = p["status"]
        if s == "status/blocked":
            order = 0
        elif p["is_stalled"]:
            order = 1
        elif s == "status/building":
            order = 2
        elif s == "status/planning":
            order = 3
        elif s == "untagged":
            order = 4
        else:
            order = 5
        return (order, p["title"].lower())

    projects.sort(key=_sort_key)
    active = [p for p in projects if p["status"] != "status/done"]
    done = [p for p in projects if p["status"] == "status/done"]

    blocked_c = sum(1 for p in active if p["status"] == "status/blocked")
    stalled_c = sum(1 for p in active if p["is_stalled"])
    no_next_c = sum(1 for p in active if not p["has_next_action"] and cfg.get("project_sync_enabled"))

    header = f"📊 <b>Project Portfolio</b>  ({len(active)} active"
    if done:
        header += f" · {len(done)} done"
    header += ")"
    if blocked_c:
        header += f"  🟠 {blocked_c} blocked"
    if stalled_c:
        header += f"  ⚠️ {stalled_c} stalled"
    if no_next_c:
        header += f"  📌 {no_next_c} no next action"
    if len(active) > 15:
        header += f"\n⚠️ You have {len(active)} active projects — GTD recommends keeping under 15"

    lines = [header, ""]
    if not active:
        lines.append("✨ No active projects. Start one with /project_new")
    else:
        needs_attention = [
            p for p in active
            if (p["is_stalled"] or (cfg.get("project_sync_enabled") and not p["has_next_action"]))
        ]
        if needs_attention:
            lines.append("🚨 <b>Needs attention</b>")
            for p in needs_attention[:10]:
                badge = _STATUS_BADGES.get(p["status"], "⚪")
                flags: list[str] = []
                if p["is_stalled"]:
                    flags.append(f"⚠️ stalled ({p['days_since']}d)")
                if cfg.get("project_sync_enabled") and not p["has_next_action"]:
                    flags.append("📌 no next action")
                suffix = f" — {' · '.join(flags)}" if flags else ""
                lines.append(f"  • <b>{p['title']}</b>  {badge}{suffix}")
            lines.append("")

        for p in active:
            badge = _STATUS_BADGES.get(p["status"], "⚪")
            stall_flag = " ⚠️ Stalled" if p["is_stalled"] else ""
            lines.append(f"<b>{p['title']}</b>  {badge}{stall_flag}")
            if cfg.get("project_sync_enabled"):
                if p["open_tasks"]:
                    next_t = p["open_tasks"][0]
                    lines.append(f"  📌 Next: {next_t.get('title', 'Untitled')}")
                else:
                    lines.append("  ⚠️ No next action — use /task to add one")
            if p["days_since"] < 999:
                lines.append(f"  🕐 {p['days_since']}d ago  ·  📂 {p['note_count']} note(s)  ·  📋 {len(p['open_tasks'])} task(s)")
            else:
                lines.append(f"  📂 {p['note_count']} note(s)  ·  📋 {len(p['open_tasks'])} task(s)")
            lines.append("")
    if done:
        done_this_week = [p for p in done if p["days_since"] <= _DONE_THIS_WEEK_DAYS]
        if done_this_week:
            titles = ", ".join(p["title"] for p in done_this_week[:5])
            extra = f" +{len(done_this_week) - 5} more" if len(done_this_week) > 5 else ""
            lines.append(f"✅ {len(done_this_week)} completed this week: {titles}{extra}")
    if not cfg.get("project_sync_enabled") and orch.task_service:
        lines.append("")
        lines.append("💡 Tip: Enable /tasks_toggle_project_sync to see next actions per project")
    return "\n".join(lines)


def _project_report(orch: TelegramOrchestrator):
    """US-060: World-Class Project Report — per-project portfolio view."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        drill_query = " ".join(context.args).strip().lower() if context.args else ""

        try:
            await update.message.chat.send_action("typing")

            # ── 1. Get project folders ──────────────────────────────────────
            cfg = orch.logging_service.get_google_tasks_config(user.id) or {}
            proj_folder_id_override = cfg.get("projects_folder_id")
            if not orch.reorg_orchestrator:
                await update.message.reply_text("❌ Joplin not available")
                return
            project_list: list[tuple[str, str]] = await orch.reorg_orchestrator.get_project_folders(
                projects_folder_id=proj_folder_id_override
            )
            if not project_list:
                await update.message.reply_text(
                    "📂 No project folders found.\n\n"
                    "Create folders under Projects in Joplin, then use /project_new to get started."
                )
                return

            # ── 2. Notes: batch fetch with updated_time ─────────────────────
            all_notes = await orch.joplin_client.get_all_notes(fields="id,title,parent_id,updated_time")
            notes_by_folder: dict[str, list[dict]] = {}
            for note in all_notes:
                fid = note.get("parent_id") or ""
                notes_by_folder.setdefault(fid, []).append(note)

            # ── 3. Status tags: fetch once per status ───────────────────────
            tags = await orch.joplin_client.fetch_tags()
            tag_id_by_name = {
                (t.get("title") or "").strip().lower(): t.get("id")
                for t in tags if t.get("id")
            }
            # folder_id → best status (blocked > building > planning > done)
            folder_status: dict[str, str] = {}
            for status_name in ["status/blocked", "status/building", "status/planning", "status/done"]:
                tag_id = tag_id_by_name.get(status_name)
                if not tag_id:
                    continue
                notes_with_tag = await orch.joplin_client.get_notes_with_tag(tag_id)
                for note in notes_with_tag:
                    fid = note.get("parent_id") or ""
                    if fid and fid not in folder_status:
                        folder_status[fid] = status_name

            # ── 4. Google Tasks: batch fetch per project ────────────────────
            tasks_by_project: dict[str, list[dict]] = {}
            last_completed_ms_by_project: dict[str, int] = {}
            if orch.task_service and cfg.get("project_sync_enabled"):
                tasks_by_project, last_completed_ms_by_project = orch.task_service.get_project_task_activity(str(user.id))

            # ── 5. Build project records ────────────────────────────────────
            projects: list[dict[str, Any]] = []
            for folder_id, title in project_list:
                notes = notes_by_folder.get(folder_id, [])
                note_count = len(notes)
                last_ms = max((n.get("updated_time") or 0 for n in notes), default=0)
                days_since = _ms_to_days_ago_user(last_ms, user.id, orch) if last_ms else 999
                status = folder_status.get(folder_id, "untagged")
                open_tasks = tasks_by_project.get(folder_id, [])
                task_days_since = _ms_to_days_ago_user(last_completed_ms_by_project.get(folder_id, 0), user.id, orch)
                is_stalled = note_count > 0 and days_since >= _STALL_DAYS and task_days_since >= _STALL_DAYS
                has_next_action = len(open_tasks) > 0
                projects.append({
                    "folder_id": folder_id, "title": title, "note_count": note_count,
                    "days_since": days_since, "status": status, "open_tasks": open_tasks,
                    "is_stalled": is_stalled, "has_next_action": has_next_action,
                    "task_days_since": task_days_since,
                })

            # ── Drill-down mode ─────────────────────────────────────────────
            if drill_query:
                match = next(
                    (p for p in projects if drill_query in p["title"].lower()), None
                )
                if not match:
                    await update.message.reply_text(
                        f"❌ No project matching '{drill_query}'\n\n"
                        "Use /project_report without arguments for the full portfolio."
                    )
                    return
                lines = [f"📋 <b>{match['title']}</b>  {_STATUS_BADGES.get(match['status'], '⚪')}"]
                lines.append("")
                if match["open_tasks"]:
                    lines.append("📌 Open tasks:")
                    for t in match["open_tasks"]:
                        due = t.get("due", "")
                        due_str = f" · due {due[:10]}" if due else ""
                        lines.append(f"  • {t.get('title', 'Untitled')}{due_str}")
                else:
                    lines.append("📌 No open tasks — use /task to add one")
                lines.append("")
                lines.append(f"📂 {match['note_count']} note(s)")
                # Last 3 notes updated (by updated_time)
                folder_notes = notes_by_folder.get(match["folder_id"], [])
                folder_notes_sorted = sorted(
                    folder_notes,
                    key=lambda n: int(n.get("updated_time") or 0),
                    reverse=True,
                )
                recent = [n for n in folder_notes_sorted if n.get("title")][:3]
                if recent:
                    lines.append("")
                    lines.append("🗂️ Recently updated notes:")
                    for n in recent:
                        d = _ms_to_days_ago_user(int(n.get("updated_time") or 0), user.id, orch)
                        lines.append(f"  • {n.get('title', 'Untitled')} · {d}d ago")
                if match["days_since"] < 999:
                    lines.append(f"🕐 Last activity: {match['days_since']} day(s) ago")
                else:
                    lines.append("🕐 Last activity: unknown")
                await update.message.reply_text("\n".join(lines), parse_mode="HTML")
                return

            # ── Portfolio view ──────────────────────────────────────────────
            # Sort: blocked → stalled → building → planning → untagged → done
            def _sort_key(p: dict) -> tuple:
                s = p["status"]
                if s == "status/blocked":
                    order = 0
                elif p["is_stalled"]:
                    order = 1
                elif s == "status/building":
                    order = 2
                elif s == "status/planning":
                    order = 3
                elif s == "untagged":
                    order = 4
                else:  # done
                    order = 5
                return (order, p["title"].lower())

            projects.sort(key=_sort_key)
            active = [p for p in projects if p["status"] != "status/done"]
            done = [p for p in projects if p["status"] == "status/done"]

            # Portfolio header
            blocked_c = sum(1 for p in active if p["status"] == "status/blocked")
            stalled_c = sum(1 for p in active if p["is_stalled"])
            no_next_c = sum(1 for p in active if not p["has_next_action"] and cfg.get("project_sync_enabled"))

            header = f"📊 <b>Project Portfolio</b>  ({len(active)} active"
            if done:
                header += f" · {len(done)} done"
            header += ")"
            if blocked_c:
                header += f"  🟠 {blocked_c} blocked"
            if stalled_c:
                header += f"  ⚠️ {stalled_c} stalled"
            if no_next_c:
                header += f"  📌 {no_next_c} no next action"
            if len(active) > 15:
                header += f"\n⚠️ You have {len(active)} active projects — GTD recommends keeping under 15"

            lines = [header, ""]

            if not active:
                lines.append("✨ No active projects. Start one with /project_new")
            else:
                needs_attention = [
                    p for p in active
                    if (p["is_stalled"] or (cfg.get("project_sync_enabled") and not p["has_next_action"]))
                ]
                if needs_attention:
                    lines.append("🚨 <b>Needs attention</b>")
                    for p in needs_attention[:10]:
                        badge = _STATUS_BADGES.get(p["status"], "⚪")
                        flags: list[str] = []
                        if p["is_stalled"]:
                            flags.append(f"⚠️ stalled ({p['days_since']}d)")
                        if cfg.get("project_sync_enabled") and not p["has_next_action"]:
                            flags.append("📌 no next action")
                        suffix = f" — {' · '.join(flags)}" if flags else ""
                        lines.append(f"  • <b>{p['title']}</b>  {badge}{suffix}")
                    lines.append("")

                for p in active:
                    badge = _STATUS_BADGES.get(p["status"], "⚪")
                    stall_flag = " ⚠️ Stalled" if p["is_stalled"] else ""
                    lines.append(f"<b>{p['title']}</b>  {badge}{stall_flag}")

                    if cfg.get("project_sync_enabled"):
                        if p["open_tasks"]:
                            next_t = p["open_tasks"][0]
                            lines.append(f"  📌 Next: {next_t.get('title', 'Untitled')}")
                        else:
                            lines.append("  ⚠️ No next action — use /task to add one")

                    if p["days_since"] < 999:
                        lines.append(f"  🕐 {p['days_since']}d ago  ·  📂 {p['note_count']} note(s)  ·  📋 {len(p['open_tasks'])} task(s)")
                    else:
                        lines.append(f"  📂 {p['note_count']} note(s)  ·  📋 {len(p['open_tasks'])} task(s)")
                    lines.append("")

            if done:
                done_this_week = [p for p in done if p["days_since"] <= _DONE_THIS_WEEK_DAYS]
                if done_this_week:
                    titles = ", ".join(p["title"] for p in done_this_week[:5])
                    extra = f" +{len(done_this_week) - 5} more" if len(done_this_week) > 5 else ""
                    lines.append(f"✅ {len(done_this_week)} completed this week: {titles}{extra}")

            if not cfg.get("project_sync_enabled") and orch.task_service:
                lines.append("")
                lines.append("💡 Tip: Enable /tasks_toggle_project_sync to see next actions per project")

            await update.message.reply_text("\n".join(lines), parse_mode="HTML")

        except Exception as exc:
            logger.error("Failed to compute project report: %s", exc, exc_info=True)
            await update.message.reply_text("❌ Failed to load project report right now.")

    return handler


# ---------------------------------------------------------------------------
# Message handler (the main routing logic)
# ---------------------------------------------------------------------------


def _message(orch: TelegramOrchestrator):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        message = update.message
        if not user or not message or not message.text:
            return

        user_id = user.id
        text = message.text.strip()

        if not check_whitelist(user_id):
            await message.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        validated = validate_message_text(text)
        if not validated:
            await message.reply_text("❌ Please send a valid message.")
            return

        try:
            logger.info("Processing message from user %d: '%s'", user_id, validated[:50])

            telegram_msg = TelegramMessage(user_id=user_id, message_text=validated)
            telegram_message_id = orch.logging_service.log_telegram_message(telegram_msg)

            pending = orch.state_manager.get_state(user_id)

            # Greetings always show menu, never trigger LLM (BF-011 Part B).
            # "hello" etc. act as escape hatch even when user has pending clarification.
            if _is_greeting(validated):
                orch.state_manager.clear_state(user_id)
                greeting = _build_greeting_response(user_id, orch)
                await _send_greeting_safe(message, greeting)
                logger.info("Greeting response sent to user %d", user_id)
                return

            if pending:
                if pending.get("active_persona") == "GTD_EXPERT":
                    await _handle_braindump_message(orch, user_id, validated, message)
                elif pending.get("active_persona") == "STOIC_JOURNAL":
                    await _handle_stoic_message(orch, user_id, validated, message)
                elif pending.get("active_persona") == "DREAM_ANALYST":
                    from src.handlers.dream import handle_dream_message
                    await handle_dream_message(orch, user_id, validated, message)
                elif pending.get("active_persona") == "PLANNING_COACH":
                    from src.handlers.planning import handle_planning_message
                    await handle_planning_message(orch, user_id, validated, message)
                elif pending.get("active_persona") == "FLASHCARD":
                    if validated.strip().lower() in ("done", "stop"):
                        from src.flashcard_service import update_session
                        session_id = pending.get("session_id")
                        if session_id:
                            update_session(
                                session_id,
                                pending.get("cards_shown", 0),
                                pending.get("cards_correct", 0),
                            )
                        orch.state_manager.clear_state(user_id)
                        await message.reply_text("✅ Session ended. Use /flashcard to practice again!")
                    else:
                        await message.reply_text(
                            "Use the buttons to rate the card, or /flashcard_done to end the session."
                        )
                elif pending.get("active_persona") == "SEARCH":
                    await _handle_search_message(orch, user_id, validated, message)
                elif pending.get("active_persona") == "PHOTO_OCR":
                    from src.handlers.photo import _is_photo_ocr_state_expired, handle_photo_message
                    if _is_photo_ocr_state_expired(orch, user_id):
                        orch.state_manager.clear_state(user_id)
                        await message.reply_text(
                            format_error_message(
                                "Photo capture session expired (24h limit). Send the photo again to start fresh."
                            )
                        )
                    else:
                        await handle_photo_message(orch, user_id, validated, message)
                elif pending.get("awaiting_project_selection"):
                    await _handle_project_selection_reply(orch, user_id, validated, message, context)
                elif pending.get("awaiting_projects_folder"):
                    await _handle_projects_folder_reply(orch, user_id, validated, message)
                else:
                    await _handle_clarification_reply(orch, user_id, validated, message, context)
            else:
                await _handle_new_request(orch, user_id, validated, message, telegram_message_id, context)

        except Exception as exc:
            logger.error("Error handling message from user %d: %s", user_id, exc)
            await message.reply_text(format_error_message(handle_api_error(exc, "message handling")))

    return handler


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _fetch_image_as_data_url(image_url: str) -> str | None:
    """Fetch an image from a URL and return a data URL (data:image/...;base64,...) or None."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()
            raw = resp.content
            ctype = (resp.headers.get("content-type") or "image/jpeg").split(";")[0].strip()
            if "image" not in ctype.lower():
                return None
            b64 = base64.b64encode(raw).decode("ascii")
            return f"data:{ctype};base64,{b64}"
    except Exception as exc:
        logger.warning("Failed to fetch recipe image from %s: %s", image_url[:60], exc)
        return None


async def _send_typing(message: Message, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send typing indicator; ignore errors so they don't break the flow."""
    with contextlib.suppress(Exception):
        await context.bot.send_chat_action(chat_id=message.chat_id, action=ChatAction.TYPING)


def _task_sync_status_line(orch: TelegramOrchestrator, user_id: int) -> str:
    """Append a one-line sync status after task creation success."""
    if not orch.task_service:
        return ""
    try:
        status = orch.task_service.get_task_sync_status(user_id)
        s = status.get("success_count", 0)
        f = status.get("failed_count", 0)
        return f"\n\n📊 Sync: ✅ {s} successful, ❌ {f} failed — /tasks_status"
    except Exception:
        return ""


async def _route_plain_message(
    orch: TelegramOrchestrator,
    user_id: int,
    text: str,
    message: Message,
    telegram_message_id: int | None,
    context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """
    Route plain messages via LLM (note, task, or both). Returns True if handled.
    """
    if not await ping_joplin_api():
        return False

    existing_tags = []
    try:
        tags = await orch.joplin_client.fetch_tags()
        existing_tags = [t.get("title", "") for t in tags if t.get("title")]
    except Exception as exc:
        logger.warning("Failed to fetch tags: %s", exc)

    urls = extract_urls(text)
    if urls:
        await _send_typing(message, context)
        await message.reply_text("🔗 Fetching link...")
    url_context = await _build_url_context(validated_text=text)

    await _send_typing(message, context)
    await message.reply_text("🤖 Analyzing...")

    folders = await orch.joplin_client.get_folders()
    ctx = {
        "existing_tags": existing_tags,
        "folders": folders,
        "url_context": url_context,
        "user_profile": get_user_profile_context(),
    }

    routing = await orch.llm_orchestrator.process_message_for_routing(text, ctx)

    if routing.status == "NEED_INFO" and routing.question:
        state = {
            "original_message": text,
            "existing_tags": existing_tags,
            "routing_pending": True,
        }
        orch.state_manager.update_state(user_id, state)
        await message.reply_text(f"🤔 {routing.question}")
        return True

    if routing.status != "SUCCESS":
        return False

    # Task only
    if routing.content_type == "task" and routing.task and orch.task_service:
        task = routing.task
        existing = await orch.task_service.detect_duplicate_task(
            task.title, str(user_id), note_index=getattr(orch, "note_index", None)
        )
        if existing:
            task_list_id = orch.task_service.get_task_list_id_for_user(str(user_id))
            if task_list_id:
                await _show_duplicate_task_choice(
                    orch, user_id, existing, task_list_id, task.title,
                    proposed_notes=task.notes or "",
                    proposed_due=task.due_date,
                    message=message,
                )
                return True
        try:
            created = orch.task_service.create_task_with_metadata(
                title=task.title,
                user_id=str(user_id),
                notes=task.notes or "",
                due_date=task.due_date,
            )
        except AppError as exc:
            logger.warning("Failed to create task from routing: %s", exc)
            await message.reply_text(format_error_message(getattr(exc, "user_message", str(exc))))
            return True
        except GoogleAuthError:
            await message.reply_text(format_error_message(
                "🔑 Google token expired or revoked. Use /tasks_connect to re-authenticate."
            ))
            return True
        except Exception as exc:
            logger.warning("Failed to create task from routing: %s", exc)
            has_token = orch.logging_service.load_google_token(str(user_id)) is not None
            if has_token:
                await message.reply_text(
                    format_error_message(f"Failed to create task: {exc}\n\nCheck /tasks_status.")
                )
            else:
                await message.reply_text(
                    format_error_message(
                        f"Failed to create task: {exc}\n\nGoogle Tasks not connected. Use /tasks_connect first."
                    )
                )
            return True
        if created:
            orch.logging_service.log_decision(
                Decision(
                    user_id=user_id,
                    telegram_message_id=telegram_message_id,
                    status="SUCCESS",
                    note_title=task.title,
                    note_body=task.notes or "",
                    tags=[],
                )
            )
            status_line = _task_sync_status_line(orch, user_id)
            await message.reply_text(
                format_success_message(
                    f"✅ Created Google Task: '{task.title}'{status_line}"
                )
            )
        else:
            has_token = orch.logging_service.load_google_token(str(user_id)) is not None
            if has_token:
                await message.reply_text(
                    format_error_message("Failed to create task. Check /tasks_status.")
                )
            else:
                await message.reply_text(
                    format_error_message(
                        "Google Tasks not connected. Use /tasks_connect first."
                    )
                )
        return True

    # Note only or both
    if routing.content_type in ("note", "both") and routing.note:
        note_data = dict(routing.note)
        if routing.content_type == "both" and routing.task:
            task = routing.task
            note_data["body"] = (note_data.get("body") or "") + f"\n\n---\n📋 **Linked Task**: {task.title}"
        # Build a JoplinNoteSchema-like object for _process_llm_response
        class _RoutingNoteResponse:
            status = "SUCCESS"
            note = note_data
            question = None
            log_entry = routing.log_entry

        note_result = await _process_llm_response(
            orch,
            user_id,
            _RoutingNoteResponse(),
            message,
            telegram_message_id,
            clear_state=True,
            url_context=url_context,
            context=context,
        )

        # If both: create task with link to note (FR-034: subtask if in project folder)
        if routing.content_type == "both" and routing.task and orch.task_service:
            note_title = (routing.note or {}).get("title", "Note")
            task = routing.task
            task_notes = f"📝 See Joplin note: {note_title}\n\n{task.notes or ''}".strip()
            folder_id = (routing.note or {}).get("parent_id")
            parent_folder_id, parent_folder_title = None, None
            if folder_id:
                cfg = orch.logging_service.get_google_tasks_config(user_id)
                proj_folder_id = (cfg or {}).get("projects_folder_id")
                proj = await orch.reorg_orchestrator.get_project_folder_for_sync(
                    folder_id, projects_folder_id=proj_folder_id
                )
                if proj:
                    parent_folder_id, parent_folder_title = proj
            existing = await orch.task_service.detect_duplicate_task(
                task.title, str(user_id), note_index=getattr(orch, "note_index", None)
            )
            if existing:
                task_list_id = orch.task_service.get_task_list_id_for_user(str(user_id))
                if task_list_id:
                    await _show_duplicate_task_choice(
                        orch, user_id, existing, task_list_id, task.title,
                        proposed_notes=task_notes,
                        proposed_due=task.due_date,
                        parent_folder_id=parent_folder_id,
                        parent_folder_title=parent_folder_title,
                        message=message,
                    )
                    return True
            try:
                created = orch.task_service.create_task_with_metadata(
                    title=task.title,
                    user_id=str(user_id),
                    notes=task_notes,
                    due_date=task.due_date,
                    parent_folder_id=parent_folder_id,
                    parent_folder_title=parent_folder_title,
                )
            except AppError as exc:
                logger.warning("Failed to create task (both flow): %s", exc)
                await message.reply_text(format_error_message(getattr(exc, "user_message", str(exc))))
                return True
            except GoogleAuthError:
                await message.reply_text(format_error_message(
                    "🔑 Google token expired or revoked. Use /tasks_connect to re-authenticate."
                ))
                return True
            except Exception as exc:
                logger.warning("Failed to create task (both flow): %s", exc)
                has_token = orch.logging_service.load_google_token(str(user_id)) is not None
                if has_token:
                    await message.reply_text(
                        format_error_message(f"Failed to create task: {exc}\n\nCheck /tasks_status.")
                    )
                else:
                    await message.reply_text(
                        format_error_message(
                            f"Failed to create task: {exc}\n\nGoogle Tasks not connected. Use /tasks_connect first."
                        )
                    )
                return True
            if created:
                orch.logging_service.log_decision(
                    Decision(
                        user_id=user_id,
                        status="SUCCESS",
                        note_title=task.title,
                        note_body=task_notes,
                        tags=[],
                    )
                )
                # FR-034: Preserve task_link (joplin_note_id ↔ google_task_id)
                if note_result and note_result.get("note_id") and created:
                    t = created[0]
                    task_list_id = (
                        orch.task_service.get_task_list_id_for_user(str(user_id))
                        if orch.task_service
                        else None
                    )
                    if task_list_id:
                        orch.logging_service.create_task_link(
                            user_id=user_id,
                            joplin_note_id=note_result["note_id"],
                            google_task_id=t.get("id", ""),
                            google_task_list_id=task_list_id,
                            joplin_note_title=note_title,
                            google_task_title=task.title,
                        )
            status_line = _task_sync_status_line(orch, user_id)
            await message.reply_text(
                format_success_message(f"✅ Also created linked Google Task: '{task.title}'{status_line}")
            )
        return True

    return False


async def _handle_new_request(
    orch: TelegramOrchestrator,
    user_id: int,
    text: str,
    message: Message,
    telegram_message_id: int | None,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    force_note: bool = False,
    force_task: bool = False,
    force_recipe: bool = False,
) -> None:
    if force_task:
        # Explicit /task: create exactly one Google Task from the user's text
        if not orch.task_service:
            await message.reply_text(
                "⚠️ Google Tasks integration is not available. "
                "Use /tasks_connect first."
            )
            return
        try:
            # FR-034: If project sync enabled and projects exist, ask "Is this for a project?"
            config = orch.logging_service.get_google_tasks_config(user_id)
            if config and config.get("project_sync_enabled") and orch.reorg_orchestrator:
                proj_folder_id = config.get("projects_folder_id")
                projects = await orch.reorg_orchestrator.get_project_folders(
                    projects_folder_id=proj_folder_id
                )
                if projects:
                    lines = ["Is this task for a project?"]
                    for i, (_fid, title) in enumerate(projects[:10], 1):
                        lines.append(f"{i}. {title}")
                    lines.append("Reply with the number, or tap a button below.")
                    keyboard = []
                    for i, (_fid, title) in enumerate(projects[:8], 1):
                        keyboard.append([
                            InlineKeyboardButton(f"{i}. {title[:30]}", callback_data=f"project_sel_{i - 1}")
                        ])
                    keyboard.append([InlineKeyboardButton("No (top-level)", callback_data="project_sel_no")])
                    orch.state_manager.update_state(user_id, {
                        "awaiting_project_selection": True,
                        "task_text": text,
                        "projects": [[fid, t] for fid, t in projects[:10]],
                    })
                    await message.reply_text(
                        "\n".join(lines),
                        reply_markup=InlineKeyboardMarkup(keyboard),
                    )
                    return

            # US-055: Duplicate check before create
            existing = await orch.task_service.detect_duplicate_task(
                text, str(user_id), note_index=getattr(orch, "note_index", None)
            )
            if existing:
                task_list_id = orch.task_service.get_task_list_id_for_user(str(user_id))
                if task_list_id:
                    await _show_duplicate_task_choice(
                        orch, user_id, existing, task_list_id, text,
                        message=message,
                    )
                    return
            created = orch.task_service.create_task_directly(text, str(user_id))
            if created:
                status_line = _task_sync_status_line(orch, user_id)
                await message.reply_text(format_success_message(
                    f"✅ Created Google Task: '{text[:80]}{'…' if len(text) > 80 else ''}'{status_line}"
                ))
            else:
                has_token = orch.logging_service.load_google_token(str(user_id)) is not None
                if has_token:
                    await message.reply_text(format_error_message("Failed to create Google Task. Check /tasks_status for details."))
                else:
                    await message.reply_text(format_error_message("Failed to create Google Task. Use /tasks_connect to connect your Google account first."))
        except AppError as exc:
            logger.warning("Task creation failed (config/auth): %s", exc)
            await message.reply_text(format_error_message(getattr(exc, "user_message", str(exc))))
        except Exception as exc:
            logger.error("Error creating Google Task: %s", exc, exc_info=True)
            has_token = orch.logging_service.load_google_token(str(user_id)) is not None
            if has_token:
                await message.reply_text(format_error_message(f"Failed to create task: {exc}\n\nCheck /tasks_status for details."))
            else:
                await message.reply_text(format_error_message(
                    f"Failed to create task: {exc}\n\nUse /tasks_connect to connect your Google account first."
                ))
        return

    # Profile queries: respond with stored profile without routing
    if not force_note and not force_task and _is_profile_query(text):
        profile = get_user_profile_context()
        if profile:
            preview = profile[:500] + "…" if len(profile) > 500 else profile
            await message.reply_text(
                f"📋 **Your profile**\n\n{preview}\n\n"
                "Use /profile set &lt;text&gt; to update.",
                parse_mode="HTML",
            )
        else:
            await message.reply_text(
                "You haven't set a profile yet. Use /profile set &lt;your about me&gt; to add one.",
                parse_mode="HTML",
            )
        return

    # Plain messages: use LLM content routing (note, task, or both)
    if not force_note and not force_task:
        routed = await _route_plain_message(
            orch, user_id, text, message, telegram_message_id, context
        )
        if routed:
            return

    logger.info("Processing as Joplin note for user %d", user_id)
    await _send_typing(message, context)
    if not await ping_joplin_api():
        await message.reply_text(
            "❌ I'm ready, but Joplin isn't accessible. "
            "Please make sure Joplin is running with Web Clipper enabled."
        )
        return

    existing_tags = []
    try:
        tags = await orch.joplin_client.fetch_tags()
        existing_tags = [t.get("title", "") for t in tags if t.get("title")]
    except Exception as exc:
        logger.warning("Failed to fetch tags: %s", exc)

    # Status: fetching link when message contains a URL
    urls = extract_urls(text)
    if urls:
        await _send_typing(message, context)
        await message.reply_text("🔗 Fetching link...")
    url_context = await _build_url_context(validated_text=text)

    # /recipe: ensure recipe template is used (pasted text or URL)
    if force_recipe:
        if not url_context or not url_context.get("url"):
            # Pasted recipe text — build synthetic recipe context
            template = template_for_url_type("recipe")
            url_context = {
                "url": "(pasted)",
                "content_type": "recipe",
                "extracted_text": text,
                "template_name": template["template_name"],
                "template_id": template["template_id"],
                "template_instructions": (
                    "Use Template 4 - Recipe. Extract ingredients, preparation, cooking steps, "
                    "and nutrition from the pasted text. Sections: Source (say 'Pasted by user'), "
                    "Ingredients, Preparation, Cooking, Nutrition (estimate if not given), Notes."
                ),
            }
        else:
            # URL was fetched — force recipe format (e.g. paywall fallback)
            url_context = dict(url_context)
            url_context["content_type"] = "recipe"
            if not url_context.get("template_name"):
                template = template_for_url_type("recipe")
                url_context["template_name"] = template["template_name"]
                url_context["template_id"] = template["template_id"]
                url_context["template_instructions"] = template["instructions"]

    # Image for URL notes: always AI-generated (no screenshot, no skip)
    if url_context and url_context.get("url") and url_context.get("url") != "(pasted)":
        url_context["url_was_primary"] = len(text.strip()) < 200

    if url_context and url_context.get("content_type") == "recipe":
        await message.reply_text("🍳 Recipe detected — saving to Resources/🍽️ Recipe and adding an image.")

    await _send_typing(message, context)
    await message.reply_text("🤖 Analyzing...")
    folders = await orch.joplin_client.get_folders()
    ctx = {
        "existing_tags": existing_tags,
        "folders": folders,
        "url_context": url_context,
        "user_profile": get_user_profile_context(),
    }
    llm_response = await orch.llm_orchestrator.process_message(text, ctx)

    await _process_llm_response(
        orch, user_id, llm_response, message, telegram_message_id,
        url_context=url_context, context=context,
    )


async def _handle_project_selection_reply(
    orch: TelegramOrchestrator,
    user_id: int,
    text: str,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """FR-034: Handle user reply to 'Is this task for a project?' (number or 'no')."""
    state = orch.state_manager.get_state(user_id)
    if not state or not state.get("awaiting_project_selection"):
        await message.reply_text("❌ No pending task. Use /task <item> to create a task.")
        return

    task_text = state.get("task_text", "")
    projects = state.get("projects", [])
    if not task_text or not orch.task_service:
        orch.state_manager.clear_state(user_id)
        await message.reply_text(format_error_message("Could not create task."))
        return

    text_lower = text.strip().lower()
    parent_folder_id: str | None = None
    parent_folder_title: str | None = None
    if text_lower not in ("no", "n", "skip", "top-level", "top level"):
        try:
            idx = int(text.strip())
            if 1 <= idx <= len(projects):
                parent_folder_id, parent_folder_title = projects[idx - 1]
        except ValueError:
            pass

    # US-055: Duplicate check before create
    existing = await orch.task_service.detect_duplicate_task(
        task_text, str(user_id), note_index=getattr(orch, "note_index", None)
    )
    if existing:
        task_list_id = orch.task_service.get_task_list_id_for_user(str(user_id))
        if task_list_id:
            orch.state_manager.clear_state(user_id)
            await _show_duplicate_task_choice(
                orch, user_id, existing, task_list_id, task_text,
                parent_folder_id=parent_folder_id,
                parent_folder_title=parent_folder_title,
                message=message,
            )
            return

    orch.state_manager.clear_state(user_id)
    try:
        if parent_folder_id and parent_folder_title:
            created = orch.task_service.create_task_with_metadata(
                title=task_text,
                user_id=str(user_id),
                parent_folder_id=parent_folder_id,
                parent_folder_title=parent_folder_title,
            )
        else:
            created = orch.task_service.create_task_directly(task_text, str(user_id))
    except AppError as exc:
        logger.warning("Failed to create task (project selection reply): %s", exc)
        await message.reply_text(format_error_message(getattr(exc, "user_message", str(exc))))
        return
    except GoogleAuthError:
        await message.reply_text(format_error_message(
            "🔑 Google token expired or revoked. Use /tasks_connect to re-authenticate."
        ))
        return
    except Exception as exc:
        logger.warning("Failed to create task (project selection reply): %s", exc)
        has_token = orch.logging_service.load_google_token(str(user_id)) is not None
        if has_token:
            await message.reply_text(format_error_message(
                f"Failed to create Google Task: {exc}\n\nCheck /tasks_status for details."
            ))
        else:
            await message.reply_text(format_error_message(
                f"Failed to create Google Task: {exc}\n\nUse /tasks_connect first."
            ))
        return

    if created:
        status_line = _task_sync_status_line(orch, user_id)
        await message.reply_text(format_success_message(
            f"✅ Created Google Task: '{task_text[:80]}{'…' if len(task_text) > 80 else ''}'{status_line}"
        ))
    else:
        has_token = orch.logging_service.load_google_token(str(user_id)) is not None
        if has_token:
            await message.reply_text(format_error_message("Failed to create Google Task. Check /tasks_status for details."))
        else:
            await message.reply_text(format_error_message("Failed to create Google Task. Use /tasks_connect first."))


async def _handle_projects_folder_reply(
    orch: TelegramOrchestrator, user_id: int, text: str, message: Message
) -> None:
    """FR-034: Handle reply to set_projects_folder picker (number or 'default')."""
    state = orch.state_manager.get_state(user_id)
    if not state or not state.get("awaiting_projects_folder"):
        await message.reply_text("❌ No pending selection. Use /tasks_set_projects_folder to try again.")
        return

    root_folders = state.get("root_folders", [])
    orch.state_manager.clear_state(user_id)

    text_lower = text.strip().lower()
    if text_lower in ("default", "0"):
        cfg = orch.logging_service.get_google_tasks_config(user_id) or {}
        cfg["projects_folder_id"] = None
        orch.logging_service.save_google_tasks_config(user_id, cfg)
        await message.reply_text("✅ Using default Projects folder (Projects / 01 - projects / project)")
        return

    try:
        idx = int(text.strip())
        if 1 <= idx <= len(root_folders):
            fid, title = root_folders[idx - 1]
            cfg = orch.logging_service.get_google_tasks_config(user_id) or {}
            cfg["projects_folder_id"] = fid
            orch.logging_service.save_google_tasks_config(user_id, cfg)
            await message.reply_text(f"✅ Projects root set to: {title}")
        else:
            await message.reply_text("❌ Invalid number. Use /tasks_set_projects_folder to try again.")
    except ValueError:
        await message.reply_text("❌ Reply with a number or 'default'. Use /tasks_set_projects_folder to try again.")


def _project_selection_callback(orch: TelegramOrchestrator):
    """FR-034: Handle inline button click for project selection."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query or not query.data:
            return
        await query.answer()
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        state = orch.state_manager.get_state(user.id)
        if not state or not state.get("awaiting_project_selection"):
            await query.edit_message_text("❌ Selection expired. Use /task <item> to create a task.")
            return

        task_text = state.get("task_text", "")
        projects = state.get("projects", [])
        if not task_text or not orch.task_service:
            orch.state_manager.clear_state(user.id)
            await query.edit_message_text(format_error_message("Could not create task."))
            return

        data = query.data
        parent_folder_id: str | None = None
        parent_folder_title: str | None = None
        if data != "project_sel_no":
            try:
                idx = int(data.replace("project_sel_", ""))
                if 0 <= idx < len(projects):
                    parent_folder_id, parent_folder_title = projects[idx]
            except (ValueError, IndexError):
                pass

        # US-055: Duplicate check before create
        existing = await orch.task_service.detect_duplicate_task(
            task_text, str(user.id), note_index=getattr(orch, "note_index", None)
        )
        if existing:
            task_list_id = orch.task_service.get_task_list_id_for_user(str(user.id))
            if task_list_id:
                orch.state_manager.clear_state(user.id)
                await _show_duplicate_task_choice(
                    orch, user.id, existing, task_list_id, task_text,
                    parent_folder_id=parent_folder_id,
                    parent_folder_title=parent_folder_title,
                    query=query,
                )
                return

        orch.state_manager.clear_state(user.id)
        try:
            if parent_folder_id and parent_folder_title:
                created = orch.task_service.create_task_with_metadata(
                    title=task_text,
                    user_id=str(user.id),
                    parent_folder_id=parent_folder_id,
                    parent_folder_title=parent_folder_title,
                )
            else:
                created = orch.task_service.create_task_directly(task_text, str(user.id))
        except AppError as exc:
            logger.warning("Failed to create task (project selection callback): %s", exc)
            await query.edit_message_text(format_error_message(getattr(exc, "user_message", str(exc))))
            return
        except GoogleAuthError:
            await query.edit_message_text(format_error_message(
                "🔑 Google token expired or revoked. Use /tasks_connect to re-authenticate."
            ))
            return
        except Exception as exc:
            logger.warning("Failed to create task (project selection callback): %s", exc)
            has_token = orch.logging_service.load_google_token(str(user.id)) is not None
            msg = f"Failed to create Google Task: {exc}\n\nCheck /tasks_status." if has_token else f"Failed to create Google Task: {exc}\n\nUse /tasks_connect first."
            await query.edit_message_text(format_error_message(msg))
            return

        if created:
            status_line = _task_sync_status_line(orch, user.id)
            await query.edit_message_text(format_success_message(
                f"✅ Created Google Task: '{task_text[:80]}{'…' if len(task_text) > 80 else ''}'{status_line}"
            ))
        else:
            has_token = orch.logging_service.load_google_token(str(user.id)) is not None
            msg = "Failed to create Google Task. Check /tasks_status." if has_token else "Failed to create Google Task. Use /tasks_connect first."
            await query.edit_message_text(format_error_message(msg))

    return handler


# ---------------------------------------------------------------------------
# US-055: Duplicate task choice (Edit / Priority / Add Anyway / Cancel)
# ---------------------------------------------------------------------------

async def _show_duplicate_task_choice(
    orch: TelegramOrchestrator,
    user_id: int,
    existing_task: dict,
    task_list_id: str,
    proposed_title: str,
    *,
    proposed_notes: str = "",
    proposed_due: str | None = None,
    parent_folder_id: str | None = None,
    parent_folder_title: str | None = None,
    message: Message | None = None,
    query: Any = None,
) -> None:
    """Show duplicate-task inline keyboard and store state for callback."""
    existing_title = (existing_task.get("title") or "").strip() or "Untitled"
    state = {
        "awaiting_duplicate_choice": True,
        "duplicate_existing_task": {
            "id": existing_task.get("id"),
            "title": existing_title,
            "task_list_id": task_list_id,
        },
        "duplicate_proposed_title": proposed_title,
        "duplicate_proposed_notes": proposed_notes,
        "duplicate_proposed_due": proposed_due,
        "duplicate_parent_folder_id": parent_folder_id,
        "duplicate_parent_folder_title": parent_folder_title,
    }
    orch.state_manager.update_state(user_id, state)
    text = (
        f"A similar task already exists: \"{existing_title[:80]}{'…' if len(existing_title) > 80 else ''}\".\n\n"
        "What do you want to do?"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ Edit", callback_data="dup_edit"),
            InlineKeyboardButton("⭐ Priority", callback_data="dup_priority"),
        ],
        [
            InlineKeyboardButton("➕ Add Anyway", callback_data="dup_add"),
            InlineKeyboardButton("❌ Cancel", callback_data="dup_cancel"),
        ],
    ])
    if query:
        await query.edit_message_text(text, reply_markup=keyboard)
    else:
        await message.reply_text(text, reply_markup=keyboard)


def _duplicate_task_callback(orch: TelegramOrchestrator):
    """US-055: Handle Edit / Priority / Add Anyway / Cancel for duplicate task."""
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query or not query.data:
            return
        await query.answer()
        user = update.effective_user
        if not user or not check_whitelist(user.id):
            return

        state = orch.state_manager.get_state(user.id)
        if not state or not state.get("awaiting_duplicate_choice"):
            await query.edit_message_text("❌ Selection expired. Use /task <item> to create a task.")
            return

        existing = state.get("duplicate_existing_task", {})
        proposed_title = state.get("duplicate_proposed_title", "")
        proposed_notes = state.get("duplicate_proposed_notes", "")
        proposed_due = state.get("duplicate_proposed_due")
        parent_folder_id = state.get("duplicate_parent_folder_id")
        parent_folder_title = state.get("duplicate_parent_folder_title")
        orch.state_manager.clear_state(user.id)

        choice = query.data
        if choice == "dup_cancel":
            await query.edit_message_text("❌ Cancelled. No new task added.")
            return

        if choice == "dup_priority":
            await query.edit_message_text(
                "⭐ To change priority or star this task, open it in Google Tasks."
            )
            return

        if choice == "dup_edit":
            task_id = existing.get("id")
            task_list_id = existing.get("task_list_id")
            if task_id and task_list_id and orch.task_service:
                try:
                    token = orch.logging_service.load_google_token(str(user.id))
                    if not token:
                        await query.edit_message_text(
                            format_error_message("Not connected. Use /tasks_connect first.")
                        )
                        return
                    orch.task_service._set_client_token(str(user.id), token)
                    patch: dict[str, Any] = {"title": proposed_title}
                    if proposed_notes:
                        patch["notes"] = proposed_notes
                    if proposed_due:
                        patch["due"] = proposed_due
                    updated = orch.task_service.tasks_client.update_task(
                        task_id, task_list_id, patch
                    )
                    if orch.task_service.tasks_client.token and orch.task_service.tasks_client.token != token:
                        orch.logging_service.save_google_token(str(user.id), orch.task_service.tasks_client.token)
                    if updated:
                        await query.edit_message_text(
                            format_success_message("✏️ Updated existing task with your new text.")
                        )
                    else:
                        await query.edit_message_text(
                            format_error_message("Could not update task. Try again or add as new.")
                        )
                except Exception as exc:
                    logger.warning("Duplicate edit update failed: %s", exc)
                    await query.edit_message_text(
                        format_error_message("Failed to update task. Try again or add as new.")
                    )
            else:
                await query.edit_message_text(
                    format_error_message("Could not update task. Try again or add as new.")
                )
            return

        if choice == "dup_add":
            if not orch.task_service:
                await query.edit_message_text(format_error_message("Could not create task."))
                return
            try:
                if parent_folder_id and parent_folder_title:
                    created = orch.task_service.create_task_with_metadata(
                        title=proposed_title,
                        user_id=str(user.id),
                        notes=proposed_notes,
                        due_date=proposed_due,
                        parent_folder_id=parent_folder_id,
                        parent_folder_title=parent_folder_title,
                    )
                else:
                    created = orch.task_service.create_task_directly(proposed_title, str(user.id))
            except Exception as exc:
                logger.warning("Failed to create task (dup_add): %s", exc)
                await query.edit_message_text(
                    format_error_message("Failed to create task. Check /tasks_status.")
                )
                return
            if created:
                status_line = _task_sync_status_line(orch, user.id)
                await query.edit_message_text(format_success_message(
                    f"✅ Created Google Task: '{proposed_title[:80]}{'…' if len(proposed_title) > 80 else ''}'{status_line}"
                ))
            else:
                await query.edit_message_text(
                    format_error_message("Failed to create Google Task. Check /tasks_status.")
                )
    return handler


async def _handle_clarification_reply(
    orch: TelegramOrchestrator,
    user_id: int,
    text: str,
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    state = orch.state_manager.get_state(user_id)
    if not state:
        await message.reply_text("❌ No pending clarification found. Please start a new request.")
        return

    original = state.get("original_message", "")
    combined = f"{original}\n\nClarification: {text}"

    # Routing clarification: re-run content routing with combined message
    if state.get("routing_pending"):
        orch.state_manager.clear_state(user_id)
        await _route_plain_message(orch, user_id, combined, message, None, context)
        return

    if is_action_item(combined) and orch.task_service:
        try:
            decision = Decision(user_id=user_id, status="SUCCESS", note_title=combined, note_body="", tags=[])
            created = orch.task_service.create_tasks_from_decision(decision, str(user_id))
            count = len(created) if created else 0
            if count > 0:
                orch.logging_service.log_decision(decision)
                orch.state_manager.clear_state(user_id)
                status_line = _task_sync_status_line(orch, user_id)
                await message.reply_text(format_success_message(f"✅ Created {count} Google Task(s): '{combined}'{status_line}"))
            else:
                has_token = orch.logging_service.load_google_token(str(user_id)) is not None
                if has_token:
                    await message.reply_text(format_error_message("Failed to create Google Task. Check /tasks_status for details."))
                else:
                    await message.reply_text(format_error_message("Failed to create Google Task. Use /tasks_connect to connect your Google account first."))
        except GoogleAuthError:
            await message.reply_text(format_error_message(
                "🔑 Google token expired or revoked. Use /tasks_connect to re-authenticate."
            ))
        except Exception as exc:
            has_token = orch.logging_service.load_google_token(str(user_id)) is not None
            if has_token:
                await message.reply_text(format_error_message(f"Failed to create task: {exc}\n\nCheck /tasks_status for details."))
            else:
                await message.reply_text(format_error_message(
                    f"Failed to create task: {exc}\n\nUse /tasks_connect to connect your Google account first."
                ))
        return

    existing_tags = state.get("existing_tags", [])
    urls = extract_urls(combined)
    if urls:
        await _send_typing(message, context)
        await message.reply_text("🔗 Fetching link...")
    url_context = await _build_url_context(validated_text=combined)
    # URL notes: always use AI image generation (never skip)
    if url_context and url_context.get("url") and url_context.get("url") != "(pasted)":
        url_context["url_was_primary"] = len(combined.strip()) < 200
    if url_context and url_context.get("content_type") == "recipe":
        await message.reply_text("🍳 Recipe detected — saving to Resources/🍽️ Recipe and adding an image.")
    await _send_typing(message, context)
    await message.reply_text("🤖 Analyzing...")
    folders = await orch.joplin_client.get_folders()
    ctx = {
        "existing_tags": existing_tags,
        "folders": folders,
        "url_context": url_context,
        "user_profile": get_user_profile_context(),
    }
    llm_response = await orch.llm_orchestrator.process_message(combined, ctx)
    await _process_llm_response(
        orch, user_id, llm_response, message,
        clear_state=True, url_context=url_context, context=context,
    )


async def _handle_braindump_message(
    orch: TelegramOrchestrator, user_id: int, text: str, message: Message
) -> None:
    from src.handlers.braindump import handle_braindump_message
    await handle_braindump_message(orch, user_id, text, message)


async def _handle_stoic_message(
    orch: TelegramOrchestrator, user_id: int, text: str, message: Message
) -> None:
    from src.handlers.stoic import handle_stoic_message
    await handle_stoic_message(orch, user_id, text, message)


async def _handle_search_message(
    orch: TelegramOrchestrator, user_id: int, text: str, message: Message
) -> None:
    from src.handlers.search import handle_search_selection
    await handle_search_selection(orch, user_id, text, message)


async def _process_llm_response(
    orch: TelegramOrchestrator,
    user_id: int,
    llm_response: Any,
    message: Message,
    telegram_message_id: int | None = None,
    clear_state: bool = False,
    url_context: dict[str, Any] | None = None,
    context: ContextTypes.DEFAULT_TYPE | None = None,
) -> dict[str, Any] | None:
    if llm_response.status == "SUCCESS" and llm_response.note:
        if context:
            await _send_typing(message, context)
        await message.reply_text("📝 Saving to Joplin...")
        note_result = await create_note_in_joplin(
            orch, llm_response.note, url_context=url_context, message=message,
        )
        if note_result:
            if note_result.get("error") == "folder_not_found":
                requested = note_result.get("requested_folder") or "(empty)"
                suggestions = note_result.get("suggestions", [])
                msg = f"❌ I couldn't find folder `{requested}`.\n\n"
                if suggestions:
                    msg += "Try one of these folders:\n"
                    for name in suggestions:
                        msg += f"• {name}\n"
                    msg += "\nReply with one folder name and I'll save the note there."
                else:
                    msg += "Please provide a valid folder name."
                await message.reply_text(msg)
                return None

            note_id = note_result["note_id"]
            tag_info = note_result.get("tag_info", {})

            try:
                await orch.joplin_client.append_log(llm_response.log_entry)
            except Exception as exc:
                logger.warning("Failed to append log: %s", exc)

            decision = Decision(
                user_id=user_id,
                telegram_message_id=telegram_message_id,
                status=llm_response.status,
                folder_chosen=llm_response.note.get("parent_id"),
                note_title=llm_response.note.get("title"),
                note_body=llm_response.note.get("body"),
                tags=llm_response.note.get("tags", []),
                joplin_note_id=note_id,
            )
            orch.logging_service.log_decision(decision)
            _log_tag_creation(orch, user_id, note_id, tag_info)

            if clear_state:
                orch.state_manager.clear_state(user_id)

            _schedule_joplin_sync()

            folder_id = note_result.get("folder_id") or llm_response.note.get("parent_id")
            folder_path = "Unknown"
            if folder_id:
                folder_path = await _build_folder_path(orch, folder_id)

            success_msg = f"✅ Note created: '{llm_response.note['title']}'\n📂 {folder_path}"
            if tag_info.get("all_tags"):
                success_msg += f"\nTags: {_format_tag_display(tag_info)}"
            if note_result.get("image_skipped"):
                reason = note_result.get("image_skipped_reason") or "unknown"
                if len(reason) > 80:
                    reason = reason[:77] + "..."
                success_msg += f"\n\n⚠️ No image could be added ({reason})."
            await message.reply_text(format_success_message(success_msg))
            return note_result
        else:
            await message.reply_text(format_error_message("Failed to create note in Joplin. Please try again."))
            return None

    elif llm_response.status == "NEED_INFO" and llm_response.question:
        state = {
            "original_message": message.text,
            "existing_tags": llm_response.note.get("existing_tags", []) if llm_response.note else [],
            "llm_response": llm_response.dict(),
        }
        orch.state_manager.update_state(user_id, state)
        await message.reply_text(
            "🧠 Second Brain folders: Inbox, Projects, Areas, Resources, Archive.\n\n"
            f"🤔 {llm_response.question}"
        )
        return None
    else:
        logger.error("Unexpected LLM response: %s", llm_response)
        await message.reply_text(format_error_message("I had trouble understanding. Please try rephrasing."))
        return None


async def create_note_in_joplin(
    orch: TelegramOrchestrator,
    note_data: dict[str, Any],
    url_context: dict[str, Any] | None = None,
    message: Message | None = None,
    image_data_url: str | None = None,
) -> dict[str, Any] | None:
    try:
        requested_folder = (note_data.get("parent_id") or "").strip()
        resolved_folder_id, suggestions = await _resolve_folder_id_or_suggestions(
            orch,
            requested_folder,
            note_title=note_data.get("title", ""),
            note_body=note_data.get("body", ""),
        )
        # Recipe notes always go in Resources/🍽️ Recipe (Ressources fallback for French)
        if url_context and url_context.get("content_type") == "recipe":
            for path in RECIPE_FOLDER_PATHS:
                try:
                    resolved_folder_id = await orch.joplin_client.get_or_create_folder_by_path(path)
                    if resolved_folder_id:
                        break
                except Exception as exc:
                    logger.warning("Recipe folder path %s failed: %s", path, exc)
            if not resolved_folder_id:
                resolved_folder_id, _ = await _resolve_folder_id_or_suggestions(
                    orch, "Resources", note_title=note_data.get("title", ""), note_body=note_data.get("body", ""),
                )
        if not resolved_folder_id:
            return {
                "error": "folder_not_found",
                "requested_folder": requested_folder,
                "suggestions": suggestions,
            }

        # Validate after folder resolution so missing/invalid parent_id
        # can be recovered via inference/suggestions.
        normalized_note = dict(note_data)
        normalized_note["parent_id"] = resolved_folder_id
        normalized_note["tags"] = await _ensure_project_status_tag(
            orch,
            resolved_folder_id,
            normalized_note.get("tags", []),
            normalized_note.get("title", ""),
            normalized_note.get("body", ""),
        )
        errors = validate_note_data(normalized_note)
        if errors:
            logger.error("Note validation failed: %s", errors)
            return None

        final_image_data_url: str | None = image_data_url
        image_skipped = False
        image_skipped_reason: str | None = None
        image_failure_reasons: list[str] = []
        if final_image_data_url is None:
            # Always try AI-generated image for URL-based notes (never screenshot, never skip)
            needs_image = (
                (url_context and url_context.get("content_type") == "recipe")
                or (
                    url_context
                    and url_context.get("url")
                    and url_context.get("url") != "(pasted)"
                )
                or (
                    url_context
                    and url_context.get("content_type") == "media"
                    and url_context.get("image_url")
                )
            )
            if needs_image and message:
                await message.reply_text("🖼️ Adding image...")
            # Recipe or generic URL: always use AI-generated image from url context
            if url_context and url_context.get("content_type") == "recipe":
                from src.url_image import generate_url_image
                img_url, gemini_reason = await generate_url_image(
                    url_context, normalized_note.get("title")
                )
                final_image_data_url = img_url
                if gemini_reason:
                    image_failure_reasons.append(f"AI generation ({gemini_reason})")
                    logger.info(
                        "Recipe AI image generation failed for '%s': %s",
                        normalized_note.get("title", "")[:60],
                        gemini_reason,
                    )
            elif (
                final_image_data_url is None
                and url_context
                and url_context.get("url")
                and url_context.get("url") != "(pasted)"
            ):
                from src.url_image import generate_url_image
                img_url, gemini_reason = await generate_url_image(
                    url_context, normalized_note.get("title")
                )
                final_image_data_url = img_url
                if gemini_reason:
                    image_failure_reasons.append(f"AI generation ({gemini_reason})")
                    logger.info(
                        "URL image generation failed for note '%s': %s",
                        normalized_note.get("title", "")[:60],
                        gemini_reason,
                    )
                    if message:
                        await message.reply_text("⚠️ Couldn't generate image for this link.")
            if final_image_data_url is None and url_context and url_context.get("content_type") in ("recipe", "media") and url_context.get("image_url"):
                final_image_data_url = await _fetch_image_as_data_url(url_context["image_url"])
                if final_image_data_url is None:
                    content_type_label = url_context.get("content_type", "url")
                    image_failure_reasons.append(f"{content_type_label} image URL fetch failed")
                    logger.info(
                        "%s image URL fetch failed for '%s'",
                        content_type_label.capitalize(),
                        normalized_note.get("title", "")[:60],
                    )

            if needs_image and final_image_data_url is None:
                image_skipped = True
                image_skipped_reason = "; ".join(image_failure_reasons) if image_failure_reasons else "unknown"
                logger.warning(
                    "Recipe/image not generated for note '%s'. Reasons: %s",
                    normalized_note.get("title", "")[:60],
                    image_skipped_reason,
                )

        note_id = await orch.joplin_client.create_note(
            folder_id=resolved_folder_id,
            title=normalized_note["title"],
            body=normalized_note["body"],
            image_data_url=final_image_data_url,
        )

        tags = normalized_note.get("tags", [])
        tag_info: dict[str, Any] = {"new_tags": [], "existing_tags": [], "all_tags": []}
        if tags:
            tag_info = await orch.joplin_client.apply_tags_and_track_new(note_id, tags)

        return {
            "note_id": note_id,
            "tag_info": tag_info,
            "folder_id": resolved_folder_id,
            "image_skipped": image_skipped,
            "image_skipped_reason": image_skipped_reason,
        }
    except Exception as exc:
        logger.error("Error creating note: %s", exc, exc_info=True)
        return None


async def _resolve_folder_id_or_suggestions(
    orch: TelegramOrchestrator,
    requested_folder: str,
    note_title: str = "",
    note_body: str = "",
) -> tuple[str | None, list[str]]:
    folders = await orch.joplin_client.get_folders()
    if not folders:
        # Self-heal first-run/empty setups by creating a default Inbox folder.
        try:
            created = await orch.joplin_client.create_folder("Inbox")
            created_id = created.get("id")
            if created_id:
                logger.info("Created default folder 'Inbox' (%s)", created_id)
                return created_id, []
        except Exception as exc:
            logger.warning("Failed to auto-create default inbox folder: %s", exc)
        return None, []

    def _fallback_inbox_id() -> str | None:
        # Preferred explicit folder name
        for f in folders:
            title = (f.get("title") or "").strip().lower()
            if title == "inbox":
                return f.get("id")

        # Common variants
        for f in folders:
            title = (f.get("title") or "").strip().lower()
            if title in {"inbox", "00-inbox", "00 inbox"}:
                return f.get("id")
            if "inbox" in title and title.startswith("00"):
                return f.get("id")
            if "inbox" in title:
                return f.get("id")
        return None

    by_id = {f.get("id"): f for f in folders if f.get("id")}
    if requested_folder in by_id:
        return requested_folder, []

    requested_lower = requested_folder.lower()
    by_title_lower = {
        (f.get("title") or "").strip().lower(): f
        for f in folders
        if f.get("title")
    }

    # Exact title match (case-insensitive)
    exact = by_title_lower.get(requested_lower)
    if exact:
        return exact.get("id"), []

    # Empty folder hint -> default inbox immediately.
    if not requested_lower:
        inbox_id = _fallback_inbox_id()
        if inbox_id:
            logger.info("Resolved empty folder hint to inbox folder id '%s'", inbox_id)
            return inbox_id, []

    # Ask LLM to pick the best existing folder when user gives vague input
    # like "I trust you" or a non-existent folder.
    try:
        folder_text = ""
        for f in folders:
            fid = f.get("id")
            title = f.get("title")
            if fid and title:
                folder_text += f"- {fid}: {title}\n"

        note_with_hint = f"Preferred folder from user: {requested_folder}\n\n{note_body or ''}"
        classification = await orch.llm_orchestrator.classify_note(
            note_title or "Untitled",
            note_with_hint,
            folder_text,
        )

        suggested_folder_id = classification.get("suggested_folder_id")
        try:
            confidence = float(classification.get("confidence", 0.0) or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0

        if suggested_folder_id in by_id and confidence >= 0.55:
            logger.info(
                "Resolved folder via LLM: requested='%s' -> folder_id='%s' (confidence=%.2f)",
                requested_folder,
                suggested_folder_id,
                confidence,
            )
            return suggested_folder_id, []
    except Exception as exc:
        logger.warning("LLM folder resolution failed for '%s': %s", requested_folder, exc)

    titles = [f.get("title", "") for f in folders if f.get("title")]
    title_map = {t.lower(): t for t in titles}

    candidates: list[str] = []

    # Prefer substring matches
    for t in titles:
        tl = t.lower()
        if requested_lower and (requested_lower in tl or tl in requested_lower):
            candidates.append(t)

    # Add fuzzy matches
    fuzzy = difflib.get_close_matches(
        requested_lower, list(title_map.keys()), n=5, cutoff=0.3
    )
    for f in fuzzy:
        candidates.append(title_map[f])

    # Deduplicate while preserving order
    deduped: list[str] = []
    seen: set[str] = set()
    for c in candidates:
        if c not in seen:
            seen.add(c)
            deduped.append(c)

    # Ensure 3-5 suggestions when possible
    if len(deduped) < 3:
        for t in sorted(titles):
            if t not in seen:
                deduped.append(t)
                seen.add(t)
            if len(deduped) >= 5:
                break

    # Final fallback: if we still can't resolve, use/create inbox folder.
    inbox_id = _fallback_inbox_id()
    if inbox_id:
        logger.info(
            "Falling back to inbox folder for unresolved hint '%s' (id '%s')",
            requested_folder,
            inbox_id,
        )
        return inbox_id, []

    # No inbox exists yet; create one and continue.
    try:
        created = await orch.joplin_client.create_folder("Inbox")
        created_id = created.get("id")
        if created_id:
            logger.info(
                "Created missing default inbox folder for unresolved hint '%s' (id '%s')",
                requested_folder,
                created_id,
            )
            return created_id, []
    except Exception as exc:
        logger.warning("Failed to create fallback inbox folder: %s", exc)

    return None, deduped[:5]


def _format_tag_display(tag_info: dict[str, Any]) -> str:
    if not tag_info.get("all_tags"):
        return ""
    new_set = set(tag_info.get("new_tags", []))
    parts = [f"{t} (new)" if t in new_set else t for t in tag_info.get("all_tags", [])]
    return ", ".join(parts)


def _log_tag_creation(
    orch: TelegramOrchestrator, user_id: int, note_id: str, tag_info: dict[str, Any]
) -> None:
    try:
        for name in tag_info.get("new_tags", []):
            orch.logging_service.log_tag_creation(user_id=user_id, note_id=note_id, tag_name=name, is_new=True)
        for name in tag_info.get("existing_tags", []):
            orch.logging_service.log_tag_creation(user_id=user_id, note_id=note_id, tag_name=name, is_new=False)
    except Exception as exc:
        logger.warning("Failed to log tag creation: %s", exc)


async def _build_url_context(validated_text: str) -> dict[str, Any]:
    """
    Build enrichment context for the first URL in text.

    Keeps LLM payload bounded while still improving note quality.
    """
    urls = extract_urls(validated_text)
    if not urls:
        return {}

    first_url = urls[0]
    context = await fetch_url_context(first_url)
    if context.get("error"):
        logger.info("URL enrichment fallback for %s: %s", first_url, context["error"])
    else:
        logger.info(
            "URL enrichment ready (%s, template=%s)",
            context.get("domain", "unknown"),
            context.get("template_name", "unknown"),
        )
    return context


async def _build_folder_path(orch: TelegramOrchestrator, folder_id: str) -> str:
    """
    Build a human-readable full path for a folder, e.g. 'Areas / 📓 Journaling / Stoic Journal'.
    Falls back to the folder title alone if the parent chain can't be resolved.  (DEF-031 / US-054)
    """
    try:
        folders = await orch.joplin_client.get_folders()
        by_id = {f["id"]: f for f in folders}
        parts: list[str] = []
        current_id: str | None = folder_id
        visited: set[str] = set()
        while current_id and current_id not in visited:
            folder = by_id.get(current_id)
            if not folder:
                break
            parts.append(folder.get("title", "?"))
            visited.add(current_id)
            current_id = folder.get("parent_id") or None
        parts.reverse()
        return " / ".join(parts) if parts else "Unknown"
    except Exception as exc:
        logger.warning("Could not build folder path for %s: %s", folder_id, exc)
        return "Unknown"


def _schedule_joplin_sync() -> None:
    """
    Schedule a best-effort Joplin sync.

    Debounces concurrent note creations by allowing only one sync task at a time.
    """
    global _sync_task
    if _sync_task and not _sync_task.done():
        return
    _sync_task = asyncio.create_task(_run_joplin_sync())


async def _run_joplin_sync() -> None:
    profile = os.environ.get("JOPLIN_PROFILE")
    if not profile and os.path.isdir("/app/data/joplin"):
        profile = "/app/data/joplin"

    cmd = ["joplin"]
    if profile:
        cmd.extend(["--profile", profile])
    cmd.append("sync")

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=90)
    except FileNotFoundError:
        logger.warning("Joplin CLI not found; skipping post-note sync")
        return
    except TimeoutError:
        logger.warning("Joplin sync timed out after note creation")
        return
    except Exception as exc:
        logger.warning("Failed to run post-note Joplin sync: %s", exc)
        return

    if proc.returncode == 0:
        logger.info("Post-note Joplin sync completed")
    else:
        err = stderr.decode("utf-8", errors="ignore").strip()
        out = stdout.decode("utf-8", errors="ignore").strip()
        logger.warning(
            "Post-note Joplin sync failed (code=%s): %s",
            proc.returncode,
            err or out or "unknown error",
        )


async def _ensure_project_status_tag(
    orch: TelegramOrchestrator,
    folder_id: str,
    tags: Any,
    title: str,
    body: str,
) -> list[str]:
    """
    Ensure project notes have exactly one status/* tag.

    Applies only when note goes into Projects subtree.
    """
    tag_list = [str(t).strip() for t in (tags or []) if str(t).strip()]
    lowered = [t.lower() for t in tag_list]

    # Keep non-status tags and preserve first valid status tag if present.
    existing_status = [t for t in lowered if t in PROJECT_STATUS_TAGS]
    kept_non_status = [t for t in tag_list if t.lower() not in PROJECT_STATUS_TAGS]

    try:
        folders = await orch.joplin_client.get_folders()
    except Exception as exc:
        logger.warning("Could not fetch folders for status-tag policy: %s", exc)
        return tag_list

    by_id = {f.get("id"): f for f in folders if f.get("id")}
    project_root_id = None
    for f in folders:
        norm = normalize_folder_title_for_match(f.get("title") or "")
        if norm in ("projects", "project"):
            project_root_id = f.get("id")
            break
    if not project_root_id:
        return tag_list

    # Walk up parents: if folder is not inside Projects, leave tags untouched.
    cur = folder_id
    in_projects = False
    visited: set[str] = set()
    while cur and cur not in visited:
        visited.add(cur)
        if cur == project_root_id:
            in_projects = True
            break
        node = by_id.get(cur)
        if not node:
            break
        cur = node.get("parent_id", "")
    if not in_projects:
        return tag_list

    status_tag = existing_status[0] if existing_status else _infer_status_tag(title, body)
    final_tags = kept_non_status + [status_tag]

    # Deduplicate while preserving order.
    out: list[str] = []
    seen: set[str] = set()
    for tag in final_tags:
        key = tag.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(tag)
    return out


def _infer_status_tag(title: str, body: str) -> str:
    text = f"{title}\n{body}".lower()
    if any(k in text for k in ["blocked", "on hold", "back burner", "waiting on", "stuck"]):
        return "status/blocked"
    if any(k in text for k in ["done", "completed", "finished", "released", "shipped"]):
        return "status/done"
    if any(k in text for k in ["plan", "planning", "discovery", "research", "backlog", "idea", "todo"]):
        return "status/planning"
    return "status/building"
