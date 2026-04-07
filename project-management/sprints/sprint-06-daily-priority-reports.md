# Sprint 6: Daily Priority Reports (US-014)

**Sprint Goal**: Deliver unified daily priority reports aggregating Joplin notes and Google Tasks with on-demand and scheduled delivery.

**Status**: ✅ Complete

**Duration**: 2025-02-03 - 2025-02-16 (2 weeks)
**Team Velocity**: 8 points (full feature)
**Sprint Planning Date**: 2025-01-24
**Sprint Start Date**: 2025-02-03
**Sprint Review Date**: 2025-02-16
**Sprint Retrospective Date**: 2025-02-16

## Sprint Overview

**Focus Areas**:
- Unified report aggregation from Joplin and Google Tasks
- On-demand report generation (/daily_report command)
- Scheduled automatic delivery with APScheduler
- User configuration and customization
- Priority ranking algorithm
- Completion tracking
- Comprehensive testing

**Key Deliverables**:
- Report generation engine with priority ranking
- Scheduled delivery with timezone support
- 7 Telegram configuration commands
- Full database schema with analytics
- Integration with existing Joplin and Google Tasks clients
- Comprehensive test suite

**Dependencies**:
- Joplin integration (✅ Complete - US-005)
- Google Tasks integration (✅ Complete - US-012)
- Logging service (✅ Complete - US-010)
- Conversation state management (✅ Complete - US-007)

**Risks & Blockers**:
- APScheduler timezone handling (Medium risk - mitigated by UTC + user timezone config)
- Matching priority tags across systems (Medium risk - documented algorithm)
- Performance on large note/task lists (Low risk - use indexes and pagination)

---

## User Stories

### Story 1: Daily Priority Report Generation - 8 Points

**User Story**: As a busy user managing multiple tasks and notes, I want to receive a daily summary of the most important items that need my attention, so that I can prioritize my work and ensure critical actions are not forgotten.

**Acceptance Criteria**:
- [x] Daily report aggregates Joplin notes (high-priority tags) and Google Tasks (incomplete)
- [x] On-demand generation via /daily_report command
- [x] Scheduled automatic delivery with configurable time
- [x] Priority ranking across both sources
- [x] Completion tracking since last report
- [x] All 7 configuration commands implemented
- [x] Database logging for all reports and interactions
- [x] Timezone support for accurate scheduling
- [x] User can customize report content
- [x] Edge cases handled (no items, mixed priority levels)

**Reference Documents**:
- US-014: Daily Priority Report for Review and Action Items
- Joplin Client API documentation
- Google Tasks API documentation
- APScheduler documentation

**Technical References**:
- File: `src/telegram_orchestrator.py` - Command handlers
- File: `src/report_generator.py` (new) - Report generation logic
- File: `src/task_service.py` - Google Tasks client (already exists)
- File: `src/joplin_client.py` - Joplin note retrieval
- File: `src/logging_service.py` - Report logging
- File: `database_schema.sql` - Report tables
- File: `src/scheduler_service.py` (new) - APScheduler integration

**Story Points**: 8

**Priority**: 🟠 High

**Status**: ✅ Complete

**Backlog Reference**: [US-014](../backlog/user-stories/US-014-daily-priority-report.md)

**Tasks**:

| Task ID | Task Description | Class/Method Reference | Document Reference | Status | Points | Assignee |
|---------|------------------|------------------------|---------------------|--------|--------|----------|
| T-001 | Create report data model and priority scoring algorithm | `report_generator.py:ReportGenerator.score_items()` | US-014 Priority Algorithm | ✅ | 1 | Claude Code |
| T-002 | Implement report aggregation (Joplin + Google Tasks) | `report_generator.py:ReportGenerator.generate_report()` | US-014 Report Components | ✅ | 2 | Claude Code |
| T-003 | Format report for Telegram message display | `report_generator.py:ReportGenerator.format_message()` | US-014 Message Format | ✅ | 1 | Claude Code |
| T-004 | Implement /daily_report on-demand command | `telegram_orchestrator.py:handle_daily_report()` | US-014 Telegram Commands | ✅ | 1 | Claude Code |
| T-005 | Create scheduler service with APScheduler | `scheduler_service.py` (new) | US-014 Scheduled Delivery | ✅ | 1.5 | Claude Code |
| T-006 | Implement all 7 configuration commands | `telegram_orchestrator.py:handle_config_*()` | US-014 Configuration | ✅ | 1 | Claude Code |
| T-007 | Add database schema for reports and configuration | `database_schema.sql` | US-014 Database Schema | ✅ | 0.5 | Claude Code |

**Total Task Points**: 8

---

## Sprint Summary

**Total Story Points**: 8
**Total Task Points**: 8
**Additional Work**: Testing and defect fixes (estimated 2-3 points)
**Estimated Total Effort**: 10-11 points
**Sprint Duration**: 2 weeks (realistic for medium-complexity feature)

**Sprint Burndown Plan**:
- Feb 3-4: Tasks T-001, T-002 (Priority algorithm + aggregation) - 3 points
- Feb 5-7: Tasks T-003, T-004 (Telegram integration) - 2 points
- Feb 10-12: Tasks T-005, T-006 (Scheduler + commands) - 2.5 points
- Feb 13-14: Tasks T-007 + testing (Database + comprehensive tests) - 2 points
- Feb 15-16: Defect fixes, documentation, review

---

## Technical Implementation Plan

### Architecture Overview

```
User Message
    ↓
telegram_orchestrator.py (command handlers)
    ↓
    ├─→ ReportGenerator (generate_report)
    │   ├─→ Fetch Joplin notes (joplin_client.py)
    │   ├─→ Fetch Google Tasks (task_service.py)
    │   ├─→ Score and rank items (priority algorithm)
    │   └─→ Format message
    │
    ├─→ SchedulerService (APScheduler)
    │   ├─→ Schedule report delivery
    │   ├─→ Handle timezone conversions
    │   └─→ Execute scheduled tasks
    │
    └─→ LoggingService (log reports)
        └─→ database (daily_reports, report_configurations)
```

### Files to Create

1. **`src/report_generator.py`** (NEW - ~300 lines)
   - `ReportGenerator` class
   - `score_items()` - Priority ranking algorithm
   - `generate_report()` - Aggregate Joplin + Google Tasks
   - `format_message()` - Telegram message formatting
   - `get_completed_items()` - Track completed items since last report

2. **`src/scheduler_service.py`** (NEW - ~150 lines)
   - `SchedulerService` class
   - Initialize APScheduler with timezone support
   - `schedule_daily_report()` - Schedule user's report
   - `cancel_daily_report()` - Cancel scheduled report
   - `reschedule_daily_report()` - Update delivery time

### Files to Modify

1. **`src/telegram_orchestrator.py`**
   - Add command handler: `handle_daily_report()` - /daily_report command
   - Add command handler: `handle_configure_report_time()` - /configure_report_time
   - Add command handler: `handle_configure_report_timezone()` - /configure_report_timezone
   - Add command handler: `handle_toggle_daily_report()` - /toggle_daily_report
   - Add command handler: `handle_show_report_config()` - /show_report_config
   - Add command handler: `handle_configure_report_content()` - /configure_report_content
   - Add command handler: `handle_report_help()` - /report_help
   - Initialize scheduler on bot startup

2. **`src/logging_service.py`**
   - Add `save_report_configuration()` - Save user's report config
   - Add `get_report_configuration()` - Retrieve user's config
   - Add `log_daily_report()` - Log report generation and metrics
   - Add `get_completed_since_last_report()` - Track completion

3. **`database_schema.sql`**
   - Add `report_configurations` table
   - Add `daily_reports` table
   - Add indexes for performance

4. **`requirements.txt`**
   - Add `APScheduler>=3.10.0` for scheduling

### Report Components Structure

```python
class ReportData:
    critical_items: List[ReportItem]      # Overdue, blocking
    high_priority_items: List[ReportItem] # Due today, high impact
    medium_priority_items: List[ReportItem]
    low_priority_items: List[ReportItem]
    pending_clarification: List[str]      # Notes awaiting response
    completed_items: List[str]            # Since last report
    joplin_count: int
    google_tasks_count: int
    total_items: int
    generated_at: datetime
```

### Priority Scoring Algorithm

```python
def score_item(item) -> float:
    priority_level = map_priority_to_score(item.priority)  # 0-5
    urgency = calculate_urgency(item.due_date)             # 0-3
    impact = get_item_impact(item)                          # 1-3
    overdue_penalty = calculate_overdue(item.due_date)     # -2 per day

    score = (priority_level * 10) + (urgency * 8) + (impact * 5) - overdue_penalty
    return score
```

### Telegram Message Format

```
📊 Daily Priority Report - Jan 23, 2025
📊 9 items total (5 from Joplin + 4 from Google Tasks)

🔴 CRITICAL (2 items)
• Follow up with client - OVERDUE since Jan 20 (Google Task)
• Complete Q1 report - OVERDUE (Joplin note #urgent)

🟠 HIGH PRIORITY (4 items)
📝 Joplin Notes (2):
  • Prepare project presentation - Due today (#important)
  • Review Q1 budget - Due today (#work)

✅ Google Tasks (2):
  • Schedule team meeting - Due today
  • Finalize contract review - Due Jan 24

⏳ PENDING CLARIFICATION (2 items)
• Meeting notes from yesterday - awaiting your response
• Project plan draft - waiting for feedback

✅ COMPLETED TODAY (3 items)
• Design homepage mockup (Joplin)
• Update project documentation (Joplin)
• Approve vendor quote (Google Task)

💡 RECOMMENDATION
Start with: "Follow up with client" (OVERDUE + high impact)
Then: "Complete Q1 report" (OVERDUE + blocking other work)

---
🔗 /daily_report - Generate another report now
⚙️ /show_report_config - View your settings
```

### Database Schema

**`report_configurations` Table**:
```sql
CREATE TABLE report_configurations (
    user_id INTEGER PRIMARY KEY,
    enabled BOOLEAN DEFAULT TRUE,
    delivery_time TIME DEFAULT '08:00',
    timezone VARCHAR(100) DEFAULT 'UTC',
    include_critical BOOLEAN DEFAULT TRUE,
    include_high BOOLEAN DEFAULT TRUE,
    include_medium BOOLEAN DEFAULT FALSE,
    include_low BOOLEAN DEFAULT FALSE,
    include_google_tasks BOOLEAN DEFAULT TRUE,
    include_clarification_pending BOOLEAN DEFAULT TRUE,
    detail_level VARCHAR(20) DEFAULT 'detailed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES telegram_users(user_id)
);
```

**`daily_reports` Table**:
```sql
CREATE TABLE daily_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    report_date DATE NOT NULL,
    scheduled_time TIME,
    joplin_items_count INTEGER,
    google_tasks_count INTEGER,
    clarification_items_count INTEGER,
    critical_items INTEGER,
    high_items INTEGER,
    medium_items INTEGER,
    low_items INTEGER,
    completed_since_last INTEGER,
    telegram_message_id INTEGER,
    generated_by VARCHAR(20) DEFAULT 'scheduled',
    user_action VARCHAR(50),
    action_timestamp DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES telegram_users(user_id),
    UNIQUE(user_id, report_date)
);

CREATE INDEX idx_daily_reports_user_date ON daily_reports(user_id, report_date);
CREATE INDEX idx_daily_reports_created ON daily_reports(created_at);
```

---

## Success Criteria for Sprint 6

- ✅ /daily_report command generates and sends report immediately
- ✅ Scheduled reports deliver at configured time in user's timezone
- ✅ Report aggregates both Joplin (priority tags) and Google Tasks (incomplete)
- ✅ Priority ranking works across both sources
- ✅ All 7 configuration commands implemented and working
- ✅ User can customize priority levels, timezone, delivery time
- ✅ Report logs are stored in database for analytics
- ✅ Completion tracking shows items completed since last report
- ✅ Edge cases handled (empty reports, all one priority level, etc)
- ✅ Timezone support for accurate scheduling
- ✅ Comprehensive testing (unit + integration)
- ✅ Documentation complete
- ✅ Production ready

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| APScheduler timezone handling | Medium | Medium | Use pytz for explicit timezone conversions, test thoroughly |
| Large Joplin/Tasks lists slow report | Low | Medium | Implement pagination, add limits (e.g., top 20 items) |
| Priority algorithm produces unexpected ranks | Medium | Low | Implement scoring review command, allow user feedback |
| Scheduler failures in production | Low | High | Add health checks, error logging, restart capability |
| Database schema issues | Low | Medium | Test schema before production, prepare rollback |

**Overall Risk**: MEDIUM-LOW - Feature is complex but dependencies are stable

---

## Implementation Notes

### Key Decisions

1. **Data Aggregation**: Use direct Joplin + Google Tasks API calls to get real-time data rather than caching
2. **Scheduling**: Use APScheduler with timezone support via pytz
3. **Priority Tags**: Look for tags: #urgent, #critical, #important, #high, #medium, #low
4. **Completion Tracking**: Query last report timestamp, count items completed since then
5. **Timezone Strategy**: Store user timezone, convert delivery time to UTC for scheduling

### Testing Strategy

- Unit tests for priority scoring algorithm
- Unit tests for message formatting
- Integration tests for Joplin + Google Tasks aggregation
- Integration tests for scheduler (mock time)
- Tests for all 7 configuration commands
- Edge case tests (empty reports, mixed priorities, special characters)
- Timezone conversion tests

### Deployment Considerations

- Add APScheduler to requirements.txt
- Initialize scheduler on bot startup
- Run database migration for new tables
- Verify timezone database installed (pytz)
- Test with real Joplin and Google Tasks instances

---

## References

- **Feature US-014**: [Daily Priority Report](../backlog/user-stories/US-014-daily-priority-report.md)
- **Sprint 5 Results**: [Sprint 5 Completion](sprint-05-user-engagement-features.md)
- **Product Backlog**: [Product Backlog](../backlog/product-backlog.md)
- **Sprint & Backlog Planning**: [Planning Document](../docs/sprint-and-backlog-planning.md)
- **APScheduler Docs**: https://apscheduler.readthedocs.io/
- **Python pytz**: https://pypi.org/project/pytz/

---

**Last Updated**: 2025-01-24
**Version**: 1.0
**Status**: Sprint Planning - Scope Confirmed (8 points, 2 weeks, Full Feature)
