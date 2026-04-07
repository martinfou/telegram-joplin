from __future__ import annotations

from pathlib import Path

from src.health.health_joplin import format_week_summary_markdown
from src.health.health_service import HealthService
from src.health.health_store import HealthStore


def _read_fixture(rel: str) -> bytes:
    p = Path(__file__).resolve().parent / "fixtures" / "health" / rel
    return p.read_bytes()


def test_health_import_and_dedupe(tmp_path: Path) -> None:
    db = tmp_path / "health.db"
    store = HealthStore(db_path=str(db))
    svc = HealthService(store=store)

    user_id = 123
    tz = "US/Eastern"

    garmin = _read_fixture("garmin_activities.csv")
    r1 = svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=garmin,
        filename="Activities.csv",
        user_timezone=tz,
        source_hint="garmin",
    )
    assert r1.parsed_rows == 2
    assert r1.inserted_rows == 2
    assert r1.deduped_skipped == 0

    # Re-import same file should dedupe
    r2 = svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=garmin,
        filename="Activities.csv",
        user_timezone=tz,
        source_hint="garmin",
    )
    assert r2.parsed_rows == 2
    assert r2.inserted_rows == 0
    assert r2.deduped_skipped == 2


def test_day_summary_merges_sources(tmp_path: Path) -> None:
    db = tmp_path / "health.db"
    store = HealthStore(db_path=str(db))
    svc = HealthService(store=store)

    user_id = 123
    tz = "US/Eastern"

    svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=_read_fixture("garmin_activities.csv"),
        filename="Activities.csv",
        user_timezone=tz,
        source_hint="garmin",
    )
    svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=_read_fixture("fatsecret_export.csv"),
        filename="FatSecret.csv",
        user_timezone=tz,
        source_hint="fatsecret",
    )
    svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=_read_fixture("arboleaf_export.csv"),
        filename="Arboleaf.csv",
        user_timezone=tz,
        source_hint="arboleaf",
    )

    day = svc.summarize_day(user_id=user_id, date="2026-03-16")
    assert day["activity"]["steps"] == 8123
    assert day["nutrition"]["calories_kcal"] == 950  # 300 + 650
    assert float(day["body"]["weight_kg"]) == 78.4


def test_import_pasted_text_garmin_and_french_weight(tmp_path: Path) -> None:
    db = tmp_path / "health.db"
    store = HealthStore(db_path=str(db))
    svc = HealthService(store=store)
    user_id = 7

    r1 = svc.import_pasted_text(
        user_id=user_id,
        text="Steps: 9,000 · distance 4.5 km · active calories 320",
        default_date="2026-03-20",
    )
    assert r1.parsed_rows == 1
    assert r1.inserted_rows == 1
    assert r1.detected_source == "garmin"

    day = svc.summarize_day(user_id=user_id, date="2026-03-20")
    assert day["activity"]["steps"] == 9000
    assert day["activity"]["distance_km"] == 4.5
    assert day["activity"]["active_calories_kcal"] == 320

    r2 = svc.import_pasted_text(
        user_id=user_id,
        text="poids 78,4 kg",
        default_date="2026-03-20",
        source_hint="arboleaf",
    )
    assert r2.parsed_rows == 1
    assert r2.inserted_rows == 1
    day2 = svc.summarize_day(user_id=user_id, date="2026-03-20")
    assert float(day2["body"]["weight_kg"]) == 78.4


def test_import_pasted_text_dedupe(tmp_path: Path) -> None:
    db = tmp_path / "health.db"
    store = HealthStore(db_path=str(db))
    svc = HealthService(store=store)
    t = "Steps 5000"
    d = "2026-03-21"
    r1 = svc.import_pasted_text(user_id=1, text=t, default_date=d)
    r2 = svc.import_pasted_text(user_id=1, text=t, default_date=d)
    assert r1.inserted_rows == 1
    assert r2.inserted_rows == 0
    assert r2.deduped_skipped == 1


def test_calendar_week_and_iso_label() -> None:
    """Wednesday 2026-03-18 is in ISO week 2026-W12; Mon–Sun bounds."""
    assert HealthService.calendar_week_monday_sunday("2026-03-18") == ("2026-03-16", "2026-03-22")
    assert HealthService.iso_week_label("2026-03-18") == "2026-W12"


def test_summarize_iso_week_matches_fixture_range(tmp_path: Path) -> None:
    db = tmp_path / "health.db"
    store = HealthStore(db_path=str(db))
    svc = HealthService(store=store)
    user_id = 123
    tz = "US/Eastern"
    svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=_read_fixture("garmin_activities.csv"),
        filename="Activities.csv",
        user_timezone=tz,
        source_hint="garmin",
    )
    w = svc.summarize_iso_week(user_id=user_id, any_date="2026-03-17")
    assert w["start_date"] == "2026-03-16"
    assert w["end_date"] == "2026-03-22"
    assert w["rollup"]["workouts"] == 2


def test_weekly_note_markdown_contains_marker() -> None:
    week = {
        "start_date": "2026-03-16",
        "end_date": "2026-03-22",
        "rollup": {
            "workouts": 1,
            "steps": 1000,
            "distance_km": 1.0,
            "active_calories_kcal": 100,
            "avg_calories_kcal": 2000,
            "avg_protein_g": 100,
            "avg_carbs_g": 200,
            "avg_fat_g": 50,
            "weight_trend_kg": -0.5,
        },
    }
    md = format_week_summary_markdown(week, week_label="2026-W12", goal_lines=["- Steps: 1/7 days meeting goal (5000)"])
    assert "2026-W12" in md
    assert "<!-- telegram-health:week:2026-W12 -->" in md
    assert "Goals" in md


def test_health_goals_adherence_steps(tmp_path: Path) -> None:
    db = tmp_path / "health.db"
    store = HealthStore(db_path=str(db))
    svc = HealthService(store=store)

    user_id = 123
    tz = "US/Eastern"

    svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=_read_fixture("garmin_activities.csv"),
        filename="Activities.csv",
        user_timezone=tz,
        source_hint="garmin",
    )
    # 8123 and 4021 steps on two days — goal 4000 so both days count as met
    svc.set_goal(user_id=user_id, metric_key="steps", target_value=4000)
    lines = svc.goal_adherence_for_week(user_id=user_id, end_date="2026-03-17")
    assert any("Steps" in ln and "2/7" in ln for ln in lines)

    assert svc.delete_goal(user_id=user_id, metric_key="steps")
    assert not svc.delete_goal(user_id=user_id, metric_key="steps")
    assert svc.list_goals(user_id) == {}


def test_week_rollup(tmp_path: Path) -> None:
    db = tmp_path / "health.db"
    store = HealthStore(db_path=str(db))
    svc = HealthService(store=store)

    user_id = 123
    tz = "US/Eastern"

    svc.import_csv_bytes(
        user_id=user_id,
        csv_bytes=_read_fixture("garmin_activities.csv"),
        filename="Activities.csv",
        user_timezone=tz,
        source_hint="garmin",
    )
    week = svc.summarize_last_7_days(user_id=user_id, end_date="2026-03-17")
    assert week["rollup"]["workouts"] == 2
    assert week["rollup"]["steps"] == 8123 + 4021

