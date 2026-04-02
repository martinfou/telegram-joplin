"""
Test suite for Stoic Journal timezone fixes (BF-005).

Covers:
- Timezone-aware datetime usage in stoic reflection
- Data loss prevention when note fetching fails
- Duplicate session detection
- /stoic_replace and /stoic_append commands
"""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.exceptions import JoplinError
from src.handlers import stoic as stoic_module


class TestStoicTimezoneUsage(unittest.TestCase):
    """Test that stoic module uses timezone-aware datetime."""

    def test_format_morning_content_uses_timezone_aware_time(self):
        """_format_morning_content should use user's timezone for timestamp."""
        mock_orch = MagicMock()
        mock_orch.logging_service.get_report_configuration.return_value = {
            "timezone": "US/Eastern"
        }

        answers = [
            {"q": "Intention", "a": "Be present"},
            {"q": "Focus", "a": "Work"},
            {"q": "Virtue", "a": "Patience"},
            {"q": "Gratitude", "a": "Health"},
            {"q": "Tasks", "a": "Task 1"},
        ]

        content = stoic_module._format_morning_content(answers, 123, mock_orch)

        # Should contain 🌞 Morning with a timestamp
        self.assertIn("### 🌞 Morning", content)
        # Should have a time in HH:MM format
        self.assertRegex(content, r"\(\d{2}:\d{2}\)")

    def test_format_evening_content_uses_timezone_aware_time(self):
        """_format_evening_content should use user's timezone for timestamp."""
        mock_orch = MagicMock()
        mock_orch.logging_service.get_report_configuration.return_value = {
            "timezone": "US/Pacific"
        }

        answers = [
            {"q": "Wins", "a": "Completed task"},
            {"q": "Challenges", "a": "Hard problem"},
            {"q": "Lesson", "a": "Learned something"},
            {"q": "Gratitude", "a": "Support"},
        ]

        content = stoic_module._format_evening_content(answers, 123, mock_orch)

        # Should contain 🌙 Evening with a timestamp
        self.assertIn("### 🌙 Evening", content)
        # Should have a time in HH:MM format
        self.assertRegex(content, r"\(\d{2}:\d{2}\)")


class TestStoicDataLossPrevention(unittest.TestCase):
    """Test that stoic module prevents data loss when API fails."""

    @pytest.mark.asyncio
    @patch('src.handlers.stoic._format_section')
    @patch.object(stoic_module, '_load_stoic_template')
    async def test_aborts_on_note_fetch_failure(self, mock_load, mock_format):
        """Should abort and not overwrite note if get_note() fails."""
        mock_load.return_value = ("q1", "q2", "template")
        mock_format.return_value = "formatted content"

        mock_orch = MagicMock()
        mock_orch.logging_service.get_report_configuration.return_value = {
            "timezone": "US/Eastern"
        }
        mock_orch.joplin_client.get_or_create_folder_by_path = AsyncMock(
            return_value="folder_id"
        )
        mock_orch.joplin_client.get_notes_in_folder = AsyncMock(
            return_value=[{"id": "note_id", "title": "2025-03-03 - Daily Stoic Reflection"}]
        )
        # Simulate API failure when trying to fetch note
        mock_orch.joplin_client.get_note = AsyncMock(
            side_effect=Exception("API Error")
        )

        mock_message = MagicMock()
        mock_message.reply_text = AsyncMock()

        state = {
            "mode": "morning",
            "answers": [{"q": "Q1", "a": "Answer 1"}],
            "body_template": "template",
        }

        # Should return False (not saved)
        result = await stoic_module._finish_stoic_session(
            mock_orch, 123, mock_message, state
        )

        self.assertFalse(result)

        # Should send error message to user
        mock_message.reply_text.assert_called()
        error_call = [
            call for call in mock_message.reply_text.call_args_list
            if "Could not fetch" in str(call)
        ]
        self.assertTrue(error_call, "Should send error message about fetch failure")

        # Should NOT call update_note (preventing data loss)
        mock_orch.joplin_client.update_note.assert_not_called()


class TestStoicDuplicateDetection(unittest.TestCase):
    """Test duplicate session detection and handling."""

    def test_check_section_exists_finds_morning_section(self):
        """_check_section_exists should detect morning section."""
        note_body = """# 2025-03-03 - Daily Stoic Reflection

## Morning Reflection

### 🌞 Morning (10:30)

- **Intention:** Be present
"""
        self.assertTrue(stoic_module._check_section_exists(note_body, "morning"))

    def test_check_section_exists_finds_evening_section(self):
        """_check_section_exists should detect evening section."""
        note_body = """# 2025-03-03 - Daily Stoic Reflection

## Evening Reflection

### 🌙 Evening (21:00)

- **Wins:** Good day
"""
        self.assertTrue(stoic_module._check_section_exists(note_body, "evening"))

    def test_check_section_exists_returns_false_for_missing_section(self):
        """_check_section_exists should return False when section not found."""
        note_body = """# 2025-03-03 - Daily Stoic Reflection

## Morning Reflection

- Some content
"""
        self.assertFalse(stoic_module._check_section_exists(note_body, "morning"))

    @pytest.mark.asyncio
    @patch.object(stoic_module, "get_current_date_str", return_value="2025-03-03")
    @patch("src.handlers.stoic._format_section")
    @patch.object(stoic_module, "_load_stoic_template")
    async def test_detects_duplicate_morning_section(self, mock_load, mock_format, _mock_date):
        """Should detect duplicate morning section and prompt user."""
        mock_load.return_value = ("q1", "q2", "template")
        mock_format.return_value = "new morning content"

        existing_body = """# 2025-03-03 - Daily Stoic Reflection

### 🌞 Morning (07:00)

- **Intention:** Original intention

## Evening Reflection

(empty)
"""

        mock_orch = MagicMock()
        mock_orch.logging_service.get_report_configuration.return_value = {
            "timezone": "US/Eastern"
        }
        mock_orch.joplin_client.get_or_create_folder_by_path = AsyncMock(
            return_value="folder_id"
        )
        mock_orch.joplin_client.get_notes_in_folder = AsyncMock(
            return_value=[{"id": "note_id", "title": "2025-03-03 - Daily Stoic Reflection"}]
        )
        mock_orch.joplin_client.get_note = AsyncMock(
            return_value={"body": existing_body}
        )
        mock_orch.state_manager.update_state = MagicMock()

        mock_message = MagicMock()
        mock_message.reply_text = AsyncMock()

        state = {
            "mode": "morning",
            "answers": [{"q": "Q1", "a": "New answer"}],
            "body_template": "template",
        }

        result = await stoic_module._finish_stoic_session(
            mock_orch, 123, mock_message, state
        )

        # Should return False (not saved directly)
        self.assertFalse(result)

        # Should offer options to user
        calls = [str(call) for call in mock_message.reply_text.call_args_list]
        self.assertTrue(
            any("/stoic_replace" in str(call) for call in calls),
            "Should suggest /stoic_replace command"
        )
        self.assertTrue(
            any("/stoic_append" in str(call) for call in calls),
            "Should suggest /stoic_append command"
        )

        # Should update state with pending action
        mock_orch.state_manager.update_state.assert_called()
        updated_state = mock_orch.state_manager.update_state.call_args[0][1]
        self.assertEqual(updated_state.get("pending_action"), "duplicate_detected")
        self.assertEqual(
            updated_state.get("duplicate_note_title"),
            "2025-03-03 - Daily Stoic Reflection",
        )


class TestStoicDuplicateNoteResolve(unittest.IsolatedAsyncioTestCase):
    """DEF-038: re-resolve note by title when stored id returns 404."""

    async def test_fetch_resolves_note_when_id_is_stale(self):
        mock_orch = MagicMock()
        stale_id = "deadbeefdeadbeefdeadbeefdeadbeef"
        good_id = "cafebabecafebabecafebabecafebabe"
        title = "2026-03-31 - Daily Stoic Reflection"

        async def get_note_side_effect(nid: str):
            if nid == stale_id:
                raise JoplinError("not found", status_code=404)
            if nid == good_id:
                return {"id": good_id, "title": title, "body": "### 🌞 Morning\n\nold"}
            raise AssertionError(f"unexpected get_note {nid!r}")

        mock_orch.joplin_client.get_note = AsyncMock(side_effect=get_note_side_effect)
        mock_orch.joplin_client.get_or_create_folder_by_path = AsyncMock(return_value="folder1")
        mock_orch.joplin_client.get_notes_in_folder = AsyncMock(
            return_value=[{"id": good_id, "title": title}]
        )

        mock_message = MagicMock()
        mock_message.reply_text = AsyncMock()

        result = await stoic_module._fetch_stoic_note_for_duplicate_action(
            mock_orch, stale_id, title, mock_message
        )
        self.assertIsNotNone(result)
        full, resolved_id = result
        self.assertEqual(resolved_id, good_id)
        self.assertIn("Morning", full.get("body", ""))
        mock_message.reply_text.assert_not_called()


class TestStoicReplaceSection(unittest.TestCase):
    """Test _replace_section function."""

    def test_replaces_morning_section(self):
        """_replace_section should replace morning content while keeping evening."""
        body = """# 2025-03-03 - Daily Stoic Reflection

### 🌞 Morning (07:00)

- **Intention:** Old intention

### 🌙 Evening (21:00)

- **Wins:** Good day
"""
        new_section = "### 🌞 Morning (10:00)\n\n- **Intention:** New intention"

        result = stoic_module._replace_section(body, new_section, "morning")

        # Should contain new morning content
        self.assertIn("New intention", result)
        # Should NOT contain old morning content
        self.assertNotIn("Old intention", result)
        # Should still contain evening section
        self.assertIn("### 🌙 Evening", result)
        self.assertIn("Good day", result)

    def test_replaces_evening_section(self):
        """_replace_section should replace evening content while keeping morning."""
        body = """# 2025-03-03 - Daily Stoic Reflection

### 🌞 Morning (07:00)

- **Intention:** Good intention

### 🌙 Evening (21:00)

- **Wins:** Old wins
"""
        new_section = "### 🌙 Evening (22:00)\n\n- **Wins:** Better wins"

        result = stoic_module._replace_section(body, new_section, "evening")

        # Should contain new evening content
        self.assertIn("Better wins", result)
        # Should NOT contain old evening content
        self.assertNotIn("Old wins", result)
        # Should still contain morning section
        self.assertIn("### 🌞 Morning", result)
        self.assertIn("Good intention", result)


if __name__ == "__main__":
    unittest.main()
