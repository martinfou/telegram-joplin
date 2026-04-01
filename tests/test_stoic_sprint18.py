"""
Sprint 18 unit tests for Stoic Journal new features:
- T-001: Mood check-in stored in state
- T-003: Question variant rotation is date-seeded
- T-004: Quote bank loads; daily rotation is date-seeded
- T-006: Streak increments on consecutive days; resets on gap
- T-007: Quick mode saves with is_quick=True, no check-in step
- T-005: /stoic review guard (< 3 entries returns early)
- T-002: Self-compassion question present in evening template
"""

from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.handlers import stoic as stoic_module
from src.handlers.stoic import (
    _CHECKIN_DONE,
    _CHECKIN_STEP_ENERGY,
    _CHECKIN_STEP_MOOD,
    _daily_quote,
    _load_stoic_quotes,
    _load_stoic_template,
    _parse_variant_block,
    _streak_message,
    _update_streak,
)

# ---------------------------------------------------------------------------
# T-004: Quote bank
# ---------------------------------------------------------------------------

class TestStoicQuotes(unittest.TestCase):
    """T-004: Quote bank loads correctly and rotation is date-seeded."""

    def test_load_stoic_quotes_returns_dict_with_morning_and_evening(self):
        quotes = _load_stoic_quotes()
        self.assertIn("morning", quotes)
        self.assertIn("evening", quotes)
        self.assertIsInstance(quotes["morning"], list)
        self.assertIsInstance(quotes["evening"], list)

    def test_load_stoic_quotes_both_non_empty(self):
        quotes = _load_stoic_quotes()
        self.assertGreater(len(quotes["morning"]), 0, "Should load at least 1 morning quote")
        self.assertGreater(len(quotes["evening"]), 0, "Should load at least 1 evening quote")

    def test_daily_quote_morning_returns_string(self):
        quote = _daily_quote("morning")
        self.assertIsInstance(quote, str)
        self.assertGreater(len(quote), 0)

    def test_daily_quote_evening_returns_string(self):
        quote = _daily_quote("evening")
        self.assertIsInstance(quote, str)
        self.assertGreater(len(quote), 0)

    def test_daily_quote_same_day_returns_same_quote(self):
        """Two calls on same day must return the same quote (date-seeded)."""
        q1 = _daily_quote("morning")
        q2 = _daily_quote("morning")
        self.assertEqual(q1, q2)

    def test_daily_quote_different_days_may_differ(self):
        """Rotation should select different quotes on different days."""
        quotes = _load_stoic_quotes()
        pool = quotes["morning"]
        if len(pool) < 2:
            self.skipTest("Need at least 2 quotes to test rotation")
        ordinal_today = datetime.now(UTC).toordinal()
        q_today = pool[ordinal_today % len(pool)]
        q_tomorrow = pool[(ordinal_today + 1) % len(pool)]
        # At minimum the logic is deterministic — today = today_idx
        self.assertEqual(_daily_quote("morning"), q_today)
        # tomorrow would be a different index (may or may not equal today)
        self.assertNotEqual(q_today, q_tomorrow)  # with 25+ quotes this should hold

    def test_daily_quote_unknown_mode_falls_back_to_morning(self):
        quote = _daily_quote("unknown_mode")
        self.assertIsInstance(quote, str)
        self.assertGreater(len(quote), 0)


# ---------------------------------------------------------------------------
# T-003: Variant rotation
# ---------------------------------------------------------------------------

class TestParseVariantBlock(unittest.TestCase):
    """T-003: VARIANT_ rotation is date-seeded and selects one per slot."""

    def test_single_variant_always_selected(self):
        lines = ["VARIANT_0: Only option"]
        result = _parse_variant_block(lines)
        self.assertEqual(result, ["Only option"])

    def test_three_variants_selects_exactly_one(self):
        lines = [
            "VARIANT_0: Option A",
            "VARIANT_1: Option B",
            "VARIANT_2: Option C",
        ]
        result = _parse_variant_block(lines)
        self.assertEqual(len(result), 1)
        self.assertIn(result[0], ["Option A", "Option B", "Option C"])

    def test_same_day_same_variant_selected(self):
        """Two calls on same day must pick the same variant (date-seeded)."""
        lines = [
            "VARIANT_0: Option A",
            "VARIANT_1: Option B",
            "VARIANT_2: Option C",
        ]
        r1 = _parse_variant_block(lines)
        r2 = _parse_variant_block(lines)
        self.assertEqual(r1, r2)

    def test_non_variant_lines_pass_through(self):
        lines = ["Plain question without variant?"]
        result = _parse_variant_block(lines)
        self.assertEqual(result, ["Plain question without variant?"])

    def test_multiple_slots_parsed_correctly(self):
        # VARIANT_0 at start of second group signals a new slot boundary.
        lines = [
            "VARIANT_0: Slot1-A",
            "VARIANT_1: Slot1-B",
            "VARIANT_0: Slot2-A",
            "VARIANT_1: Slot2-B",
        ]
        result = _parse_variant_block(lines)
        self.assertEqual(len(result), 2)
        self.assertIn(result[0], ["Slot1-A", "Slot1-B"])
        self.assertIn(result[1], ["Slot2-A", "Slot2-B"])

    def test_empty_lines_skipped(self):
        # Blank lines don't start new slots; VARIANT_0/VARIANT_1 with blank line
        # between them → two separate single-variant slots (each yields its only option).
        lines = ["", "VARIANT_0: Question A", "", "VARIANT_1: Question B"]
        result = _parse_variant_block(lines)
        # Blank line breaks the run → two slots (each with 1 variant)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Question A")
        self.assertEqual(result[1], "Question B")

    def test_variant_selection_matches_date_ordinal(self):
        """Selected variant index should match toordinal() % 3."""
        lines = [
            "VARIANT_0: Option A",
            "VARIANT_1: Option B",
            "VARIANT_2: Option C",
        ]
        expected_idx = datetime.now(UTC).toordinal() % 3
        expected = ["Option A", "Option B", "Option C"][expected_idx]
        result = _parse_variant_block(lines)
        self.assertEqual(result[0], expected)


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

class TestLoadStoicTemplate(unittest.TestCase):
    """Template loads morning/evening questions and body template."""

    def test_returns_three_tuple(self):
        result = _load_stoic_template()
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)

    def test_morning_questions_non_empty(self):
        morning_q, _, _ = _load_stoic_template()
        self.assertGreater(len(morning_q), 0)

    def test_evening_questions_non_empty(self):
        _, evening_q, _ = _load_stoic_template()
        self.assertGreater(len(evening_q), 0)

    def test_morning_questions_count_is_seven(self):
        """Morning template has 7 question slots."""
        morning_q, _, _ = _load_stoic_template()
        self.assertEqual(len(morning_q), 7)

    def test_evening_questions_count_is_ten(self):
        """Evening template has 10 question slots (Sprint 18: +self-compassion +learning)."""
        _, evening_q, _ = _load_stoic_template()
        self.assertEqual(len(evening_q), 10)

    def test_self_compassion_in_evening_questions(self):
        """T-002: Self-compassion question should be at index 4."""
        _, evening_q, _ = _load_stoic_template()
        self.assertGreaterEqual(len(evening_q), 5)
        # Index 4 should be the self-compassion question
        compassion_keywords = ["friend", "compassion", "comfort", "love", "kind"]
        found = any(
            kw in evening_q[4].lower() for kw in compassion_keywords
        )
        self.assertTrue(found, f"Index 4 should be self-compassion question, got: {evening_q[4]}")

    def test_learning_question_in_evening(self):
        """US-042: 'What I Learned Today' should appear as evening question at index 8."""
        _, evening_q, _ = _load_stoic_template()
        self.assertGreaterEqual(len(evening_q), 9)
        learning_keywords = ["learn", "insight", "lesson", "taught", "skill"]
        found = any(
            kw in evening_q[8].lower() for kw in learning_keywords
        )
        self.assertTrue(found, f"Index 8 should be learning question, got: {evening_q[8]}")

    def test_body_template_contains_placeholders(self):
        _, _, body = _load_stoic_template()
        self.assertIn("{{DATE}}", body)
        self.assertIn("{{MORNING_CONTENT}}", body)
        self.assertIn("{{EVENING_CONTENT}}", body)

    def test_parse_variant_block_slot_boundary_all_slots_present(self):
        """T-013: All 3 variants must be present for each slot across both templates.

        CI guard against _parse_variant_block regressions where multiple variants
        get collapsed into a single slot (the Sprint 18 bug). Mirrors the exact
        parsing logic used by _load_stoic_template() in stoic.py.
        """
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "src" / "prompts" / "stoic_journal_template.md"
        self.assertTrue(template_path.exists(), "stoic_journal_template.md must exist")

        raw = template_path.read_text(encoding="utf-8")
        parts = raw.split("---", 1)
        self.assertEqual(len(parts), 2, "Template must contain '---' separator before body template")

        block = parts[0].strip()
        morning_raw: list[str] = []
        evening_raw: list[str] = []
        current: list[str] | None = None
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.upper() == "MORNING_QUESTIONS:":
                current = morning_raw
                continue
            if stripped.upper() == "EVENING_QUESTIONS:":
                current = evening_raw
                continue
            if current is not None:
                current.append(line)

        morning_questions = _parse_variant_block(morning_raw)
        evening_questions = _parse_variant_block(evening_raw)

        self.assertEqual(
            len(morning_questions), 7,
            f"Morning should have 7 slots after variant resolution, got {len(morning_questions)}"
        )
        self.assertEqual(
            len(evening_questions), 10,
            f"Evening should have 10 slots after variant resolution, got {len(evening_questions)}"
        )

        # All resolved questions must be non-empty strings
        for i, q in enumerate(morning_questions):
            self.assertIsInstance(q, str, f"Morning slot {i} must be a string")
            self.assertGreater(len(q.strip()), 0, f"Morning slot {i} must not be empty")
        for i, q in enumerate(evening_questions):
            self.assertIsInstance(q, str, f"Evening slot {i} must be a string")
            self.assertGreater(len(q.strip()), 0, f"Evening slot {i} must not be empty")

    def test_parse_variant_block_slot_boundary_three_variants_per_slot(self):
        """T-013: Each variant slot must have exactly 3 variants (VARIANT_0, VARIANT_1, VARIANT_2).

        CI guard: if the template is edited and a variant is removed or a slot
        boundary is broken, this test fails. Ensures all 7 morning + 10 evening
        slots have exactly 3 variant lines each.
        """
        from pathlib import Path
        template_path = Path(__file__).parent.parent / "src" / "prompts" / "stoic_journal_template.md"
        self.assertTrue(template_path.exists(), "stoic_journal_template.md must exist")
        raw = template_path.read_text(encoding="utf-8")
        parts = raw.split("---", 1)
        self.assertEqual(len(parts), 2, "Template must contain '---' separator")
        block = parts[0].strip()
        morning_raw = []
        evening_raw = []
        current = None
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.upper() == "MORNING_QUESTIONS:":
                current = morning_raw
                continue
            if stripped.upper() == "EVENING_QUESTIONS:":
                current = evening_raw
                continue
            if current is not None:
                current.append(line)

        def slots_from_raw(lines: list[str]) -> list[list[str]]:
            """Split raw lines into slots (same boundary logic as _parse_variant_block)."""
            slots: list[list[str]] = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if not line:
                    i += 1
                    continue
                if line.startswith("VARIANT_"):
                    variants = []
                    while i < len(lines):
                        text = lines[i].strip()
                        if not text.startswith("VARIANT_"):
                            break
                        if text.startswith("VARIANT_0:") and variants:
                            break
                        variants.append(text)
                        i += 1
                    if variants:
                        slots.append(variants)
                else:
                    slots.append([line])
                    i += 1
            return slots

        morning_slots = slots_from_raw(morning_raw)
        evening_slots = slots_from_raw(evening_raw)
        self.assertEqual(len(morning_slots), 7, "Morning must have 7 slots")
        self.assertEqual(len(evening_slots), 10, "Evening must have 10 slots")

        for idx, slot in enumerate(morning_slots):
            variant_lines = [s for s in slot if s.startswith("VARIANT_")]
            self.assertEqual(
                len(variant_lines), 3,
                f"Morning slot {idx} must have exactly 3 variants (VARIANT_0/1/2), got {len(variant_lines)}"
            )
            for v in ("VARIANT_0:", "VARIANT_1:", "VARIANT_2:"):
                self.assertTrue(
                    any(s.startswith(v) for s in variant_lines),
                    f"Morning slot {idx} missing {v.strip(':')}"
                )
        for idx, slot in enumerate(evening_slots):
            variant_lines = [s for s in slot if s.startswith("VARIANT_")]
            self.assertEqual(
                len(variant_lines), 3,
                f"Evening slot {idx} must have exactly 3 variants (VARIANT_0/1/2), got {len(variant_lines)}"
            )
            for v in ("VARIANT_0:", "VARIANT_1:", "VARIANT_2:"):
                self.assertTrue(
                    any(s.startswith(v) for s in variant_lines),
                    f"Evening slot {idx} missing {v.strip(':')}"
                )


# ---------------------------------------------------------------------------
# T-006: Streak tracking
# ---------------------------------------------------------------------------

class TestStreakUpdate(unittest.TestCase):
    """T-006: Streak increments on consecutive days, resets on gap > 1."""

    def _make_orch(self, last_date: str | None, streak: str | None) -> MagicMock:
        mock_orch = MagicMock()
        prefs: dict[str, str] = {}
        if last_date is not None:
            prefs[stoic_module._PREF_LAST_ENTRY] = last_date
        if streak is not None:
            prefs[stoic_module._PREF_STREAK] = streak

        def get_pref(uid, key):
            return prefs.get(key)

        def set_pref(uid, key, val):
            prefs[key] = val

        mock_orch.state_manager.get_user_pref.side_effect = get_pref
        mock_orch.state_manager.set_user_pref.side_effect = set_pref
        # DEF-037: _update_streak uses get_user_timezone_aware_now() which resolves to
        # default timezone (America/Montreal) since stored "UTC" is treated as legacy.
        mock_orch.logging_service.get_report_configuration.return_value = None
        return mock_orch

    def _today(self) -> str:
        """Return today's date in the configured default timezone (America/Montreal)."""
        from src.timezone_utils import get_now_in_default_tz
        return get_now_in_default_tz().date().isoformat()

    def test_first_entry_gives_streak_of_one(self):
        orch = self._make_orch(None, None)
        result = _update_streak(orch, 1)
        self.assertEqual(result, 1)

    def test_same_day_does_not_increment(self):
        today = self._today()
        orch = self._make_orch(today, "3")
        result = _update_streak(orch, 1)
        self.assertEqual(result, 3)

    def test_consecutive_day_increments(self):
        from src.timezone_utils import get_now_in_default_tz
        yesterday = (get_now_in_default_tz().date() - timedelta(days=1)).isoformat()
        orch = self._make_orch(yesterday, "4")
        result = _update_streak(orch, 1)
        self.assertEqual(result, 5)

    def test_two_day_gap_resets_to_one(self):
        from src.timezone_utils import get_now_in_default_tz
        two_days_ago = (get_now_in_default_tz().date() - timedelta(days=2)).isoformat()
        orch = self._make_orch(two_days_ago, "10")
        result = _update_streak(orch, 1)
        self.assertEqual(result, 1)

    def test_large_gap_resets_to_one(self):
        from src.timezone_utils import get_now_in_default_tz
        month_ago = (get_now_in_default_tz().date() - timedelta(days=30)).isoformat()
        orch = self._make_orch(month_ago, "25")
        result = _update_streak(orch, 1)
        self.assertEqual(result, 1)

    def test_streak_saved_after_increment(self):
        from src.timezone_utils import get_now_in_default_tz
        yesterday = (get_now_in_default_tz().date() - timedelta(days=1)).isoformat()
        mock_orch = MagicMock()
        saved: dict[str, str] = {}

        def get_pref(uid, key):
            if key == stoic_module._PREF_LAST_ENTRY:
                return yesterday
            if key == stoic_module._PREF_STREAK:
                return "2"
            return None

        def set_pref(uid, key, val):
            saved[key] = val

        mock_orch.state_manager.get_user_pref.side_effect = get_pref
        mock_orch.state_manager.set_user_pref.side_effect = set_pref
        mock_orch.logging_service.get_report_configuration.return_value = None

        _update_streak(mock_orch, 1)

        self.assertIn(stoic_module._PREF_STREAK, saved)
        self.assertEqual(saved[stoic_module._PREF_STREAK], "3")
        today = get_now_in_default_tz().date().isoformat()
        self.assertEqual(saved[stoic_module._PREF_LAST_ENTRY], today)


class TestStreakMessage(unittest.TestCase):
    """_streak_message produces correct motivational text."""

    def test_day_one(self):
        msg = _streak_message(1, "morning")
        self.assertIn("Day 1", msg)

    def test_early_streak(self):
        msg = _streak_message(5, "morning")
        self.assertIn("🔥", msg)
        self.assertIn("5", msg)

    def test_week_streak(self):
        msg = _streak_message(14, "evening")
        self.assertIn("🔥", msg)
        self.assertIn("14", msg)

    def test_long_streak(self):
        msg = _streak_message(45, "morning")
        self.assertIn("🔥", msg)
        self.assertIn("45", msg)

    def test_quick_mode_prefix(self):
        msg = _streak_message(3, "morning", is_quick=True)
        self.assertIn("Quick entry", msg)

    def test_full_mode_prefix(self):
        msg = _streak_message(3, "morning", is_quick=False)
        self.assertIn("Stoic reflection", msg)


# ---------------------------------------------------------------------------
# T-001: Mood check-in state handling
# ---------------------------------------------------------------------------

class TestMoodCheckin(unittest.IsolatedAsyncioTestCase):
    """T-001: Mood check-in stored in state, energy stored, transitions to Q&A."""

    def _make_state(self, checkin_step: int, mode: str = "morning") -> dict:
        return {
            "active_persona": "STOIC_JOURNAL",
            "mode": mode,
            "questions": [],
            "answers": [],
            "body_template": "",
            "is_quick": False,
            "checkin_step": checkin_step,
            "mood_checkin": "",
            "energy_level": "",
        }

    async def test_mood_step_stores_mood_and_advances(self):
        state = self._make_state(_CHECKIN_STEP_MOOD)
        mock_orch = MagicMock()
        mock_orch.state_manager.get_state.return_value = state
        updated_states: list[dict] = []
        mock_orch.state_manager.update_state.side_effect = lambda uid, s: updated_states.append(dict(s))

        mock_message = MagicMock()
        mock_message.reply_text = AsyncMock()

        await stoic_module.handle_stoic_message(mock_orch, 1, "energized", mock_message)

        self.assertTrue(len(updated_states) > 0)
        last_state = updated_states[-1]
        self.assertEqual(last_state["mood_checkin"], "energized")
        self.assertEqual(last_state["checkin_step"], _CHECKIN_STEP_ENERGY)

        # Should ask energy question
        mock_message.reply_text.assert_called_once()
        call_text = mock_message.reply_text.call_args[0][0]
        self.assertIn("Energy", call_text)

    async def test_energy_step_stores_energy_and_transitions(self):
        state = self._make_state(_CHECKIN_STEP_ENERGY)
        mock_orch = MagicMock()
        mock_orch.state_manager.get_state.return_value = state
        updated_states: list[dict] = []
        mock_orch.state_manager.update_state.side_effect = lambda uid, s: updated_states.append(dict(s))
        mock_orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}
        mock_orch.joplin_client.get_or_create_folder_by_path = AsyncMock(return_value="folder_id")
        mock_orch.joplin_client.get_notes_in_folder = AsyncMock(return_value=[])

        mock_message = MagicMock()
        mock_message.reply_text = AsyncMock()

        await stoic_module.handle_stoic_message(mock_orch, 1, "4", mock_message)

        energy_saved = any(s.get("energy_level") == "4" for s in updated_states)
        self.assertTrue(energy_saved, "Energy level should be saved in state")

        checkin_done = any(s.get("checkin_step") == _CHECKIN_DONE for s in updated_states)
        self.assertTrue(checkin_done, "checkin_step should advance to DONE")

    async def test_quick_mode_skips_checkin(self):
        """T-007: Quick mode starts with checkin_step=DONE, so no check-in question asked."""
        state = self._make_state(_CHECKIN_DONE, mode="morning")
        state["is_quick"] = True
        state["questions"] = ["What is your intention for today?", "What is your #1 priority?"]
        state["answers"] = []

        mock_orch = MagicMock()
        mock_orch.state_manager.get_state.return_value = state
        mock_orch.state_manager.update_state = MagicMock()

        mock_message = MagicMock()
        mock_message.reply_text = AsyncMock()

        # Answering first question should go to second Q, not check-in
        await stoic_module.handle_stoic_message(mock_orch, 1, "Focus on deep work", mock_message)

        mock_message.reply_text.assert_called_once()
        reply_text = mock_message.reply_text.call_args[0][0]
        # Should show second question, not an energy/mood question
        self.assertNotIn("Energy", reply_text)
        self.assertNotIn("feeling", reply_text.lower())


# ---------------------------------------------------------------------------
# T-007: Quick mode — is_quick stored in state
# ---------------------------------------------------------------------------

class TestQuickModeState(unittest.IsolatedAsyncioTestCase):
    """T-007: /stoic_quick stores is_quick=True and uses 2-question sets."""

    async def test_quick_mode_sets_is_quick_true(self):
        mock_orch = MagicMock()
        mock_orch.state_manager.get_state.return_value = None  # no active session
        mock_orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}

        stored_state: dict = {}
        mock_orch.state_manager.update_state.side_effect = lambda uid, s: stored_state.update(s)

        mock_update = MagicMock()
        mock_update.effective_user.id = 1
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = ["morning"]

        with patch("src.handlers.stoic.check_whitelist", return_value=True), \
             patch("src.handlers.stoic.get_user_timezone_aware_now") as mock_now:
            mock_now.return_value = datetime(2026, 3, 8, 9, 0, tzinfo=UTC)
            handler = stoic_module._stoic_quick(mock_orch)
            await handler(mock_update, mock_context)

        self.assertTrue(stored_state.get("is_quick"), "is_quick should be True in state")
        self.assertEqual(stored_state.get("checkin_step"), _CHECKIN_DONE)

    async def test_quick_morning_uses_two_questions(self):
        mock_orch = MagicMock()
        mock_orch.state_manager.get_state.return_value = None
        mock_orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}

        stored_state: dict = {}
        mock_orch.state_manager.update_state.side_effect = lambda uid, s: stored_state.update(s)

        mock_update = MagicMock()
        mock_update.effective_user.id = 1
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = ["morning"]

        with patch("src.handlers.stoic.check_whitelist", return_value=True), \
             patch("src.handlers.stoic.get_user_timezone_aware_now") as mock_now:
            mock_now.return_value = datetime(2026, 3, 8, 9, 0, tzinfo=UTC)
            handler = stoic_module._stoic_quick(mock_orch)
            await handler(mock_update, mock_context)

        self.assertEqual(stored_state.get("mode"), "morning")
        # Quick morning should have exactly 2 questions
        self.assertEqual(len(stored_state.get("questions", [])), 2)

    async def test_quick_auto_detects_evening_after_17(self):
        mock_orch = MagicMock()
        mock_orch.state_manager.get_state.return_value = None
        mock_orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}

        stored_state: dict = {}
        mock_orch.state_manager.update_state.side_effect = lambda uid, s: stored_state.update(s)

        mock_update = MagicMock()
        mock_update.effective_user.id = 1
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = []  # No explicit mode

        with patch("src.handlers.stoic.check_whitelist", return_value=True), \
             patch("src.handlers.stoic.get_user_timezone_aware_now") as mock_now:
            mock_now.return_value = datetime(2026, 3, 8, 19, 30, tzinfo=UTC)  # 19:30 → evening
            handler = stoic_module._stoic_quick(mock_orch)
            await handler(mock_update, mock_context)

        self.assertEqual(stored_state.get("mode"), "evening")

    async def test_quick_auto_detects_morning_before_17(self):
        mock_orch = MagicMock()
        mock_orch.state_manager.get_state.return_value = None
        mock_orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}

        stored_state: dict = {}
        mock_orch.state_manager.update_state.side_effect = lambda uid, s: stored_state.update(s)

        mock_update = MagicMock()
        mock_update.effective_user.id = 1
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()
        mock_context.args = []

        with patch("src.handlers.stoic.check_whitelist", return_value=True), \
             patch("src.handlers.stoic.get_user_timezone_aware_now") as mock_now:
            mock_now.return_value = datetime(2026, 3, 8, 8, 0, tzinfo=UTC)  # 08:00 → morning
            handler = stoic_module._stoic_quick(mock_orch)
            await handler(mock_update, mock_context)

        self.assertEqual(stored_state.get("mode"), "morning")


# ---------------------------------------------------------------------------
# T-005: /stoic review guard (< 3 entries)
# ---------------------------------------------------------------------------

class TestStoicReviewGuard(unittest.IsolatedAsyncioTestCase):
    """T-005: /stoic review returns early when fewer than 3 entries found."""

    async def test_review_returns_early_with_zero_entries(self):
        mock_orch = MagicMock()
        mock_orch.joplin_client.get_or_create_folder_by_path = AsyncMock(return_value="folder_id")
        mock_orch.joplin_client.get_notes_in_folder = AsyncMock(return_value=[])

        mock_update = MagicMock()
        mock_update.effective_user.id = 1
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()

        with patch("src.handlers.stoic.check_whitelist", return_value=True):
            handler = stoic_module._stoic_review(mock_orch)
            await handler(mock_update, mock_context)

        calls = [str(c) for c in mock_update.message.reply_text.call_args_list]
        guard_triggered = any(
            "journal entr" in c or "Keep journaling" in c for c in calls
        )
        self.assertTrue(guard_triggered, "Should show guard message when 0 entries")

        # Should NOT call LLM
        mock_orch.llm_orchestrator.generate_stoic_weekly_review.assert_not_called()

    async def test_review_returns_early_with_two_entries(self):
        mock_orch = MagicMock()
        # Return 2 notes (below threshold)
        notes = [
            {"id": f"note_{i}", "title": f"2026-03-0{i+1} - Daily Stoic Reflection"}
            for i in range(2)
        ]
        mock_orch.joplin_client.get_or_create_folder_by_path = AsyncMock(return_value="folder_id")
        mock_orch.joplin_client.get_notes_in_folder = AsyncMock(return_value=notes)

        # get_note returns note with recent date
        today = datetime.now(UTC).date()
        async def get_note(note_id):
            idx = int(note_id.split("_")[1])
            note_date = (today - timedelta(days=idx)).isoformat()
            return {
                "id": note_id,
                "title": f"{note_date} - Daily Stoic Reflection",
                "body": "Sample body",
            }
        mock_orch.joplin_client.get_note = get_note

        mock_update = MagicMock()
        mock_update.effective_user.id = 1
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()

        with patch("src.handlers.stoic.check_whitelist", return_value=True):
            handler = stoic_module._stoic_review(mock_orch)
            await handler(mock_update, mock_context)

        calls = [str(c) for c in mock_update.message.reply_text.call_args_list]
        guard_triggered = any(
            "entr" in c.lower() or "Keep journaling" in c for c in calls
        )
        self.assertTrue(guard_triggered, "Should show guard message for < 3 entries")

        mock_orch.llm_orchestrator.generate_stoic_weekly_review.assert_not_called()

    async def test_review_calls_llm_with_three_or_more_entries(self):
        mock_orch = MagicMock()
        today = datetime.now(UTC).date()
        notes = [
            {"id": f"note_{i}", "title": f"{(today - timedelta(days=i)).isoformat()} - Daily Stoic Reflection"}
            for i in range(4)
        ]
        mock_orch.joplin_client.get_or_create_folder_by_path = AsyncMock(return_value="folder_id")
        mock_orch.joplin_client.get_notes_in_folder = AsyncMock(return_value=notes)

        async def get_note(note_id):
            idx = int(note_id.split("_")[1])
            note_date = (today - timedelta(days=idx)).isoformat()
            return {
                "id": note_id,
                "title": f"{note_date} - Daily Stoic Reflection",
                "body": "Entry content here.",
            }
        mock_orch.joplin_client.get_note = get_note
        mock_orch.llm_orchestrator.generate_stoic_weekly_review = AsyncMock(return_value="Synthesis text.")
        mock_orch.joplin_client.create_note = AsyncMock(return_value="review_note_id")
        mock_orch.joplin_client.apply_tags = AsyncMock()

        mock_update = MagicMock()
        mock_update.effective_user.id = 1
        mock_update.message = MagicMock()
        mock_update.message.reply_text = AsyncMock()

        mock_context = MagicMock()

        with patch("src.handlers.stoic.check_whitelist", return_value=True):
            handler = stoic_module._stoic_review(mock_orch)
            await handler(mock_update, mock_context)

        mock_orch.llm_orchestrator.generate_stoic_weekly_review.assert_called_once()


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

class TestFormatCheckinSection(unittest.TestCase):
    """_format_checkin_section produces correct Markdown."""

    def test_format_checkin_section_includes_mood_and_energy(self):
        result = stoic_module._format_checkin_section("calm", "3")
        self.assertIn("calm", result)
        self.assertIn("3", result)
        self.assertIn("Check-in", result)

    def test_format_checkin_section_empty_still_returns_string(self):
        result = stoic_module._format_checkin_section("", "")
        self.assertIsInstance(result, str)


class TestFormatMorningContent(unittest.TestCase):
    """_format_morning_content handles 7 answers."""

    def _make_orch(self):
        mock_orch = MagicMock()
        mock_orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}
        return mock_orch

    def _make_answers(self, n: int) -> list[dict]:
        return [{"q": f"Q{i}", "a": f"Answer {i}"} for i in range(n)]

    def test_morning_content_contains_section_header(self):
        result = stoic_module._format_morning_content(self._make_answers(7), 1, self._make_orch())
        self.assertIn("🌞 Morning", result)

    def test_morning_content_with_fewer_answers(self):
        result = stoic_module._format_morning_content(self._make_answers(3), 1, self._make_orch())
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


class TestFormatEveningContent(unittest.TestCase):
    """_format_evening_content handles 10 answers including self-compassion and learning."""

    def _make_orch(self):
        mock_orch = MagicMock()
        mock_orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}
        return mock_orch

    def _make_answers(self, n: int) -> list[dict]:
        return [{"q": f"Q{i}", "a": f"Answer {i}"} for i in range(n)]

    def test_evening_content_contains_section_header(self):
        result = stoic_module._format_evening_content(self._make_answers(10), 1, self._make_orch())
        self.assertIn("🌙 Evening", result)

    def test_evening_content_includes_self_compassion_section(self):
        answers = self._make_answers(10)
        answers[4] = {"q": "Self-compassion?", "a": "I was kind to myself"}
        result = stoic_module._format_evening_content(answers, 1, self._make_orch())
        self.assertIn("I was kind to myself", result)

    def test_evening_content_includes_learning_section(self):
        answers = self._make_answers(10)
        answers[8] = {"q": "What did you learn?", "a": "I learned about async patterns"}
        result = stoic_module._format_evening_content(answers, 1, self._make_orch())
        self.assertIn("I learned about async patterns", result)
        # Should have the 📚 section marker
        self.assertIn("📚", result)

    def test_evening_content_with_fewer_answers(self):
        result = stoic_module._format_evening_content(self._make_answers(4), 1, self._make_orch())
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)


if __name__ == "__main__":
    unittest.main()
