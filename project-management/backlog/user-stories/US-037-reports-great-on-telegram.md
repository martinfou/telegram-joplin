# User Story: US-037 - Reports Look Great on Telegram

**Status**: ✅ Completed  
**Priority**: 🟡 Medium  
**Story Points**: 5  
**Created**: 2026-03-05  
**Updated**: 2026-03-06  
**Assigned Sprint**: Backlog

## Description

Improve the visual presentation of daily, weekly, and monthly reports when delivered via Telegram. Reports currently use plain text with ASCII separators (`====`, `----`) and emojis, but do not leverage Telegram's formatting capabilities. This feature will make reports visually polished, scannable, and delightful to read on mobile using **monospace tables**.

## Design Approach: Monospace Tables

**Chosen design.** Use `<pre>` blocks with Unicode box-drawing characters (`┌─┬─┐`, `│`, `└─┴─┘`) for structured tables. Monospace ensures columns align correctly across devices.

**Daily report** — Priority tasks table (PRIORITY | ITEM | SOURCE); Joplin notes table (# | Title).  
**Weekly report** — Metrics table (Metric | This | vs Last); by-day bar chart.  
**Monthly report** — Overview table (Metric | This Mo | Change); weekly trend bars.

Use `parse_mode="HTML"` with `<pre>...</pre>` for table blocks. LLM title shortening keeps columns narrow (~40 chars).

### Design mockups

**Daily:**
```
📊 Daily Priority Report — Mar 5, 2026

┌────────────┬─────────────────────────────┬──────────┐
│ PRIORITY   │ ITEM                        │ SOURCE   │
├────────────┼─────────────────────────────┼──────────┤
│ 🔴 Critical│ Q4 budget presentation      │ 📝 Note  │
│ 🔴 Critical│ Fix auth defect in prod        │ ✅ Task  │
│ 🟠 High    │ Review PR #142              │ ✅ Task  │
└────────────┴─────────────────────────────┴──────────┘

📝 Joplin Notes (7)
┌────┬──────────────────────────────────┐
│ #  │ Title                            │
├────┼──────────────────────────────────┤
│ 1  │ Project Alpha status             │
│ 2  │ Meeting notes – Tuesday          │
└────┴──────────────────────────────────┘
```

**Weekly:** Metrics table (Metric | This | vs Last); by-day bars.  
**Monthly:** Overview table (Metric | This Mo | Change); weekly trend bars.

## User Story

As a user who receives daily, weekly, and monthly reports in Telegram,
I want reports to be beautifully formatted with clear hierarchy, proper typography, and mobile-friendly layout,
so that I can quickly scan and act on my priorities without squinting at walls of plain text.

## Current State

- **Daily report** (`format_report_message`): Plain text, ASCII separators, emojis. No `parse_mode`.
- **Weekly report** (`format_weekly_report`): Plain text, emojis, ASCII bars (`█░`). No `parse_mode`.
- **Monthly report** (`format_report`): Uses Markdown (`#`, `##`, `|` tables) but sent without `parse_mode` — renders as raw text.
- All reports sent via `reply_text(message)` or `send_message(chat_id=..., text=message)` with no formatting.

## Proposed Improvements

1. **Monospace tables** — Use `<pre>` blocks with Unicode box-drawing characters for structured tables (priority tasks, Joplin notes, metrics).
2. **parse_mode="HTML"** — Wrap table blocks in `<pre>...</pre>` so monospace alignment renders correctly.
3. **Visual hierarchy** — Section headers above tables; emojis for priority levels (🔴🟠🟡🟢).
4. **Consistent formatting** — Same table style across daily, weekly, and monthly reports.
5. **Message length handling** — Split long reports into multiple messages if exceeding Telegram's 4096-character limit.
6. **Escape special characters** — Ensure user-generated content is escaped for HTML (`<`, `>`, `&`) inside `<pre>` blocks.
7. **LLM title shortening** — Shorten long titles to essential meaning (~40 chars) so table columns stay narrow and readable.

## Acceptance Criteria

- [ ] Daily report uses monospace tables (priority tasks, Joplin notes) with `parse_mode="HTML"` and `<pre>` blocks.
- [ ] Weekly report uses monospace tables (metrics, by-day breakdown) with same style.
- [ ] Monthly report uses monospace tables (overview, weekly trends) with same style.
- [ ] All user-generated text is escaped for HTML to prevent parse failures.
- [ ] Reports exceeding 4096 characters are split into multiple messages with clear continuation (e.g., "Part 1/2").
- [ ] Formatting is consistent across all three report types.
- [ ] Reports remain readable and scannable on mobile (primary Telegram use case).
- [ ] Long titles are shortened (via LLM) to essential meaning when displaying in report items.
- [ ] Existing tests pass; new tests cover formatting and escaping.

## Business Value

- **User delight** — Reports feel professional and polished, increasing engagement with the feature.
- **Reduced cognitive load** — Clear visual hierarchy helps users quickly find what matters.
- **Trust** — Polished output signals quality and care, reinforcing the product's value.
- **Differentiation** — Many bots send plain-text dumps; great formatting stands out.

## Technical Requirements

- Use `parse_mode="HTML"` with `<pre>...</pre>` for monospace table blocks.
- Implement escaping for user content: `html.escape()` for text inside `<pre>` blocks.
- Add table builder helpers: fixed column widths, Unicode box chars (`┌─┬─┐`, `│`, `├─┼─┤`, `└─┴─┘`).
- Add message splitting logic when `len(message) > 4096`.
- LLM-based title shortening: pass long titles through LLM to extract essential phrase (e.g., max ~40 chars); fallback to simple truncation if LLM unavailable or slow.
- Update `ReportGenerator.format_report_message`, `format_report_compact`, `format_report_detailed`.
- Update `WeeklyReportGenerator.format_weekly_report`.
- Update `MonthlyReportGenerator.format_report`.
- Update handlers in `src/handlers/reports.py` to pass `parse_mode` and handle multi-message sends.
- Ensure compatibility with scheduled report delivery (`send_scheduled_report`, `send_scheduled_weekly_report`).

## Reference Documents

- [US-014 Daily Priority Report](US-014-daily-priority-report.md)
- [US-015 Weekly Review Report](US-015-weekly-review-report.md)
- [US-031 Monthly Review Report](US-031-monthly-review-report.md)
- [Telegram Bot API: Formatting](https://core.telegram.org/bots/api#formatting-options)

## Technical References

- `src/report_generator.py` — `format_report_message`, `format_report_compact`, `format_report_detailed`, `_format_item_line`
- `src/weekly_report_generator.py` — `format_weekly_report`
- `src/monthly_report_generator.py` — `format_report`
- `src/handlers/reports.py` — `_daily_report`, `_weekly_report`, `_monthly_report`, `send_scheduled_report`, `send_scheduled_weekly_report`
- `src/llm_orchestrator.py` — For LLM-based title shortening (optional)

## Dependencies

- None (reports already exist; this is a formatting enhancement)

## Notes

- **Monospace tables**: Use `<pre>` so Unicode box-drawing chars and column alignment render correctly. No need for HTML `<table>`.
- **Column widths**: Fix widths (e.g., 12 / 30 / 10 chars) so tables align; LLM shortening helps fit titles.
- Consider a shared `report_formatter.py` or `telegram_tables.py` module for table building and escaping.
- **LLM title shortening**: Batch titles per report; fallback to truncation with ellipsis at ~40 chars.

## History

- 2026-03-05 - Created
- 2026-03-06 - Added LLM title shortening for essential-only display
- 2026-03-06 - Chosen design: monospace tables with `<pre>` and Unicode box-drawing
