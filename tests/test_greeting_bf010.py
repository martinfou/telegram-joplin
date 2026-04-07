"""
Tests for BF-010: Greeting parse entities fix.

Verifies that the greeting uses HTML (not Markdown) to avoid underscore parse errors,
and that the plain-text fallback strips HTML correctly.
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

# Import the module to test (conftest adds project root to path)
from src.handlers import core as core_module


class TestGreetingContent(unittest.TestCase):
    """Test greeting content and helpers."""

    def test_greeting_uses_html_not_markdown(self):
        """Greeting should use <b> tags, not **, to avoid Markdown underscore issues."""
        orch = MagicMock()
        orch.logging_service.get_report_configuration.return_value = {"timezone": "UTC"}
        greeting = core_module._build_greeting_response(999, orch)
        # Should use HTML <b> for bold, not Markdown **
        self.assertIn("<b>📝 Capture</b>", greeting)
        self.assertIn("<b>🔍 Search</b>", greeting)
        self.assertIn("<b>📊 Review</b>", greeting)
        self.assertIn("<b>💪 Health</b>", greeting)
        self.assertIn("/health_today", greeting)
        self.assertIn("/health_import_quick", greeting)
        # Underscores in commands should be present (no Markdown italic)
        self.assertIn("/report_daily", greeting)
        self.assertIn("/report_weekly", greeting)
        self.assertIn("/report_monthly", greeting)
        # Angle brackets should be escaped for HTML
        self.assertIn("&lt;text&gt;", greeting)
        self.assertIn("&lt;query&gt;", greeting)

    def test_greeting_to_plain_strips_html(self):
        """_greeting_to_plain should strip <b> tags and unescape entities."""
        html = "<b>📝 Capture</b>\n• /task &lt;text&gt; → Create"
        plain = core_module._greeting_to_plain(html)
        self.assertNotIn("<b>", plain)
        self.assertNotIn("</b>", plain)
        self.assertIn("📝 Capture", plain)
        self.assertIn("<text>", plain)
        self.assertNotIn("&lt;", plain)
        self.assertNotIn("&gt;", plain)

    def test_is_profile_query(self):
        """_is_profile_query should match who am i and similar."""
        self.assertTrue(core_module._is_profile_query("who am i"))
        self.assertTrue(core_module._is_profile_query("Who am I?"))
        self.assertTrue(core_module._is_profile_query("what is my profile"))
        self.assertTrue(core_module._is_profile_query("tell me about myself"))
        self.assertFalse(core_module._is_profile_query("create a note about me"))
        self.assertFalse(core_module._is_profile_query("hello"))
