"""Weekly health summary note in Joplin (US-057)."""

from __future__ import annotations

import logging
from typing import Any

from src.exceptions import JoplinAuthError, JoplinConnectionError, JoplinError
from src.health.health_service import HealthService
from src.joplin_client import JoplinClient

logger = logging.getLogger(__name__)

# PARA-style path (matches US-057)
WEEKLY_HEALTH_FOLDER_PARTS = ["01 - Areas", "💪 Health & Fitness", "Weekly Health"]


def format_week_summary_markdown(
    week: dict[str, Any],
    *,
    week_label: str,
    goal_lines: list[str] | None = None,
) -> str:
    """Markdown body for the weekly health note (Joplin)."""
    roll = week.get("rollup") or {}
    start = week.get("start_date", "")
    end = week.get("end_date", "")
    lines: list[str] = [
        f"# {week_label} - Health Summary",
        "",
        f"*Week {start} → {end} (Mon–Sun, your timezone).*",
        "",
        "<!-- telegram-health:week:" + week_label + " -->",
        "",
        "## Activity",
        f"- Workouts: {roll.get('workouts', 0)}",
    ]
    if roll.get("steps") is not None:
        lines.append(f"- Steps (total): {roll['steps']:,}")
    if roll.get("distance_km") is not None:
        lines.append(f"- Distance (total): {roll['distance_km']} km")
    if roll.get("active_calories_kcal") is not None:
        lines.append(f"- Active calories (total): {roll['active_calories_kcal']:,} kcal")
    lines.append("")

    lines.append("## Nutrition")
    if roll.get("avg_calories_kcal") is None:
        lines.append("- *(not provided)*")
    else:
        lines.append(f"- Avg calories: {roll['avg_calories_kcal']:,} kcal/day")
        macro_bits: list[str] = []
        if roll.get("avg_protein_g") is not None:
            macro_bits.append(f"{roll['avg_protein_g']}g protein")
        if roll.get("avg_carbs_g") is not None:
            macro_bits.append(f"{roll['avg_carbs_g']}g carbs")
        if roll.get("avg_fat_g") is not None:
            macro_bits.append(f"{roll['avg_fat_g']}g fat")
        if macro_bits:
            lines.append("- Avg macros: " + " / ".join(macro_bits))
    lines.append("")

    lines.append("## Body")
    if roll.get("weight_trend_kg") is None:
        lines.append("- *(not provided)*")
    else:
        delta = roll["weight_trend_kg"]
        sign = "+" if isinstance(delta, (int, float)) and delta > 0 else ""
        lines.append(f"- Weight trend (first→last weigh-in this week): {sign}{delta} kg")

    if goal_lines:
        lines.append("")
        lines.append("## Goals (this calendar week)")
        lines.extend(goal_lines)

    lines.append("")
    lines.append("---")
    lines.append("*Updated automatically by Telegram-Joplin health import.*")
    return "\n".join(lines)


async def sync_weekly_health_note_to_joplin(
    *,
    joplin: JoplinClient,
    health_service: HealthService,
    user_id: int,
    anchor_date: str,
) -> str | None:
    """
    Create or replace the ISO-week health summary note under Weekly Health.

    Returns Joplin note id on success, or None if Joplin is unavailable (logged).
    """
    try:
        week_label = HealthService.iso_week_label(anchor_date)
        week = health_service.summarize_iso_week(user_id=user_id, any_date=anchor_date)
        goals = health_service.goal_adherence_for_iso_week(user_id=user_id, anchor_date=anchor_date)
        body = format_week_summary_markdown(week, week_label=week_label, goal_lines=goals or None)
        title = f"{week_label} - Health Summary"

        folder_id = await joplin.get_or_create_folder_by_path(WEEKLY_HEALTH_FOLDER_PARTS)
        notes = await joplin.get_notes_in_folder(folder_id)
        existing = next((n for n in notes if (n.get("title") or "").strip() == title), None)

        if existing and existing.get("id"):
            await joplin.update_note(str(existing["id"]), {"body": body})
            logger.info("Updated weekly health note %s for user %s week %s", existing["id"], user_id, week_label)
            return str(existing["id"])

        note_id = await joplin.create_note(folder_id, title, body)
        logger.info("Created weekly health note %s for user %s week %s", note_id, user_id, week_label)
        return note_id
    except (JoplinError, JoplinAuthError, JoplinConnectionError) as exc:
        logger.warning("Weekly health Joplin sync skipped: %s", exc)
        return None
    except Exception:
        logger.exception("Weekly health Joplin sync failed")
        return None
