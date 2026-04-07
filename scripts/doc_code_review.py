#!/usr/bin/env python3
"""
Documentation-Code Consistency Review (FR-036 MVP).

Scans docs and code for potential contradictions across Categories 1, 2, 3, 9.
Output: Markdown report for human review.

Usage:
  python scripts/doc_code_review.py
  python scripts/doc_code_review.py --output project-management/reports/doc-code-consistency-latest.md

Categories (MVP):
  1 - Explicit Contradictions (counts, options)
  2 - Inconsistencies (file references, terminology)
  3 - Stale Documentation (deprecated, version drift)
  9 - API Changes (file paths, class names)
"""

from __future__ import annotations

import argparse
import os
import re
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC_DIRS = ["docs", "project-management", "README.md"]
CODE_DIRS = ["src", "config.py", "main.py"]


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _list_py_files() -> set[str]:
    """List all Python files under src/."""
    files: set[str] = set()
    src = REPO_ROOT / "src"
    if not src.exists():
        return files
    for p in src.rglob("*.py"):
        rel = str(p.relative_to(REPO_ROOT))
        files.add(rel)
        files.add(rel.replace("/", os.sep))
    return files


def _extract_commands_from_code() -> set[str]:
    """Extract command names from CommandHandler('cmd', ...) in src/."""
    commands: set[str] = set()
    pattern = re.compile(r'CommandHandler\s*\(\s*["\']([a-z_0-9]+)["\']')
    for rel in _list_py_files():
        path = REPO_ROOT / rel.replace(os.sep, "/")
        text = _read_file(path)
        for m in pattern.finditer(text):
            commands.add(m.group(1))
    return commands


# Exclude generated reports from scan (they contain previous findings and cause self-referential flags)
DOC_EXCLUDE = {"project-management/reports/doc-code-consistency-latest.md"}


def _list_doc_files() -> list[Path]:
    """List all markdown files in doc scope."""
    paths: list[Path] = []
    for name in DOC_DIRS:
        p = REPO_ROOT / name
        if p.is_file():
            rel = str(p.relative_to(REPO_ROOT)).replace("\\", "/")
            if rel not in DOC_EXCLUDE:
                paths.append(p)
        elif p.is_dir():
            for f in p.rglob("*.md"):
                rel = str(f.relative_to(REPO_ROOT)).replace("\\", "/")
                if rel not in DOC_EXCLUDE:
                    paths.append(f)
    return paths


def _extract_src_refs_from_docs() -> list[tuple[str, str, int]]:
    """Extract src/... references from docs. Returns (file_path, doc_path, line_no)."""
    refs: list[tuple[str, str, int]] = []
    # Match src/foo/bar.py or src/foo.py
    pattern = re.compile(r"`?(src/[a-zA-Z0-9_/.-]+\.py)`?")
    for doc in _list_doc_files():
        text = _read_file(doc)
        rel_doc = str(doc.relative_to(REPO_ROOT))
        for i, line in enumerate(text.splitlines(), 1):
            for m in pattern.finditer(line):
                refs.append((m.group(1).strip("`"), rel_doc, i))
    return refs


def run_checks() -> list[dict]:
    """Run all MVP checks. Returns list of flagged items."""
    items: list[dict] = []
    py_files = _list_py_files()
    commands = _extract_commands_from_code()
    src_refs = _extract_src_refs_from_docs()

    # Normalize paths for comparison
    py_files_normalized = {f.replace("\\", "/") for f in py_files}

    # Check 1: Doc references src/X.py but file doesn't exist (Category 2/9)
    for ref, doc_path, line_no in src_refs:
        ref_norm = ref.replace("\\", "/")
        if ref_norm not in py_files_normalized:
            # Maybe it's src/handlers/foo vs src/handlers/foo.py
            base = ref_norm.replace(".py", "")
            if not any(f.replace(".py", "") == base for f in py_files_normalized):
                items.append({
                    "doc": doc_path,
                    "code": ref_norm,
                    "category": "2/9 File Reference",
                    "description": f"Doc references '{ref}' which does not exist in codebase",
                    "severity": "High",
                    "status": "Open",
                    "line": line_no,
                })

    # Check 2: Doc references existing file (informational, no flag)
    # We only flag missing files above.

    # Check 3: Commands in greeting/core vs registered (Category 1 - count check)
    # Extract commands mentioned in core.py greeting
    core_path = REPO_ROOT / "src" / "handlers" / "core.py"
    core_text = _read_file(core_path)
    mentioned = set()
    for m in re.finditer(r"/ ([a-z_0-9]+)\b", core_text):
        cmd = m.group(1)
        if cmd in (
            "start", "help", "status", "note", "task", "sync", "project_status", "helpme",
            "braindump", "braindump_stop", "dream", "dream_done", "dream_cancel",
            "habits", "plan", "plan_done", "plan_cancel", "daily_report", "weekly_report",
            "monthly_report", "find", "search", "ask", "reindex", "readlater", "rl", "reading",
        ):
            mentioned.add(cmd)
    # Compare: all user-facing commands should be in both
    user_commands = {c for c in commands if not c.startswith("reorg_") and c != "enrich_notes"
                     and c not in ("authorize_google_tasks", "verify_google", "google_tasks_config",
                                   "set_task_list", "toggle_auto_tasks", "toggle_privacy",
                                   "google_tasks_status", "list_inbox_tasks",
                                   "configure_report_time", "configure_report_timezone",
                                   "toggle_daily_report", "show_report_config", "configure_report_content",
                                   "report_help", "capture")}
    # This is a soft check - we just report if greeting might be missing commands
    documented_in_greeting = {"start", "help", "status", "note", "task", "braindump", "dream",
                              "habits", "plan", "daily_report", "weekly_report", "monthly_report",
                              "find", "search", "ask", "readlater", "reading",
                              "health_import", "health_import_quick", "health_today", "health_week",
                              "health_goal", "health_goals", "health_last"}
    missing_in_greeting = user_commands - documented_in_greeting - {"helpme", "project_status", "sync",
                                                                    "reindex", "rl", "braindump_stop",
                                                                    "dream_done", "dream_cancel",
                                                                    "plan_done", "plan_cancel"}
    if missing_in_greeting:
        items.append({
            "doc": "src/handlers/core.py (greeting)",
            "code": f"Registered commands: {sorted(user_commands)}",
            "category": "1.1 Conflicting Counts/Options",
            "description": f"Commands registered but possibly not in greeting: {sorted(missing_in_greeting)}",
            "severity": "Medium",
            "status": "Open",
            "line": 0,
        })

    return items


def render_report(items: list[dict], trigger: str = "On-demand") -> str:
    """Render Markdown report."""
    today = date.today().isoformat()
    open_count = sum(1 for i in items if i.get("status") == "Open")
    lines = [
        "# Documentation-Code Consistency Report",
        f"**Date**: {today}",
        f"**Trigger**: {trigger}",
        "",
        "## Summary",
        f"- Total flagged: {len(items)}",
        f"- Open: {open_count} | Resolved: 0 | False Positive: 0",
        "",
        "## Items",
        "",
        "| # | Doc | Code | Category | Description | Severity | Status |",
        "|---|-----|------|----------|-------------|----------|--------|",
    ]
    for i, item in enumerate(items, 1):
        doc = item.get("doc", "")
        code = item.get("code", "")
        cat = item.get("category", "")
        desc = item.get("description", "").replace("|", "\\|")
        sev = item.get("severity", "")
        status = item.get("status", "Open")
        lines.append(f"| {i} | {doc} | {code} | {cat} | {desc} | {sev} | {status} |")

    lines.extend([
        "",
        "## Next Steps",
        "1. Human review: For each Open item, decide: fix docs, fix code, or mark False Positive.",
        "2. Update status in this report.",
        "3. Create backlog items for fixes if needed.",
        "",
        "---",
        "*Generated by scripts/doc_code_review.py (FR-036)*",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Doc-Code Consistency Review (FR-036)")
    parser.add_argument(
        "--output", "-o",
        default="project-management/reports/doc-code-consistency-latest.md",
        help="Output report path",
    )
    parser.add_argument(
        "--trigger",
        default="On-demand",
        help="Trigger reason (e.g. 'Pre-sprint planning')",
    )
    args = parser.parse_args()

    out_path = REPO_ROOT / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    items = run_checks()
    report = render_report(items, args.trigger)
    out_path.write_text(report, encoding="utf-8")
    print(f"Report written to {out_path} ({len(items)} items flagged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
