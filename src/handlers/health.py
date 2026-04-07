from __future__ import annotations

import logging
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


def register_health_handlers(application: Any, orch: TelegramOrchestrator) -> None:
    async def health_import_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        msg = update.message
        if not user or not msg:
            return
        if not check_whitelist(user.id):
            await msg.reply_text("❌ Sorry, you're not authorized to use this bot.")
            return

        await msg.reply_text(
            "Send a CSV file with caption `/health_import` (optionally `garmin|fatsecret|arboleaf`), "
            "or use `/health_import_quick <text>` for paste.",
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
                    "Or send a CSV with caption /health_import.",
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
        if not caption.lower().startswith("/health_import"):
            return

        source_hint = _parse_source_arg(caption)

        status = await msg.reply_text("Parsing import…")
        try:
            tg_file = await doc.get_file()
            data = await tg_file.download_as_bytearray()
            user_tz = orch.health_service.user_timezone(user.id, orch.logging_service)
            result = orch.health_service.import_csv_bytes(
                user_id=user.id,
                csv_bytes=bytes(data),
                filename=doc.file_name,
                user_timezone=user_tz,
                source_hint=source_hint,
                message_id=msg.message_id,
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
            note_id = await _sync_weekly_note_after_import(orch, user.id, result)
            if note_id:
                lines.append("")
                lines.append("Weekly Joplin note updated (💪 Health & Fitness → Weekly Health).")
            await status.edit_text("\n".join(lines))
        except Exception as exc:
            logger.exception("Health import failed: %s", exc)
            await status.edit_text(format_error_message("Import failed. Try a different export or source hint."))

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

