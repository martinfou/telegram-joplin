# Sprint 6: Daily Priority Reports - Quick Start Guide

## Status: ✅ Ready for Testing

All Sprint 6 features are **implemented, integrated, and covered by defect fixes**. The bot is ready for manual integration testing.

---

## What's New in Sprint 6

### 7 New Commands for Daily Reports

```
/daily_report                              - Get on-demand priority report
/configure_report_time HH:MM               - Set delivery time (e.g., 09:00)
/configure_report_timezone TIMEZONE        - Set timezone (e.g., US/Eastern)
/toggle_daily_report on|off                - Enable/disable scheduled delivery
/show_report_config                        - View current settings
/configure_report_content LEVEL            - Set detail level (detailed/compact)
/report_help                               - Show report command help
```

All commands are now listed in `/helpme` for easy discovery.

---

## Quick Testing Checklist

### ✅ Phase 1: Smoke Test (5 minutes)

```bash
# 1. Start the bot
python main.py

# 2. In Telegram, send:
/start                           # Verify bot responds
/helpme                          # Verify report commands are listed
/daily_report                    # Get on-demand report
/show_report_config              # View default settings
```

**Expected Results:**
- Bot responds to all commands
- Report commands visible in /helpme
- On-demand report shows Joplin notes and/or Google Tasks
- Config shows default timezone (UTC) and time (08:00)

---

### ✅ Phase 2: Configuration Test (10 minutes)

```bash
# 1. Configure delivery time
/configure_report_time 14:00

# 2. Configure timezone
/configure_report_timezone US/Eastern

# 3. Verify settings
/show_report_config

# 4. Get updated report
/daily_report

# 5. Toggle reports on
/toggle_daily_report on

# 6. Check settings again
/show_report_config
```

**Expected Results:**
- Time changes to 14:00
- Timezone changes to US/Eastern
- Config shows updated values
- Reports enabled with "✓ Job scheduled" message
- Report generated successfully

---

### ✅ Phase 3: Scheduling Test (Varies by waiting time)

**Option A: Quick Test (1 minute from now)**
```bash
# 1. Configure for 1 minute from now
/configure_report_time 13:50         # (set to current time + 1 min)
/configure_report_timezone UTC

# 2. Enable reports
/toggle_daily_report on

# 3. Wait 1-2 minutes for automatic delivery
```

**Option B: Longer Test (Set for specific time)
```bash
# 1. Set for a time in the next 5 minutes
/configure_report_time 14:05         # (adjust to your current time + 5 min)

# 2. Enable reports
/toggle_daily_report on

# 3. Wait for delivery at configured time
# 4. Verify message received at correct time
```

**Expected Results:**
- Report delivered automatically at scheduled time
- Message appears at correct time in user's timezone
- Only one message per day (no duplicates)

---

### ✅ Phase 4: Feature Integration Test

```bash
# 1. Create a new Joplin note
# (Send a message to the bot that becomes a note)

# 2. Get immediate report
/daily_report

# 3. Verify new note appears in report

# 4. Check report includes tags and priorities
```

**Expected Results:**
- Newly created note appears in next report
- Report shows correct title and priority
- Tags are properly associated

---

## Recent Bug Fix

### Issue: Google Tasks Not Showing in Report
**Fixed in commit 4331560**

**What was wrong:**
- Report generator called non-existent `get_task_lists()` method
- Should have called `get_available_task_lists()`
- Method calls were async but TaskService methods are sync

**What's fixed:**
- Correct method names: `get_available_task_lists()` and `get_user_tasks()`
- Removed incorrect `await` keywords
- Added string conversion for user_id parameters
- Added filtering for completed tasks
- Improved error handling with `.get()` for dict access

**Result:** Google Tasks now properly fetched and included in reports

---

## Test Data Setup

### Create Sample Joplin Notes

Before testing, create notes in Joplin with these patterns:

**High Priority Note:**
```
Title: Fix critical defect in authentication
Tags: critical, security, urgent
Body: Login flow has security vulnerability that needs immediate fix
```

**Medium Priority Note:**
```
Title: Update documentation
Tags: documentation, documentation, important
Body: API docs need to be updated for v2.0
```

**Low Priority Note:**
```
Title: Code refactoring
Tags: tech-debt, low
Body: Refactor utilities module for better maintainability
```

### Create Sample Google Tasks

If Google Tasks is connected, create tasks:

```
🔴 Urgent: Review PR by end of day
🟠 Important: Schedule meeting with team lead
🟡 Normal: Update dependencies in project
```

---

## Monitoring During Tests

### Check Logs for:

✅ Success indicators:
```
INFO - Generating async report for user [ID]
INFO - Generating on-demand daily report for user [ID]
INFO - Daily report sent to user [ID]: X items
INFO - Scheduled daily report delivered
INFO - Scheduler started on bot startup
```

❌ Error indicators:
```
ERROR - Failed to fetch Google Tasks
ERROR - Failed to fetch Joplin notes
ERROR - Error in handle_configure_report_time
WARNING - Failed to schedule daily report
```

### Database Checks:

```sql
-- Check report configuration saved
SELECT * FROM report_configurations WHERE user_id = [YOUR_USER_ID];

-- Check daily reports logged
SELECT * FROM daily_reports WHERE user_id = [YOUR_USER_ID]
ORDER BY created_at DESC LIMIT 5;

-- Check scheduler history
SELECT * FROM task_sync_history WHERE user_id = [YOUR_USER_ID]
ORDER BY created_at DESC LIMIT 5;
```

---

## Common Issues & Solutions

### Issue 1: "No items in report"
**Cause:** Joplin has no notes or Google Tasks has no tasks
**Solution:** Create test notes in Joplin (see Test Data Setup above)

### Issue 2: "Failed to fetch Google Tasks"
**Cause:** Google Tasks not authorized or configured
**Solution:** Run `/authorize_google_tasks` and complete auth flow, OR disable Google Tasks if not using it

### Issue 3: "Error setting report time"
**Cause:** Invalid time format
**Solution:** Use 24-hour format HH:MM (e.g., 08:00, 14:30, 23:59)

### Issue 4: "Unknown timezone"
**Cause:** Invalid timezone string
**Solution:** Use pytz timezone names:
- US/Eastern, US/Central, US/Mountain, US/Pacific
- Europe/London, Europe/Paris, Europe/Berlin
- Asia/Tokyo, Asia/Shanghai, Asia/Hong_Kong
- UTC, GMT, Australia/Sydney

### Issue 5: Scheduled report never delivers
**Causes:**
- Bot not running at scheduled time
- Reports disabled (`toggle_daily_report off`)
- Scheduler not started (check logs for "Scheduler started")
**Solution:** Verify bot is running, enable reports, check logs

---

## Files Changed in Sprint 6

| File | Changes |
|------|---------|
| `src/report_generator.py` | 708 lines - Report engine with priority scoring |
| `src/scheduler_service.py` | 338 lines - APScheduler wrapper |
| `src/telegram_orchestrator.py` | 7 handlers + scheduler integration + /helpme update |
| `src/logging_service.py` | 4 new methods for config persistence |
| `database_schema.sql` | 47 new lines - new tables and indexes |
| `requirements.txt` | APScheduler>=3.10.0, pytz>=2024.1 |

---

## Full Integration Test Guide

For comprehensive testing with 40+ test cases, see:
**`project-management/sprints/SPRINT-06-INTEGRATION-TESTS.md`**

---

## Summary

✅ **Implementation**: 100% Complete
✅ **Bug Fixes**: All known issues fixed
✅ **Documentation**: Complete
✅ **Bot Tested**: Initializes successfully
⏳ **Manual Testing**: Ready to begin

**Next Step:** Run through the Quick Testing Checklist above to validate features!

---

**Last Updated:** 2026-01-24 (After defect fix commit 4331560)
**Status:** Production-Ready for Integration Testing
