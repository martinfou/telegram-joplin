"""
State Manager for Conversation State Persistence
Manages user conversation states for the Telegram bot.
"""

import json
import logging
import sqlite3
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

class StateManager:
    """Manages conversation state for users"""

    def __init__(self, db_path: str = "data/bot/conversation_state.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        with self._lock:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create states table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_states (
                    user_id INTEGER PRIMARY KEY,
                    state TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create index for performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_states_updated
                ON user_states(updated_at)
            ''')

            conn.commit()
            conn.close()

    def get_state(self, user_id: int) -> dict[str, Any] | None:
        """Get current state for a user"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT state FROM user_states WHERE user_id = ?",
                    (user_id,)
                )

                row = cursor.fetchone()
                conn.close()

                if row:
                    return json.loads(row[0])

                return None

            except (sqlite3.Error, json.JSONDecodeError) as e:
                logger.error(f"Error getting state for user {user_id}: {e}")
                return None

    def get_state_updated_at(self, user_id: int) -> str | None:
        """Return updated_at timestamp for user's state, or None if no state."""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT updated_at FROM user_states WHERE user_id = ?",
                    (user_id,),
                )
                row = cursor.fetchone()
                conn.close()
                return row[0] if row else None
            except sqlite3.Error as e:
                logger.error(f"Error getting state updated_at for user {user_id}: {e}")
                return None

    def update_state(self, user_id: int, state: dict[str, Any]) -> bool:
        """Update or create state for a user"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                state_json = json.dumps(state)

                # Use INSERT OR REPLACE to handle both insert and update
                cursor.execute('''
                    INSERT OR REPLACE INTO user_states (user_id, state, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, state_json))

                conn.commit()
                conn.close()

                logger.info(f"Updated state for user {user_id}")
                return True

            except (sqlite3.Error, json.JSONDecodeError) as e:
                logger.error(f"Error updating state for user {user_id}: {e}")
                return False

    def clear_state(self, user_id: int) -> bool:
        """Clear state for a user"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("DELETE FROM user_states WHERE user_id = ?", (user_id,))

                deleted = cursor.rowcount > 0
                conn.commit()
                conn.close()

                if deleted:
                    logger.info(f"Cleared state for user {user_id}")
                else:
                    logger.debug(f"No state found to clear for user {user_id}")

                return True

            except sqlite3.Error as e:
                logger.error(f"Error clearing state for user {user_id}: {e}")
                return False

    def has_pending_state(self, user_id: int) -> bool:
        """Check if user has a pending state"""
        state = self.get_state(user_id)
        return state is not None

    def cleanup_old_states(self, days_old: int = 7) -> int:
        """Clean up states older than specified days"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute(f'''
                    DELETE FROM user_states
                    WHERE updated_at < datetime('now', '-{days_old} days')
                ''')

                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()

                if deleted_count > 0:
                    logger.info(f"Cleaned up {deleted_count} old states")

                return deleted_count

            except sqlite3.Error as e:
                logger.error(f"Error cleaning up old states: {e}")
                return 0

    def get_all_active_users(self) -> list[int]:
        """Get list of all users with active states"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute("SELECT user_id FROM user_states")
                rows = cursor.fetchall()
                conn.close()

                return [row[0] for row in rows]

            except sqlite3.Error as e:
                logger.error(f"Error getting active users: {e}")
                return []

    def migrate_from_dict(self, dict_states: dict[int, dict[str, Any]]) -> bool:
        """Migrate states from in-memory dict to database (for transition)"""
        success = True
        for user_id, state in dict_states.items():
            if not self.update_state(user_id, state):
                success = False

        return success

# Simple in-memory fallback for development/testing
class InMemoryStateManager:
    """Simple in-memory state manager for testing"""

    def __init__(self):
        self._states: dict[int, tuple[dict[str, Any], str]] = {}
        self._lock = threading.Lock()

    def get_state(self, user_id: int) -> dict[str, Any] | None:
        with self._lock:
            entry = self._states.get(user_id)
            return entry[0] if entry else None

    def get_state_updated_at(self, user_id: int) -> str | None:
        with self._lock:
            entry = self._states.get(user_id)
            return entry[1] if entry else None

    def update_state(self, user_id: int, state: dict[str, Any]) -> bool:
        with self._lock:
            now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
            self._states[user_id] = (state, now)
            return True

    def clear_state(self, user_id: int) -> bool:
        with self._lock:
            self._states.pop(user_id, None)
            return True

    def has_pending_state(self, user_id: int) -> bool:
        return user_id in self._states

    def cleanup_old_states(self, days_old: int = 7) -> int:
        return 0

    def get_all_active_users(self) -> list[int]:
        with self._lock:
            return list(self._states.keys())
