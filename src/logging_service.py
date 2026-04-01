"""
Logging Service for Telegram-Joplin Bot

Provides SQLite database logging for:
- Telegram conversations
- LLM interactions
- Decision processes
- System debugging

Uses SQLite for simplicity and reliability.
"""

import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TelegramMessage:
    id: int | None = None
    user_id: int = 0
    message_text: str = ""
    response_text: str | None = None
    timestamp: datetime | None = None
    message_type: str = "user"


@dataclass
class LLMInteraction:
    id: int | None = None
    prompt: str = ""
    response: str = ""
    model: str = ""
    temperature: float | None = None
    max_tokens: int | None = None
    confidence_score: float | None = None
    processing_time: float | None = None
    timestamp: datetime | None = None


@dataclass
class Decision:
    id: int | None = None
    user_id: int = 0
    telegram_message_id: int | None = None
    llm_interaction_id: int | None = None
    status: str = ""
    folder_chosen: str | None = None
    note_title: str | None = None
    note_body: str | None = None
    tags: list[str] | None = None
    joplin_note_id: str | None = None
    error_message: str | None = None
    timestamp: datetime | None = None


class LoggingService:
    def __init__(self, db_path: str = "data/bot/bot_logs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database with schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        schema_path = Path(__file__).resolve().parent.parent / "database_schema.sql"
        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, encoding="utf-8") as f:
                schema = f.read()
            conn.executescript(schema)
            # FR-034: Migration for existing DBs - add project_sync_enabled if missing
            try:
                conn.execute(
                    "ALTER TABLE google_tasks_config ADD COLUMN project_sync_enabled BOOLEAN DEFAULT 0"
                )
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists
            # FR-034: Migration - add projects_folder_id for configurable Projects parent
            try:
                conn.execute(
                    "ALTER TABLE google_tasks_config ADD COLUMN projects_folder_id TEXT"
                )
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists
            # Sprint 20 T-007: optional project portfolio in weekly report
            try:
                conn.execute(
                    "ALTER TABLE report_configurations ADD COLUMN include_project_portfolio BOOLEAN DEFAULT 0"
                )
                conn.commit()
            except sqlite3.OperationalError:
                pass  # Column already exists
            conn.commit()

    def _dict_factory(self, cursor, row):
        """Convert row to dict"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def log_telegram_message(self, message: TelegramMessage) -> int | None:
        """Log a Telegram message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO telegram_messages (user_id, message_text, response_text, message_type, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                message.user_id,
                message.message_text,
                message.response_text,
                message.message_type,
                message.timestamp or datetime.now()
            ))
            conn.commit()
            return cursor.lastrowid

    def log_llm_interaction(self, interaction: LLMInteraction) -> int | None:
        """Log an LLM interaction"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO llm_interactions (prompt, response, model, temperature, max_tokens, confidence_score, processing_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                interaction.prompt,
                interaction.response,
                interaction.model,
                interaction.temperature,
                interaction.max_tokens,
                interaction.confidence_score,
                interaction.processing_time,
                interaction.timestamp or datetime.now()
            ))
            conn.commit()
            return cursor.lastrowid

    def log_decision(self, decision: Decision) -> int | None:
        """Log a decision process"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO decisions (user_id, telegram_message_id, llm_interaction_id, status, folder_chosen, note_title, note_body, tags, joplin_note_id, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision.user_id,
                decision.telegram_message_id,
                decision.llm_interaction_id,
                decision.status,
                decision.folder_chosen,
                decision.note_title,
                decision.note_body,
                json.dumps(decision.tags) if decision.tags else None,
                decision.joplin_note_id,
                decision.error_message,
                decision.timestamp or datetime.now()
            ))
            conn.commit()
            return cursor.lastrowid

    def log_system_event(self, level: str, module: str, message: str, extra_data: dict[str, Any] | None = None):
        """Log a system event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_logs (level, module, message, extra_data, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                level,
                module,
                message,
                json.dumps(extra_data) if extra_data else None,
                datetime.now()
            ))
            conn.commit()

    def get_recent_messages(self, user_id: int, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent messages for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM telegram_messages
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()

    def get_decisions_by_status(self, status: str, limit: int = 50) -> list[dict[str, Any]]:
        """Get decisions by status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM decisions
                WHERE status = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (status, limit))
            return cursor.fetchall()

    def get_llm_interactions_by_model(self, model: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get LLM interactions by model"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM llm_interactions
                WHERE model = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (model, limit))
            return cursor.fetchall()

    def cleanup_old_data(self, days: int = 30):
        """Clean up data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Delete old messages
            cursor.execute('DELETE FROM telegram_messages WHERE timestamp < ?', (cutoff_date,))
            deleted_messages = cursor.rowcount

            # Delete old interactions
            cursor.execute('DELETE FROM llm_interactions WHERE timestamp < ?', (cutoff_date,))
            deleted_interactions = cursor.rowcount

            # Delete old decisions
            cursor.execute('DELETE FROM decisions WHERE timestamp < ?', (cutoff_date,))
            deleted_decisions = cursor.rowcount

            # Delete old logs
            cursor.execute('DELETE FROM system_logs WHERE timestamp < ?', (cutoff_date,))
            deleted_logs = cursor.rowcount

            conn.commit()

            self.log_system_event('INFO', 'cleanup', f'Cleaned up old data: {deleted_messages} messages, {deleted_interactions} interactions, {deleted_decisions} decisions, {deleted_logs} logs')

    def get_stats(self) -> dict[str, int]:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            stats = {}
            tables = ['telegram_messages', 'llm_interactions', 'decisions', 'system_logs']

            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                stats[table] = cursor.fetchone()[0]

            return stats

    def save_google_token(self, user_id: str, token: dict[str, Any]):
        """Save Google OAuth token for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO google_tokens (user_id, token_data, updated_at)
                VALUES (?, ?, ?)
            ''', (
                user_id,
                json.dumps(token),
                datetime.now()
            ))
            conn.commit()

    def load_google_token(self, user_id: str) -> dict[str, Any] | None:
        """Load Google OAuth token for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT token_data FROM google_tokens
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (user_id,))
            row = cursor.fetchone()
            if row:
                return json.loads(row['token_data'])
            return None

    def delete_google_token(self, user_id: str):
        """Delete Google OAuth token for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM google_tokens WHERE user_id = ?', (user_id,))
            conn.commit()

    # Google Tasks Configuration Methods

    def save_google_tasks_config(self, user_id: int, config: dict[str, Any]):
        """Save Google Tasks configuration for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO google_tasks_config
                (user_id, enabled, auto_create_tasks, task_list_id, task_list_name,
                 include_only_tagged, task_creation_tags, privacy_mode, project_sync_enabled,
                 projects_folder_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                config.get('enabled', True),
                config.get('auto_create_tasks', True),
                config.get('task_list_id'),
                config.get('task_list_name'),
                config.get('include_only_tagged', False),
                json.dumps(config.get('task_creation_tags', [])),
                config.get('privacy_mode', False),
                config.get('project_sync_enabled', False),
                config.get('projects_folder_id'),
                datetime.now()
            ))
            conn.commit()

    def get_user_ids_with_project_sync_enabled(self) -> list[int]:
        """FR-034: Return user IDs that have project sync enabled (for periodic cleanup)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id FROM google_tasks_config WHERE project_sync_enabled = 1"
            )
            return [row[0] for row in cursor.fetchall()]

    def get_google_tasks_config(self, user_id: int) -> dict[str, Any] | None:
        """Get Google Tasks configuration for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM google_tasks_config WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                row['task_creation_tags'] = json.loads(row.get('task_creation_tags', '[]'))
                return row
            return None

    def delete_google_tasks_config(self, user_id: int):
        """Delete Google Tasks configuration for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM google_tasks_config WHERE user_id = ?', (user_id,))
            conn.commit()

    # Task Link Methods

    def create_task_link(self, user_id: int, joplin_note_id: str, google_task_id: str,
                        google_task_list_id: str, joplin_note_title: str,
                        google_task_title: str) -> int | None:
        """Create a link between a Joplin note and Google Task"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO task_links
                    (user_id, joplin_note_id, google_task_id, google_task_list_id,
                     joplin_note_title, google_task_title)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, joplin_note_id, google_task_id, google_task_list_id,
                      joplin_note_title, google_task_title))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Link already exists
                return None

    def get_task_link(self, user_id: int, joplin_note_id: str) -> dict[str, Any] | None:
        """Get task link for a Joplin note"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM task_links
                WHERE user_id = ? AND joplin_note_id = ?
            ''', (user_id, joplin_note_id))
            return cursor.fetchone()

    def get_all_task_links(self, user_id: int) -> list[dict[str, Any]]:
        """Get all task links for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM task_links
                WHERE user_id = ?
                ORDER BY synced_at DESC
            ''', (user_id,))
            return cursor.fetchall()

    def update_task_link_sync(self, task_link_id: int, new_sync_time: datetime = None):
        """Update last sync time for a task link"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sync_time = new_sync_time or datetime.now()
            cursor.execute('''
                UPDATE task_links
                SET last_sync = ?
                WHERE id = ?
            ''', (sync_time, task_link_id))
            conn.commit()

    def delete_task_link(self, task_link_id: int):
        """Delete a task link"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM task_links WHERE id = ?', (task_link_id,))
            conn.commit()

    # FR-034: Joplin project ↔ Google Tasks parent mapping

    def get_all_project_sync_mappings(self, user_id: int) -> list[dict[str, Any]]:
        """Get all Joplin project folder → Google parent task mappings for a user."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM joplin_project_sync WHERE user_id = ?",
                (user_id,),
            )
            return cursor.fetchall()

    def get_project_sync_mapping(
        self, user_id: int, joplin_folder_id: str
    ) -> dict[str, Any] | None:
        """Get mapping for a Joplin project folder to Google parent task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM joplin_project_sync WHERE user_id = ? AND joplin_folder_id = ?",
                (user_id, joplin_folder_id),
            )
            return cursor.fetchone()

    def save_project_sync_mapping(
        self,
        user_id: int,
        joplin_folder_id: str,
        joplin_folder_title: str,
        google_task_id: str,
        google_task_list_id: str,
    ) -> None:
        """Save or update mapping from Joplin project folder to Google parent task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO joplin_project_sync
                (user_id, joplin_folder_id, joplin_folder_title, google_task_id, google_task_list_id, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, joplin_folder_id) DO UPDATE SET
                    joplin_folder_title = excluded.joplin_folder_title,
                    google_task_id = excluded.google_task_id,
                    google_task_list_id = excluded.google_task_list_id,
                    updated_at = excluded.updated_at
                """,
                (user_id, joplin_folder_id, joplin_folder_title, google_task_id, google_task_list_id, datetime.now()),
            )
            conn.commit()

    def delete_project_sync_mapping(self, user_id: int, joplin_folder_id: str) -> None:
        """Remove mapping when Joplin project folder is deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM joplin_project_sync WHERE user_id = ? AND joplin_folder_id = ?",
                (user_id, joplin_folder_id),
            )
            conn.commit()

    def delete_all_project_sync_mappings(self, user_id: int) -> int:
        """Remove all project sync mappings for a user. Returns count deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM joplin_project_sync WHERE user_id = ?",
                (user_id,),
            )
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    # Task Sync History Methods

    def log_task_sync(self, user_id: int, task_link_id: int | None, google_task_id: str,
                     action: str, old_status: str | None, new_status: str | None,
                     sync_direction: str, sync_result: str, error_message: str | None = None):
        """Log a task synchronization event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO task_sync_history
                (user_id, task_link_id, google_task_id, action, old_status, new_status,
                 sync_direction, sync_result, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, task_link_id, google_task_id, action, old_status, new_status,
                  sync_direction, sync_result, error_message))
            conn.commit()

    def get_sync_history(self, user_id: int, limit: int = 50) -> list[dict[str, Any]]:
        """Get task synchronization history for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM task_sync_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            return cursor.fetchall()

    def get_failed_syncs(self, user_id: int) -> list[dict[str, Any]]:
        """Get failed task synchronization attempts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM task_sync_history
                WHERE user_id = ? AND sync_result = 'failed'
                ORDER BY created_at DESC
            ''', (user_id,))
            return cursor.fetchall()

    def get_successful_syncs(self, user_id: int) -> list[dict[str, Any]]:
        """Get successful task synchronization entries"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM task_sync_history
                WHERE user_id = ? AND sync_result = 'success'
                ORDER BY created_at DESC
            ''', (user_id,))
            return cursor.fetchall()

    def delete_failed_syncs_no_token(self) -> int:
        """Remove failed sync rows that were logged only because user had no Google token.
        Used after BF-001 fix: those were not real sync attempts and should not count as failures.
        Returns number of rows deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM task_sync_history
                WHERE sync_result = 'failed'
                  AND error_message LIKE 'No Google token found for user %'
            ''')
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def log_tag_creation(self, user_id: int, note_id: str, tag_name: str, is_new: bool = False):
        """Log tag creation or application to database for audit trail

        Args:
            user_id: Telegram user ID
            note_id: Joplin note ID the tag was applied to
            tag_name: Name of the tag
            is_new: True if tag was newly created, False if it was existing
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tag_creation_history
                    (user_id, joplin_note_id, tag_name, is_new_tag, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, note_id, tag_name, is_new))
                conn.commit()
                logger.debug(f"Logged tag creation: user={user_id}, note={note_id}, tag={tag_name}, is_new={is_new}")
        except Exception as e:
            logger.error(f"Failed to log tag creation: {e}")

    # Report Configuration Methods

    def save_report_configuration(self, user_id: int, config: dict[str, Any]):
        """Save report configuration for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO report_configurations
                (user_id, enabled, delivery_time, timezone, include_critical, include_high,
                 include_medium, include_low, include_google_tasks, include_clarification_pending,
                 include_project_portfolio, detail_level, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                config.get('enabled', True),
                config.get('delivery_time', '08:00'),
                config.get('timezone') or None,
                config.get('include_critical', True),
                config.get('include_high', True),
                config.get('include_medium', False),
                config.get('include_low', False),
                config.get('include_google_tasks', True),
                config.get('include_clarification_pending', True),
                config.get('include_project_portfolio', False),
                config.get('detail_level', 'detailed'),
                datetime.now()
            ))
            conn.commit()
            logger.debug(f"Saved report configuration for user {user_id}")

    def get_report_configuration(self, user_id: int) -> dict[str, Any] | None:
        """Get report configuration for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = self._dict_factory
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM report_configurations WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                return row
            return None

    def delete_report_configuration(self, user_id: int):
        """Delete report configuration for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM report_configurations WHERE user_id = ?', (user_id,))
            conn.commit()
            logger.debug(f"Deleted report configuration for user {user_id}")

    def log_daily_report(self, user_id: int, report_data: dict[str, Any], report_date: datetime | None = None):
        """Log a daily report generation event"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO daily_reports
                (user_id, report_date, joplin_items_count, google_tasks_count,
                 clarification_items_count, critical_items, high_items, medium_items,
                 low_items, completed_since_last, generated_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                (report_date or datetime.now()).date(),
                report_data.get('joplin_count', 0),
                report_data.get('google_tasks_count', 0),
                report_data.get('clarification_count', 0),
                report_data.get('critical_items', 0),
                report_data.get('high_items', 0),
                report_data.get('medium_items', 0),
                report_data.get('low_items', 0),
                report_data.get('completed_count', 0),
                report_data.get('generated_by', 'scheduled')  # 'scheduled' or 'manual'
            ))
            conn.commit()
            logger.debug(f"Logged daily report for user {user_id}")
