from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HealthRow:
    user_id: int
    date: str  # YYYY-MM-DD (user timezone)
    source: str  # garmin|fatsecret|arboleaf
    row_type: str  # activity|daily|food_item|weigh_in|sleep|...
    metrics: dict[str, Any]
    raw_row: dict[str, Any]
    confidence: dict[str, float] | None
    row_hash: str
    import_id: str
    created_at: datetime | None = None


class HealthStore:
    """
    Dedicated SQLite store for health imports.

    Stores canonical rows with:
    - row-level dedupe via (user_id, row_hash) unique constraint
    - raw_row JSON for audit/debug
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS health_import_events (
                    import_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    source TEXT,
                    input_type TEXT, -- csv|text|ocr
                    filename TEXT,
                    message_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS health_rows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    source TEXT NOT NULL,
                    row_type TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    raw_row_json TEXT NOT NULL,
                    confidence_json TEXT,
                    row_hash TEXT NOT NULL,
                    import_id TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, row_hash),
                    FOREIGN KEY(import_id) REFERENCES health_import_events(import_id)
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_health_rows_user_date ON health_rows(user_id, date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_health_rows_user_source ON health_rows(user_id, source)")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS health_goals (
                    user_id INTEGER NOT NULL,
                    metric_key TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, metric_key)
                )
                """
            )
            conn.commit()

    def create_import_event(
        self,
        *,
        import_id: str,
        user_id: int,
        source: str | None,
        input_type: str,
        filename: str | None = None,
        message_id: int | None = None,
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO health_import_events
                    (import_id, user_id, source, input_type, filename, message_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (import_id, user_id, source, input_type, filename, message_id),
            )
            conn.commit()

    def insert_rows(self, rows: Iterable[HealthRow]) -> tuple[int, int]:
        """Return (inserted, deduped_skipped)."""
        inserted = 0
        skipped = 0
        with sqlite3.connect(self.db_path) as conn:
            for r in rows:
                try:
                    conn.execute(
                        """
                        INSERT INTO health_rows
                            (user_id, date, source, row_type, metrics_json, raw_row_json, confidence_json, row_hash, import_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            r.user_id,
                            r.date,
                            r.source,
                            r.row_type,
                            json.dumps(r.metrics, sort_keys=True),
                            json.dumps(r.raw_row, sort_keys=True),
                            json.dumps(r.confidence, sort_keys=True) if r.confidence is not None else None,
                            r.row_hash,
                            r.import_id,
                        ),
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    skipped += 1
            conn.commit()
        return inserted, skipped

    def get_last_rows_by_source(self, user_id: int) -> dict[str, dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT source, date, row_type, metrics_json, created_at
                FROM health_rows
                WHERE user_id = ?
                ORDER BY datetime(created_at) DESC
                """,
                (user_id,),
            )
            out: dict[str, dict[str, Any]] = {}
            for row in cur.fetchall():
                src = row["source"]
                if src in out:
                    continue
                out[src] = {
                    "date": row["date"],
                    "row_type": row["row_type"],
                    "metrics": json.loads(row["metrics_json"]),
                    "created_at": row["created_at"],
                }
            return out

    def get_rows_for_date(self, user_id: int, date: str) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT date, source, row_type, metrics_json, raw_row_json, confidence_json
                FROM health_rows
                WHERE user_id = ? AND date = ?
                ORDER BY source, row_type, id
                """,
                (user_id, date),
            )
            rows = []
            for r in cur.fetchall():
                rows.append(
                    {
                        "date": r["date"],
                        "source": r["source"],
                        "row_type": r["row_type"],
                        "metrics": json.loads(r["metrics_json"]),
                        "raw_row": json.loads(r["raw_row_json"]),
                        "confidence": json.loads(r["confidence_json"]) if r["confidence_json"] else None,
                    }
                )
            return rows

    def get_rows_for_range(self, user_id: int, start_date: str, end_date: str) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                """
                SELECT date, source, row_type, metrics_json, raw_row_json, confidence_json
                FROM health_rows
                WHERE user_id = ? AND date >= ? AND date <= ?
                ORDER BY date, source, row_type, id
                """,
                (user_id, start_date, end_date),
            )
            rows = []
            for r in cur.fetchall():
                rows.append(
                    {
                        "date": r["date"],
                        "source": r["source"],
                        "row_type": r["row_type"],
                        "metrics": json.loads(r["metrics_json"]),
                        "raw_row": json.loads(r["raw_row_json"]),
                        "confidence": json.loads(r["confidence_json"]) if r["confidence_json"] else None,
                    }
                )
            return rows

    def upsert_goal(self, *, user_id: int, metric_key: str, target_value: float) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO health_goals (user_id, metric_key, target_value, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, metric_key) DO UPDATE SET
                    target_value = excluded.target_value,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (user_id, metric_key, target_value),
            )
            conn.commit()

    def delete_goal(self, *, user_id: int, metric_key: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "DELETE FROM health_goals WHERE user_id = ? AND metric_key = ?",
                (user_id, metric_key),
            )
            conn.commit()
            return cur.rowcount > 0

    def delete_all_goals(self, *, user_id: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("DELETE FROM health_goals WHERE user_id = ?", (user_id,))
            conn.commit()
            return cur.rowcount

    def list_goals(self, user_id: int) -> dict[str, float]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT metric_key, target_value FROM health_goals WHERE user_id = ? ORDER BY metric_key",
                (user_id,),
            )
            return {str(k): float(v) for k, v in cur.fetchall()}

    @staticmethod
    def iso_date_range_last_n_days(end_date: str, n_days: int) -> tuple[str, str]:
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        start = end - timedelta(days=max(n_days - 1, 0))
        return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    @staticmethod
    def iter_dates_inclusive(start_date: str, end_date: str) -> list[str]:
        d0 = datetime.strptime(start_date, "%Y-%m-%d").date()
        d1 = datetime.strptime(end_date, "%Y-%m-%d").date()
        out: list[str] = []
        d = d0
        while d <= d1:
            out.append(d.strftime("%Y-%m-%d"))
            d += timedelta(days=1)
        return out

