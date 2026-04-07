from __future__ import annotations

import contextlib
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.health.health_store import HealthRow, HealthStore
from src.health.normalization import row_hash_from_normalized_row
from src.health.parsers import (
    ParsedHealthRow,
    detect_source_from_csv_header,
    parse_arboleaf_csv,
    parse_fatsecret_csv,
    parse_freeform_health_text,
    parse_garmin_activities_csv,
)
from src.timezone_utils import get_current_date_str, get_user_timezone

logger = logging.getLogger(__name__)

# User-configurable targets via /health_goal (US-057)
GOAL_METRIC_KEYS = frozenset(
    {
        "steps",
        "protein_g",
        "carbs_g",
        "fat_g",
        "calories_kcal",
        "active_calories_kcal",
        "weight_kg",
        "body_fat_pct",
    }
)


@dataclass(frozen=True)
class ImportResult:
    import_id: str
    detected_source: str | None
    parsed_rows: int
    inserted_rows: int
    deduped_skipped: int
    date_count: int
    preview_lines: list[str]


class HealthService:
    def __init__(self, store: HealthStore):
        self.store = store

    def new_import_id(self) -> str:
        return str(uuid.uuid4())

    def import_csv_bytes(
        self,
        *,
        user_id: int,
        csv_bytes: bytes,
        filename: str | None,
        user_timezone: str,
        source_hint: str | None,
        input_type: str = "csv",
        message_id: int | None = None,
    ) -> ImportResult:
        # detect from header
        detected = None
        try:
            header_line = csv_bytes.decode("utf-8-sig", errors="replace").splitlines()[0]
            header_cols = [c.strip() for c in header_line.split(",")]
            detected = detect_source_from_csv_header(header_cols)
        except Exception:
            detected = None

        source = source_hint or detected
        if source not in (None, "garmin", "fatsecret", "arboleaf"):
            source = None

        import_id = self.new_import_id()
        self.store.create_import_event(
            import_id=import_id,
            user_id=user_id,
            source=source,
            input_type=input_type,
            filename=filename,
            message_id=message_id,
        )

        parsed: list[ParsedHealthRow] = []
        if source == "garmin":
            parsed = parse_garmin_activities_csv(csv_bytes, user_timezone)
        elif source == "fatsecret":
            parsed = parse_fatsecret_csv(csv_bytes, user_timezone)
        elif source == "arboleaf":
            parsed = parse_arboleaf_csv(csv_bytes, user_timezone)
        else:
            # try all parsers and pick the one that yields most rows
            candidates = [
                ("garmin", parse_garmin_activities_csv(csv_bytes, user_timezone)),
                ("fatsecret", parse_fatsecret_csv(csv_bytes, user_timezone)),
                ("arboleaf", parse_arboleaf_csv(csv_bytes, user_timezone)),
            ]
            best_source, best_rows = max(candidates, key=lambda x: len(x[1]))
            parsed = best_rows
            source = best_source if parsed else None

        return self._insert_parsed_rows(
            user_id=user_id,
            import_id=import_id,
            parsed=parsed,
            detected_source=source,
        )

    def import_pasted_text(
        self,
        *,
        user_id: int,
        text: str,
        default_date: str,
        source_hint: str | None = None,
        message_id: int | None = None,
    ) -> ImportResult:
        parsed, resolved = parse_freeform_health_text(
            text,
            default_date=default_date,
            source_hint=source_hint,
        )
        import_id = self.new_import_id()
        self.store.create_import_event(
            import_id=import_id,
            user_id=user_id,
            source=resolved or source_hint,
            input_type="text",
            filename=None,
            message_id=message_id,
        )
        return self._insert_parsed_rows(
            user_id=user_id,
            import_id=import_id,
            parsed=parsed,
            detected_source=resolved or source_hint,
        )

    def _insert_parsed_rows(
        self,
        *,
        user_id: int,
        import_id: str,
        parsed: list[ParsedHealthRow],
        detected_source: str | None,
    ) -> ImportResult:
        rows: list[HealthRow] = []
        for r in parsed:
            normalized_for_hash = {
                "date": r.date,
                "source": r.source,
                "row_type": r.row_type,
                "metrics": r.metrics,
                "raw_row": r.raw_row,
            }
            rh = row_hash_from_normalized_row(normalized_for_hash)
            rows.append(
                HealthRow(
                    user_id=user_id,
                    date=r.date,
                    source=r.source,
                    row_type=r.row_type,
                    metrics=r.metrics,
                    raw_row=r.raw_row,
                    confidence=r.confidence,
                    row_hash=rh,
                    import_id=import_id,
                )
            )

        inserted, skipped = self.store.insert_rows(rows)
        dates = sorted({r.date for r in rows})
        preview: list[str] = []
        for r in parsed[:3]:
            preview.append(f"- {r.date} {r.source}/{r.row_type}: {r.metrics}")
        if len(parsed) > 3:
            preview.append(f"- … and {len(parsed) - 3} more")

        return ImportResult(
            import_id=import_id,
            detected_source=detected_source,
            parsed_rows=len(parsed),
            inserted_rows=inserted,
            deduped_skipped=skipped,
            date_count=len(dates),
            preview_lines=preview,
        )

    def summarize_day(self, *, user_id: int, date: str) -> dict[str, Any]:
        rows = self.store.get_rows_for_date(user_id, date)
        by_source_type: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for r in rows:
            by_source_type[(r["source"], r["row_type"])].append(r)

        # Garmin activity: aggregate
        steps = 0
        distance_km = 0.0
        active_kcal = 0
        workouts = 0
        avg_hr_vals: list[int] = []

        for r in by_source_type.get(("garmin", "activity"), []):
            m = r["metrics"] or {}
            if "steps" in m and isinstance(m["steps"], int):
                steps += m["steps"]
            if "distance_km" in m:
                with contextlib.suppress(Exception):
                    distance_km += float(m["distance_km"])
            if "active_calories_kcal" in m and isinstance(m["active_calories_kcal"], int):
                active_kcal += m["active_calories_kcal"]
            if m:
                workouts += 1
            if "avg_hr_bpm" in m and isinstance(m["avg_hr_bpm"], int):
                avg_hr_vals.append(m["avg_hr_bpm"])

        # FatSecret foods: aggregate totals + top items by kcal
        food_rows = by_source_type.get(("fatsecret", "food_item"), [])
        cal = 0
        prot = 0
        carbs = 0
        fat = 0
        items: list[tuple[str, int]] = []
        for r in food_rows:
            m = r["metrics"] or {}
            kcal = m.get("calories_kcal") if isinstance(m.get("calories_kcal"), int) else 0
            cal += kcal
            prot += m.get("protein_g") if isinstance(m.get("protein_g"), int) else 0
            carbs += m.get("carbs_g") if isinstance(m.get("carbs_g"), int) else 0
            fat += m.get("fat_g") if isinstance(m.get("fat_g"), int) else 0
            item = m.get("item") if isinstance(m.get("item"), str) else ""
            if item and kcal:
                items.append((item, kcal))
        items_sorted = sorted(items, key=lambda x: x[1], reverse=True)[:5]

        # Arboleaf latest weigh-in for the day (if multiple, pick last inserted order already)
        weigh_rows = by_source_type.get(("arboleaf", "weigh_in"), [])
        weight_kg = None
        body_fat_pct = None
        bmi = None
        if weigh_rows:
            m = weigh_rows[-1]["metrics"] or {}
            weight_kg = m.get("weight_kg")
            body_fat_pct = m.get("body_fat_pct")
            bmi = m.get("bmi")

        return {
            "date": date,
            "activity": {
                "workouts": workouts,
                "steps": steps or None,
                "distance_km": round(distance_km, 2) if distance_km else None,
                "active_calories_kcal": active_kcal or None,
                "avg_hr_bpm": int(sum(avg_hr_vals) / len(avg_hr_vals)) if avg_hr_vals else None,
            },
            "nutrition": {
                "calories_kcal": cal or None,
                "protein_g": prot or None,
                "carbs_g": carbs or None,
                "fat_g": fat or None,
                "top_items": items_sorted,
            },
            "body": {
                "weight_kg": weight_kg,
                "body_fat_pct": body_fat_pct,
                "bmi": bmi,
            },
            "sources_present": sorted({r["source"] for r in rows}),
        }

    def summarize_last_7_days(self, *, user_id: int, end_date: str) -> dict[str, Any]:
        start_date, end_date = HealthStore.iso_date_range_last_n_days(end_date, 7)
        rows = self.store.get_rows_for_range(user_id, start_date, end_date)

        # Group by day then reuse summarize_day for consistent logic (simple, ok for small data)
        dates = sorted({r["date"] for r in rows})
        days = [self.summarize_day(user_id=user_id, date=d) for d in dates]

        # Basic rollups
        total_workouts = sum((d["activity"]["workouts"] or 0) for d in days)
        total_steps = sum((d["activity"]["steps"] or 0) for d in days)
        total_distance_km = sum((d["activity"]["distance_km"] or 0.0) for d in days)
        total_active_kcal = sum((d["activity"]["active_calories_kcal"] or 0) for d in days)

        # Nutrition averages across days that have nutrition
        nutrition_days = [d for d in days if d["nutrition"]["calories_kcal"] is not None]
        def avg(key: str) -> int | None:
            vals = [int(d["nutrition"][key]) for d in nutrition_days if d["nutrition"][key] is not None]
            return int(sum(vals) / len(vals)) if vals else None

        body_days = [d for d in days if d["body"]["weight_kg"] is not None]
        weight_trend = None
        if len(body_days) >= 2:
            try:
                w0 = float(body_days[0]["body"]["weight_kg"])
                w1 = float(body_days[-1]["body"]["weight_kg"])
                weight_trend = round(w1 - w0, 2)
            except Exception:
                weight_trend = None

        return {
            "start_date": start_date,
            "end_date": end_date,
            "days": days,
            "rollup": {
                "workouts": total_workouts,
                "steps": total_steps or None,
                "distance_km": round(total_distance_km, 2) if total_distance_km else None,
                "active_calories_kcal": total_active_kcal or None,
                "avg_calories_kcal": avg("calories_kcal"),
                "avg_protein_g": avg("protein_g"),
                "avg_carbs_g": avg("carbs_g"),
                "avg_fat_g": avg("fat_g"),
                "weight_trend_kg": weight_trend,
            },
        }

    # Convenience helpers used by handlers
    @staticmethod
    def user_timezone(user_id: int, logging_service: Any) -> str:
        return get_user_timezone(user_id, logging_service)

    @staticmethod
    def today_str(user_id: int, logging_service: Any) -> str:
        return get_current_date_str(user_id, logging_service)

    def set_goal(self, *, user_id: int, metric_key: str, target_value: float) -> None:
        self.store.upsert_goal(user_id=user_id, metric_key=metric_key, target_value=target_value)

    def delete_goal(self, *, user_id: int, metric_key: str) -> bool:
        return self.store.delete_goal(user_id=user_id, metric_key=metric_key)

    def delete_all_goals(self, *, user_id: int) -> int:
        return self.store.delete_all_goals(user_id=user_id)

    def list_goals(self, user_id: int) -> dict[str, float]:
        return self.store.list_goals(user_id)

    def goal_adherence_for_week(self, *, user_id: int, end_date: str) -> list[str]:
        """Human-readable lines for /health_week and /health_goals (7-day window ending end_date)."""
        goals = self.list_goals(user_id)
        if not goals:
            return []

        start_date, end_s = HealthStore.iso_date_range_last_n_days(end_date, 7)
        if end_s != end_date:
            end_date = end_s
        dates = HealthStore.iter_dates_inclusive(start_date, end_date)
        lines: list[str] = []

        for metric, target in sorted(goals.items(), key=lambda x: x[0]):
            if metric not in GOAL_METRIC_KEYS:
                continue
            if metric == "weight_kg":
                w = self._latest_weight_kg_in_range(user_id, start_date, end_date)
                if w is None:
                    lines.append(f"- Weight: no weigh-in this week (goal {target:g} kg)")
                else:
                    delta = round(float(w) - target, 2)
                    sign = "+" if delta > 0 else ""
                    lines.append(f"- Weight: latest {w} kg vs goal {target:g} kg ({sign}{delta} kg)")
                continue

            met = 0
            total = len(dates)
            for d in dates:
                day = self.summarize_day(user_id=user_id, date=d)
                if self._day_meets_goal(day, metric, target):
                    met += 1
            label = self._goal_metric_label(metric)
            lines.append(f"- {label}: {met}/{total} days meeting goal ({target:g})")

        return lines

    @staticmethod
    def _goal_metric_label(metric: str) -> str:
        return {
            "steps": "Steps",
            "protein_g": "Protein",
            "carbs_g": "Carbs",
            "fat_g": "Fat",
            "calories_kcal": "Calories (≤ cap)",
            "active_calories_kcal": "Active calories",
            "body_fat_pct": "Body fat (≤)",
        }.get(metric, metric)

    def _latest_weight_kg_in_range(self, user_id: int, start_date: str, end_date: str) -> float | None:
        rows = self.store.get_rows_for_range(user_id, start_date, end_date)
        latest: tuple[datetime, float] | None = None
        for r in rows:
            if r["row_type"] != "weigh_in":
                continue
            m = r["metrics"] or {}
            w = m.get("weight_kg")
            if w is None:
                continue
            try:
                wf = float(w)
            except (TypeError, ValueError):
                continue
            d = datetime.strptime(r["date"], "%Y-%m-%d")
            if latest is None or d >= latest[0]:
                latest = (d, wf)
        return latest[1] if latest else None

    @staticmethod
    def _day_meets_goal(day: dict[str, Any], metric: str, target: float) -> bool:
        act = day.get("activity") or {}
        nut = day.get("nutrition") or {}
        body = day.get("body") or {}

        if metric == "steps":
            s = act.get("steps")
            return isinstance(s, int) and s >= int(target)
        if metric == "active_calories_kcal":
            c = act.get("active_calories_kcal")
            return isinstance(c, int) and c >= int(target)
        if metric == "protein_g":
            p = nut.get("protein_g")
            return isinstance(p, int) and p >= int(target)
        if metric == "carbs_g":
            p = nut.get("carbs_g")
            return isinstance(p, int) and p >= int(target)
        if metric == "fat_g":
            p = nut.get("fat_g")
            return isinstance(p, int) and p >= int(target)
        if metric == "calories_kcal":
            c = nut.get("calories_kcal")
            return isinstance(c, int) and c <= int(target)
        if metric == "body_fat_pct":
            b = body.get("body_fat_pct")
            try:
                bf = float(b) if b is not None else None
            except (TypeError, ValueError):
                bf = None
            return bf is not None and bf <= float(target)
        return False

