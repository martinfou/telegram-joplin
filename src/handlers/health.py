from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from src.health.health_joplin import sync_weekly_health_note_to_joplin
from src.health.health_service import GOAL_METRIC_KEYS, ImportResult
from src.security_utils import (
    check_whitelist,
    format_error_message,
    format_success_message,
    split_message_for_telegram,
)
from src.telegram_orchestrator import TelegramOrchestrator

logger = logging.getLogger(__name__)

HEALTH_IMPORT_PENDING_KEY = "health_import_pending"
PENDING_IMPORT_TTL = timedelta(minutes=15)


def _clear_health_import_pending(orch: TelegramOrchestrator, user_id: int) -> None:
    st = orch.state_manager.get_state(user_id) or {}
    st.pop(HEALTH_IMPORT_PENDING_KEY, None)
    orch.state_manager.update_state(user_id, st)


def _set_health_import_pending(orch: TelegramOrchestrator, user_id: int, source_hint: str | None) -> None:
    st = orch.state_manager.get_state(user_id) or {}
    st[HEALTH_IMPORT_PENDING_KEY] = {
        "source_hint": source_hint,
        "expires_at": (datetime.now(UTC) + PENDING_IMPORT_TTL).isoformat(),
    }
    orch.state_manager.update_state(user_id, st)


def _get_valid_health_import_pending(orch: TelegramOrchestrator, user_id: int) -> dict[str, Any] | None:
    st = orch.state_manager.get_state(user_id) or {}
    raw = st.get(HEALTH_IMPORT_PENDING_KEY)
    if not isinstance(raw, dict):
        return None
    exp = raw.get("expires_at")
    if isinstance(exp, str):
        try:
            eta = datetime.fromisoformat(exp.replace("Z", "+00:00"))
            if datetime.now(UTC) > eta:
                _clear_health_import_pending(orch, user_id)
                return None
        except (TypeError, ValueError):
            pass
    return raw


def _split_quick_payload(payload: str) -> tuple[str | None, str]:
    """Optional leading `garmin|fatsecret|arboleaf` then body text."""
    p = payload.strip()
    if not p:
        return None, ""
    first, _, rest = p.partition(" ")
    low = first.strip().lower().rstrip(":")
    if low in ("garmin", "fatsecret", "arboleaf"):
        return low, rest.strip()
    return None, p


def _parse_source_arg(text: str | None) -> str | None:
    if not text:
        return None
    t = text.strip().lower()
    if not t:
        return None
    # allow "/health_import garmin"
    parts = t.split()
    if len(parts) >= 2 and parts[0].startswith("/health_import"):
        cand = parts[1].strip().lower()
        return cand if cand in ("garmin", "fatsecret", "arboleaf") else None
    return None


def _format_day_summary(day: dict[str, Any]) -> str:
    date = day["date"]
    lines: list[str] = [f"📈 Health — {date}", ""]

    act = day.get("activity") or {}
    lines.append("🏃 Activity (Garmin)")
    if not any(act.get(k) is not None for k in ("steps", "distance_km", "active_calories_kcal", "avg_hr_bpm")):
        lines.append("- (not provided)")
    else:
        if act.get("steps") is not None:
            lines.append(f"- Steps: {act['steps']:,}")
        if act.get("distance_km") is not None:
            lines.append(f"- Distance: {act['distance_km']} km")
        if act.get("active_calories_kcal") is not None:
            lines.append(f"- Active calories: {act['active_calories_kcal']:,} kcal")
        if act.get("avg_hr_bpm") is not None:
            lines.append(f"- Avg HR: {act['avg_hr_bpm']} bpm")
    lines.append("")

    nut = day.get("nutrition") or {}
    lines.append("🍽️ Nutrition (FatSecret)")
    if not any(nut.get(k) is not None for k in ("calories_kcal", "protein_g", "carbs_g", "fat_g")):
        lines.append("- (not provided)")
    else:
        if nut.get("calories_kcal") is not None:
            lines.append(f"- Calories: {nut['calories_kcal']:,} kcal")
        macros = []
        if nut.get("protein_g") is not None:
            macros.append(f"{nut['protein_g']}g protein")
        if nut.get("carbs_g") is not None:
            macros.append(f"{nut['carbs_g']}g carbs")
        if nut.get("fat_g") is not None:
            macros.append(f"{nut['fat_g']}g fat")
        if macros:
            lines.append("- Macros: " + " / ".join(macros))
        top = nut.get("top_items") or []
        if top:
            lines.append("- Top foods:")
            for name, kcal in top[:5]:
                lines.append(f"  - {name} ({kcal} kcal)")
    lines.append("")

    body = day.get("body") or {}
    lines.append("⚖️ Body (Arboleaf)")
    if not any(body.get(k) is not None for k in ("weight_kg", "body_fat_pct", "bmi")):
        lines.append("- (not provided)")
    else:
        if body.get("weight_kg") is not None:
            lines.append(f"- Weight: {body['weight_kg']} kg")
        if body.get("body_fat_pct") is not None:
            lines.append(f"- Body fat: {body['body_fat_pct']}%")
        if body.get("bmi") is not None:
            lines.append(f"- BMI: {body['bmi']}")

    return "\n".join(lines).strip()


def _format_week_summary(week: dict[str, Any]) -> str:
    roll = week.get("rollup") or {}
    lines = [f"📈 Health Week — {week['start_date']} → {week['end_date']}", ""]
    lines.append("🏃 Activity")
    lines.append(f"- Workouts: {roll.get('workouts', 0)}")
    if roll.get("steps") is not None:
        lines.append(f"- Steps: {roll['steps']:,}")
    if roll.get("distance_km") is not None:
        lines.append(f"- Distance: {roll['distance_km']} km")
    if roll.get("active_calories_kcal") is not None:
        lines.append(f"- Active calories: {roll['active_calories_kcal']:,} kcal")
    lines.append("")

    lines.append("🍽️ Nutrition")
    if roll.get("avg_calories_kcal") is None:
        lines.append("- (not provided)")
    else:
        lines.append(f"- Avg calories: {roll['avg_calories_kcal']:,} kcal/day")
        macro_bits = []
        if roll.get("avg_protein_g") is not None:
            macro_bits.append(f"{roll['avg_protein_g']}g protein")
        if roll.get("avg_carbs_g") is not None:
            macro_bits.append(f"{roll['avg_carbs_g']}g carbs")
        if roll.get("avg_fat_g") is not None:
            macro_bits.append(f"{roll['avg_fat_g']}g fat")
        if macro_bits:
            lines.append("- Avg macros: " + " / ".join(macro_bits))
    lines.append("")

    lines.append("⚖️ Body")
    if roll.get("weight_trend_kg") is None:
        lines.append("- (not provided)")
    else:
        delta = roll["weight_trend_kg"]
        sign = "+" if isinstance(delta, (int, float)) and delta > 0 else ""
        lines.append(f"- Weight trend: {sign}{delta} kg")
    return "\n".join(lines).strip()


async def _sync_weekly_note_after_import(
    orch: TelegramOrchestrator,
    user_id: int,
    result: ImportResult,
) -> str | None:
    if result.parsed_rows == 0:
        return None
    anchor = result.date_max or result.date_min or orch.health_service.today_str(user_id, orch.logging_service)
    return await sync_weekly_health_note_to_joplin(
        joplin=orch.joplin_client,
        health_service=orch.health_service,
        user_id=user_id,
        anchor_date=anchor,
    )


def _looks_like_csv(doc: Any) -> bool:
    fn = (getattr(doc, "file_name", None) or "").lower()
    mime = (getattr(doc, "mime_type", None) or "").lower()
    return fn.endswith(".csv") or "csv" in mime or mime in ("text/plain", "application/vnd.ms-excel")


async def _run_health_csv_import(
    orch: TelegramOrchestrator,
    user_id: int,
    msg: Any,
    doc: Any,
    source_hint: str | None,
    status_msg: Any,
) -> None:
    try:
        tg_file = await doc.get_file()
        data = await tg_file.download_as_bytearray()
        user_tz = orch.health_service.user_timezone(user_id, orch.logging_service)
        result = orch.health_service.import_csv_bytes(
            user_id=user_id,
            csv_bytes=bytes(data),
            filename=getattr(doc, "file_name", None),
            user_timezone=user_tz,
            source_hint=source_hint,
            message_id=getattr(msg, "message_id", None),
        )
        lines = [
            format_success_message("Import saved."),
            f"Detected: {result.detected_source or 'unknown'}",
            f"Parsed: {result.parsed_rows} row(s) covering {result.date_count} day(s)",
            f"Inserted: {result.inserted_rows} (deduped skipped: {result.deduped_skipped})",
            "",
            "Preview:",
            *(result.preview_lines or ["(no rows)"]),
        ]
        note_id = await _sync_weekly_note_after_import(orch, user_id, result)
        if note_id:
            lines.append("")
            lines.append("Weekly Joplin note updated (💪 Health & Fitness → Weekly Health).")
        await status_msg.edit_text("\n".join(lines))
    except Exception as exc:
        logger.exception("Health import failed: %s", exc)
        await status_msg.edit_text(format_error_message("Import failed. Try a different export or source hint."))


async def try_health_import_from_photo(
    orch: TelegramOrchestrator,
    update: Update,
    _context: ContextTypes.DEFAULT_TYPE,
) -> bool:
    """
    Health screenshot: OCR via Gemini, then same parse path as /health_import_quick.

    Activates when caption starts with /health_import OR user has health_import_pending
    (after /health_import). Returns True if this message was handled (including errors).
    """
    message = update.message
    user = update.effective_user
    if not message or not message.photo or not user:
        return False

    cap = (message.caption or "").strip().lower()
    pending = _get_valid_health_import_pending(orch, user.id)

    if not cap.startswith("/health_import") and not pending:
        return False

    if cap.startswith("/health_import"):
        _clear_health_import_pending(orch, user.id)
        source_hint = _parse_source_arg(message.caption or "")
    else:
        pend = pending or {}
        sh = pend.get("source_hint")
        source_hint = sh if isinstance(sh, str) and sh in ("garmin", "fatsecret", "arboleaf") else None
        _clear_health_import_pending(orch, user.id)

    from src.handlers.photo import (  # noqa: PLC0415 — avoid import cycle with photo handler
        _MAX_IMAGE_SIZE_BYTES,
        _MIN_IMAGE_SIZE_BYTES,
        _detect_image_mime,
    )
    from src.ocr_service import extract_text_from_image

    photo = message.photo[-1]
    photo_file = await photo.get_file()
    image_bytes = await photo_file.download_as_bytearray()
    image_data = bytes(image_bytes)
    mime_type = _detect_image_mime(image_data)

    if len(image_data) < _MIN_IMAGE_SIZE_BYTES:
        await message.reply_text(format_error_message("Image too small. Send a clearer screenshot."))
        return True
    if len(image_data) > _MAX_IMAGE_SIZE_BYTES:
        await message.reply_text(format_error_message("Image too large (max 20 MB)."))
        return True

    status = await message.reply_text("🔍 Reading health screenshot…")
    try:

        async def _status_cb(_msg: str) -> None:
            pass

        ocr_result = await extract_text_from_image(
            image_data, mime_type=mime_type, status_callback=_status_cb
        )
        if not ocr_result:
            await status.edit_text(
                format_error_message(
                    "OCR failed. Set GEMINI_API_KEY for screenshots, or use /health_import_quick with paste.",
                )
            )
            return True

        raw_text = (ocr_result.get("text") or "").strip()
        summary = (ocr_result.get("summary") or "").strip()
        if summary and summary.lower() not in raw_text.lower():
            body = f"{raw_text}\n{summary}".strip() if raw_text else summary
        else:
            body = raw_text

        if not body:
            await status.edit_text(
                format_error_message(
                    "No text found in the image. Try a clearer screenshot or /health_import_quick.",
                )
            )
            return True

        today = orch.health_service.today_str(user.id, orch.logging_service)
        result = orch.health_service.import_pasted_text(
            user_id=user.id,
            text=body,
            default_date=today,
            source_hint=source_hint,
            message_id=message.message_id,
            input_type="ocr",
        )
        if result.parsed_rows == 0:
            await status.edit_text(
                format_error_message(
                    "Could not parse health data from the screenshot. "
                    "Try /health_import_quick with pasted text, or send a CSV export.",
                )
            )
            return True

        lines = [
            format_success_message("Import saved (from screenshot)."),
            f"Detected: {result.detected_source or 'unknown'}",
            f"Parsed: {result.parsed_rows} row(s) covering {result.date_count} day(s)",
            f"Inserted: {result.inserted_rows} (deduped skipped: {result.deduped_skipped})",
            "",
            "Preview:",
            *(result.preview_lines or ["(no rows)"]),
        ]
        note_id = await _sync_weekly_note_after_import(orch, user.id, result)
        if note_id:
            lines.append("")
            lines.append("Weekly Joplin note updated (💪 Health & Fitness → Weekly Health).")
        await status.edit_text("\n".join(lines))
        return True
    except Exception as exc:
        logger.exception("Health OCR import failed: %s", exc)
        await status.edit_text(format_error_message("Health screenshot import failed."))
        return True


def register_health_handlers(application: Any, orch: TelegramOrchestrator) -> None:
    async def health_import_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        text = (msg.text or "").strip()
        parts = text.split()
        if len(parts) >= 2 and parts[1].lower() == "cancel":
            _clear_health_import_pending(orch, user.id)
            await msg.reply_text("Health import mode cancelled.")
            return

        source_hint: str | None = None
        if len(parts) >= 2:
            cand = parts[1].strip().lower()
            if cand in ("garmin", "fatsecret", "arboleaf"):
                source_hint = cand

        _set_health_import_pending(orch, user.id, source_hint)
        extra = f"\nOptional source hint saved: {source_hint}." if source_hint else ""
        await msg.reply_text(
            "Ready for health import.\n\n"
            "Send your .csv or a screenshot as the next message — no caption needed.\n"
            "Or use caption /health_import on the file or photo if your app allows.\n\n"
            "/health_import cancel — abort (expires in ~15 min)."
            + extra,
            parse_mode=None,
        )

    async def health_import_quick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        text = msg.text or ""
        parts = text.split(None, 1)
        payload = parts[1] if len(parts) > 1 else ""
        hint, body = _split_quick_payload(payload)
        if not body.strip():
            await msg.reply_text(format_error_message("Paste text after the command."))  # type: ignore[arg-type]
            return

        today = orch.health_service.today_str(user.id, orch.logging_service)
        result = orch.health_service.import_pasted_text(
            user_id=user.id,
            text=body,
            default_date=today,
            source_hint=hint,
            message_id=msg.message_id,
        )
        if result.parsed_rows == 0:
            await msg.reply_text(
                format_error_message(
                    "Could not parse that text. Try: `garmin` — steps, distance km, calories; "
                    "`fatsecret` — calories / macros; `arboleaf` — weight kg, body fat. "
                    "Or run /health_import then send the .csv (no caption), "
                    "or send a CSV with caption /health_import.",
                )
            )
            return
        lines = [
            format_success_message("Import saved."),
            f"Detected: {result.detected_source or 'unknown'}",
            f"Parsed: {result.parsed_rows} row(s) covering {result.date_count} day(s)",
            f"Inserted: {result.inserted_rows} (deduped skipped: {result.deduped_skipped})",
            "",
            "Preview:",
            *(result.preview_lines or ["(no rows)"]),
        ]
        note_id = await _sync_weekly_note_after_import(orch, user.id, result)
        if note_id:
            lines.append("")
            lines.append("Weekly Joplin note updated (💪 Health & Fitness → Weekly Health).")
        await msg.reply_text("\n".join(lines))

    async def _handle_import_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            return
        doc = msg.document
        if not doc:
            return

        caption = (msg.caption or "").strip()
        cap_low = caption.lower()
        pending = _get_valid_health_import_pending(orch, user.id)

        if cap_low.startswith("/health_import"):
            _clear_health_import_pending(orch, user.id)
            source_hint = _parse_source_arg(caption)
        elif pending:
            if not _looks_like_csv(doc):
                await msg.reply_text(
                    "Waiting for a health export. Send a .csv file, a screenshot, or /health_import cancel.",
                )
                return
            source_hint = pending.get("source_hint")
            if isinstance(source_hint, str) and source_hint not in ("garmin", "fatsecret", "arboleaf"):
                source_hint = None
            _clear_health_import_pending(orch, user.id)
        else:
            return

        status = await msg.reply_text("Parsing import…")
        await _run_health_csv_import(orch, user.id, msg, doc, source_hint, status)

    async def health_today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return
        date = orch.health_service.today_str(user.id, orch.logging_service)
        day = orch.health_service.summarize_day(user_id=user.id, date=date)
        text = _format_day_summary(day)
        for chunk in split_message_for_telegram(text):
            await msg.reply_text(chunk)

    async def health_week_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return
        end = orch.health_service.today_str(user.id, orch.logging_service)
        week = orch.health_service.summarize_last_7_days(user_id=user.id, end_date=end)
        text = _format_week_summary(week)
        goal_lines = orch.health_service.goal_adherence_for_week(user_id=user.id, end_date=end)
        if goal_lines:
            text = text + "\n\n🎯 Goals (last 7 days)\n" + "\n".join(goal_lines)
        for chunk in split_message_for_telegram(text):
            await msg.reply_text(chunk)

    async def health_goal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return
        text_raw = (msg.text or "").strip()
        parts = text_raw.split(None, 1)
        payload = parts[1].strip() if len(parts) > 1 else ""
        tokens = payload.split()
        if not tokens:
            await msg.reply_text(
                "Usage:\n"
                "`/health_goal <metric> <value>` — set a target\n"
                "`/health_goal delete <metric>` — remove one goal\n"
                "`/health_goal delete all` — remove all goals\n\n"
                f"Metrics: {', '.join(sorted(GOAL_METRIC_KEYS))}\n"
                "Examples: `/health_goal steps 10000`, `/health_goal protein_g 160`, "
                "`/health_goal calories_kcal 2200` (daily cap).",
            )
            return
        if tokens[0].lower() == "delete":
            if len(tokens) < 2:
                await msg.reply_text("Specify a metric to delete or `all`.")
                return
            if tokens[1].lower() == "all":
                n = orch.health_service.delete_all_goals(user_id=user.id)
                await msg.reply_text(f"Removed {n} goal(s).")
                return
            mk = tokens[1].lower()
            if mk not in GOAL_METRIC_KEYS:
                await msg.reply_text("Unknown metric.")
                return
            ok = orch.health_service.delete_goal(user_id=user.id, metric_key=mk)
            await msg.reply_text("Removed that goal." if ok else "No goal was set for that metric.")
            return
        if len(tokens) < 2:
            await msg.reply_text("Need both metric and value, e.g. `/health_goal steps 10000`.")
            return
        mk = tokens[0].lower()
        if mk not in GOAL_METRIC_KEYS:
            await msg.reply_text(f"Unknown metric. Choose from: {', '.join(sorted(GOAL_METRIC_KEYS))}")
            return
        try:
            val = float(tokens[1].replace(",", "."))
        except ValueError:
            await msg.reply_text("Invalid number for target value.")
            return
        orch.health_service.set_goal(user_id=user.id, metric_key=mk, target_value=val)
        await msg.reply_text(f"Goal saved: {mk} = {val:g}")

    async def health_goals_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return
        goals = orch.health_service.list_goals(user.id)
        if not goals:
            await msg.reply_text(
                "No goals yet. Set targets with `/health_goal steps 10000`, `/health_goal protein_g 160`, etc.",
            )
            return
        end = orch.health_service.today_str(user.id, orch.logging_service)
        lines = ["Your goals:"]
        for k in sorted(goals):
            lines.append(f"- {k}: {goals[k]:g}")
        lines.append("")
        lines.append("Last 7 days:")
        lines.extend(orch.health_service.goal_adherence_for_week(user_id=user.id, end_date=end))
        out = "\n".join(lines)
        for chunk in split_message_for_telegram(out):
            await msg.reply_text(chunk)

    async def health_last_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return
        last = orch.health_store.get_last_rows_by_source(user.id)
        if not last:
            await msg.reply_text("No health data saved yet.")
            return
        lines = ["Last captured per source:"]
        for src, info in last.items():
            lines.append(f"- {src}: {info.get('date')} ({info.get('row_type')})")
        await msg.reply_text("\n".join(lines))

    application.add_handler(CommandHandler("health_import", health_import_cmd))
    application.add_handler(CommandHandler("health_import_quick", health_import_quick_cmd))
    application.add_handler(CommandHandler("health_today", health_today_cmd))
    application.add_handler(CommandHandler("health_week", health_week_cmd))
    application.add_handler(CommandHandler("health_goal", health_goal_cmd))
    application.add_handler(CommandHandler("health_goals", health_goals_cmd))
    application.add_handler(CommandHandler("health_last", health_last_cmd))

    # CSV uploads for /health_import via caption
    application.add_handler(MessageHandler(filters.Document.ALL, _handle_import_document))

    logger.info("Health handlers registered")

