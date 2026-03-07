#!/usr/bin/env python3
"""
Test script to verify the Intelligent Joplin Librarian setup
Run this after setup to ensure everything is working correctly.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_imports() -> bool:
    """Test that all required modules can be imported."""
    modules_to_test = [
        "src.settings",
        "src.joplin_client",
        "src.state_manager",
        "src.llm_orchestrator",
        "src.security_utils",
        "src.telegram_orchestrator",
    ]

    print("Testing imports...")
    failed_imports = []

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ {len(failed_imports)} modules failed to import")
        return False
    print(f"\n✅ All {len(modules_to_test)} modules imported successfully")
    return True


def test_config() -> bool:
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from src.settings import get_settings

        settings = get_settings()

        checks = [
            ("TELEGRAM_BOT_TOKEN", settings.telegram.bot_token),
            ("ALLOWED_TELEGRAM_USER_IDS", settings.telegram.allowed_user_ids),
        ]

        for name, value in checks:
            if value:
                print(f"  ✅ {name} is configured")
            else:
                print(f"  ⚠️  {name} is not set (configure in .env file)")

        # At least one LLM provider
        has_llm = bool(
            settings.llm.openai_api_key
            or settings.llm.deepseek_api_key
            or (settings.llm.provider == "ollama")
        )
        if has_llm:
            print(f"  ✅ LLM provider ({settings.llm.provider}) configured")
        else:
            print(f"  ⚠️  No LLM API key set (DEEPSEEK_API_KEY, OPENAI_API_KEY, or OLLAMA)")

        print("  ✅ Configuration module loaded")
        return True

    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_joplin_connection() -> bool:
    """Test Joplin API connection."""
    print("\nTesting Joplin connection...")
    try:
        from src.joplin_client import JoplinClient

        client = JoplinClient()

        async def _ping():
            return await client.ping()

        result = asyncio.run(_ping())
        if result:
            print("  ✅ Joplin API is accessible")
            return True
        print("  ⚠️  Joplin API is not accessible (make sure Joplin is running)")
        return False

    except Exception as e:
        print(f"  ⚠️  Joplin connection test failed: {e}")
        print("     (This is expected if Joplin is not running)")
        return False


def test_llm_providers() -> bool:
    """Test LLM provider availability."""
    print("\nTesting LLM providers...")
    try:
        from src.llm_providers import registry

        available = registry.get_available_providers()
        if available:
            print(f"  ✅ {len(available)} LLM provider(s) available: {', '.join(available.keys())}")
            return True
        print("  ⚠️  No LLM providers configured")
        print("     Configure DEEPSEEK_API_KEY, OPENAI_API_KEY, or OLLAMA in .env")
        return False

    except Exception as e:
        print(f"  ❌ LLM provider test failed: {e}")
        return False


def test_state_manager() -> bool:
    """Test state manager functionality."""
    print("\nTesting state manager...")
    import tempfile

    temp_db_path = None

    try:
        from src.state_manager import StateManager

        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        temp_db.close()
        temp_db_path = temp_db.name
        manager = StateManager(db_path=temp_db_path)

        test_user_id = 12345
        test_state = {"test": "data"}

        manager.update_state(test_user_id, test_state)
        retrieved = manager.get_state(test_user_id)

        if retrieved == test_state:
            print("  ✅ State manager basic operations work")
            return True
        print("  ❌ State manager data mismatch")
        return False

    except Exception as e:
        print(f"  ❌ State manager test failed: {e}")
        return False
    finally:
        if temp_db_path and os.path.exists(temp_db_path):
            try:
                os.unlink(temp_db_path)
            except OSError:
                pass


def main() -> bool:
    """Run all tests."""
    print("🧪 Testing Intelligent Joplin Librarian Setup")
    print("=" * 50)

    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("LLM Providers", test_llm_providers),
        ("State Manager", test_state_manager),
        ("Joplin Connection", test_joplin_connection),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("🧪 TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")

    print(f"\nPassed: {passed}/{total}")

    # Require imports, config, and LLM - Joplin is optional for starting
    required = ["Module Imports", "Configuration", "LLM Providers", "State Manager"]
    required_ok = all(r for n, r in results if n in required)

    if required_ok:
        print("\n🎉 Core setup OK! You can run the bot.")
        if passed < total:
            print("   (Joplin connection optional — start Joplin before saving notes)")
    else:
        print("\n⚠️  Some required tests failed. Check the output above.")
        print("   Make sure you've run ./setup.sh and configured your .env file.")

    return required_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
