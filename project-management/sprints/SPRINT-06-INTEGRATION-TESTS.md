# Sprint 6: Daily Priority Reports - Integration Test Scenarios

## Overview

This document provides comprehensive manual integration testing scenarios for Sprint 6 (Daily Priority Reports feature). These tests validate the complete feature implementation including report generation, scheduling, configuration, and database logging.

**Test Environment Requirements:**
- Running Telegram bot with Sprint 6 code
- Live Joplin instance with sample notes
- Google Tasks integration (optional, but recommended)
- SQLite database initialized with schema
- User whitelist configured with test user ID

---

## Test Setup

### Prerequisites

1. **Joplin Instance**
   - Running and accessible at configured URL
   - Sample notes with various priorities created:
     - High priority notes (marked with tags/titles)
     - Medium priority notes
     - Low priority notes
   - Sample folders/notebooks for organization

2. **Google Tasks (Optional)**
   - OAuth credentials configured (if testing Google Tasks integration)
   - Sample task lists created
   - Sample tasks with various completion states

3. **Database**
   - Initialize with `database_schema.sql` if not done
   - Verify all report-related tables exist:
     - `report_configurations`
     - `daily_reports`
     - `task_links`
     - `task_sync_history`

4. **Bot Configuration**
   - TELEGRAM_BOT_TOKEN configured
   - User whitelist includes test user ID
   - JOPLIN_BASE_URL and JOPLIN_TOKEN configured
   - APScheduler running (initialized on bot start)

### Test Data Preparation

Create sample notes in Joplin for testing:

```
🔴 CRITICAL: Fix authentication defect [High Priority]
- Description: Security issue in login flow
- Due: Today
- Tags: critical, security, urgent

🟠 HIGH: Implement user dashboard [High Priority]
- Description: New feature for user analytics
- Due: Tomorrow
- Tags: feature, important

🟡 MEDIUM: Update documentation [Medium Priority]
- Description: API documentation needs refresh
- Due: Next week
- Tags: documentation

🟢 LOW: Code cleanup [Low Priority]
- Description: Refactor utilities module
- Due: Eventually
- Tags: tech-debt, low
```

---

## Test Suite 1: On-Demand Report Generation

### T1.1: Basic /daily_report command

**Objective:** Verify on-demand report generation works correctly

**Steps:**
1. Send `/daily_report` command to bot
2. Observe response within 5 seconds

**Expected Results:**
- Bot generates report message with all sections
- Message includes:
  - Summary section (total counts)
  - Critical items (if any)
  - High priority items (if any)
  - Medium priority items (if any)
  - Low priority items (if any)
  - Pending clarifications section
- Message is properly formatted with emoji indicators
- Log entry created in `daily_reports` table

**Pass Criteria:**
- Report received within 5 seconds
- All expected sections present
- No error messages
- Database record created

---

### T1.2: Report with only Joplin notes

**Objective:** Verify report generation from Joplin-only data

**Steps:**
1. Ensure Google Tasks integration is disabled or no tasks exist
2. Send `/daily_report`
3. Verify response

**Expected Results:**
- Report shows only Joplin notes
- Google Tasks section not included if empty
- Priority scoring correctly calculated
- Joplin notes displayed with titles and priorities

**Pass Criteria:**
- Report generated successfully
- Only Joplin sources shown
- Correct item counts

---

### T1.3: Report with Joplin and Google Tasks

**Objective:** Verify unified report aggregation from both sources

**Steps:**
1. Ensure both Joplin and Google Tasks are available
2. Have incomplete tasks in Google Tasks
3. Send `/daily_report`
4. Observe aggregation

**Expected Results:**
- Report includes both Joplin notes and Google Tasks
- Items ranked by unified priority score
- Mixed source items sorted correctly
- Clear indication of source (Joplin vs Google Tasks)

**Pass Criteria:**
- Both sources aggregated in single report
- Correct count for each source type
- Proper ranking across sources

---

### T1.4: Report respects content filters

**Objective:** Verify report formatting options

**Steps:**
1. Send `/daily_report`
2. Observe report format/detail level

**Expected Results:**
- Report uses configured detail level
- Shows appropriate amount of information
- No excessive verbosity or truncation

**Pass Criteria:**
- Report format matches expectations
- Information density appropriate

---

## Test Suite 2: Configuration Commands

### T2.1: Configure report delivery time

**Objective:** Set report delivery time

**Steps:**
1. Send `/configure_report_time 09:30`
2. Observe response
3. Send `/show_report_config` to verify

**Expected Results:**
- Bot confirms time set to 09:30
- Timezone shown in response
- Config command shows updated time
- Database updated: `report_configurations.delivery_time = '09:30'`
- Scheduler job created/updated
- Positive feedback message received

**Pass Criteria:**
- Time accepted and confirmed
- Config reflects change
- Job scheduled message shown

---

### T2.2: Configure report timezone

**Objective:** Set user's timezone for scheduling

**Steps:**
1. Send `/configure_report_timezone US/Eastern`
2. Observe response
3. Send `/show_report_config` to verify

**Expected Results:**
- Bot confirms timezone set to US/Eastern
- Delivery time shown in response
- Database updated: `report_configurations.timezone = 'US/Eastern'`
- Scheduler recalculates job trigger for new timezone
- Confirmation message received

**Pass Criteria:**
- Timezone accepted (valid pytz timezone)
- Config reflects change
- Job rescheduled message shown

---

### T2.3: Invalid timezone handling

**Objective:** Verify timezone validation

**Steps:**
1. Send `/configure_report_timezone InvalidTZ`
2. Observe error handling

**Expected Results:**
- Bot rejects invalid timezone
- Error message explains valid format
- Database NOT updated
- No scheduler job created
- Fallback suggestion provided

**Pass Criteria:**
- Invalid timezone rejected gracefully
- Database unchanged
- User informed of error

---

### T2.4: Invalid time format handling

**Objective:** Verify time validation

**Steps:**
1. Send `/configure_report_time 25:00`
2. Send `/configure_report_time 14:60`
3. Send `/configure_report_time abc`
4. Observe all responses

**Expected Results:**
- All invalid formats rejected
- Error messages explain correct format
- Database NOT updated
- Helpful examples provided

**Pass Criteria:**
- All invalid formats rejected
- Clear error messages shown
- Database integrity maintained

---

### T2.5: Show report configuration

**Objective:** Display current report settings

**Steps:**
1. Configure time to 10:00
2. Configure timezone to Europe/London
3. Send `/show_report_config`
4. Observe response

**Expected Results:**
- Config message shows:
  - Current delivery time: 10:00
  - Current timezone: Europe/London
  - Enabled/disabled status
  - Content filter settings
  - Next scheduled delivery (if applicable)
- All settings match database values

**Pass Criteria:**
- All config options displayed
- Values match database
- Proper formatting

---

### T2.6: Toggle daily reports on

**Objective:** Enable scheduled daily reports

**Steps:**
1. Send `/toggle_daily_report on`
2. Observe response
3. Check scheduler status

**Expected Results:**
- Bot confirms daily reports enabled
- Scheduled time and timezone shown
- APScheduler job created
- Database updated: `report_configurations.enabled = TRUE`
- Confirmation message shows "✓ Job scheduled"
- Scheduler has active job for user

**Pass Criteria:**
- Reports enabled successfully
- Job scheduled and active
- Database reflects enabled state

---

### T2.7: Toggle daily reports off

**Objective:** Disable scheduled daily reports

**Steps:**
1. Ensure reports enabled first
2. Send `/toggle_daily_report off`
3. Observe response
4. Check scheduler status

**Expected Results:**
- Bot confirms daily reports disabled
- APScheduler job cancelled
- Database updated: `report_configurations.enabled = FALSE`
- Confirmation message shows "✓ Job cancelled"
- Scheduler no longer has job for user

**Pass Criteria:**
- Reports disabled successfully
- Job cancelled and removed
- Database reflects disabled state

---

### T2.8: Toggle with various formats

**Objective:** Verify command accepts different boolean formats

**Steps:**
1. Send `/toggle_daily_report yes`
2. Send `/toggle_daily_report no`
3. Send `/toggle_daily_report true`
4. Send `/toggle_daily_report false`
5. Send `/toggle_daily_report 1`
6. Send `/toggle_daily_report 0`

**Expected Results:**
- All valid formats accepted
- yes/true/1 → enable reports
- no/false/0 → disable reports
- Appropriate messages shown for each

**Pass Criteria:**
- All valid formats work
- Correct interpretation (enable/disable)

---

### T2.9: Report help command

**Objective:** Display available report commands

**Steps:**
1. Send `/report_help`
2. Observe response

**Expected Results:**
- Message lists all 7 report-related commands:
  - `/daily_report` - Get on-demand report
  - `/configure_report_time HH:MM` - Set delivery time
  - `/configure_report_timezone TIMEZONE` - Set timezone
  - `/toggle_daily_report on|off` - Enable/disable scheduled
  - `/show_report_config` - Show current settings
  - `/configure_report_content` - Set content filters
  - `/report_help` - Show this help
- Usage examples provided
- Help text clear and actionable

**Pass Criteria:**
- All commands listed
- Examples provided
- Help text is clear

---

## Test Suite 3: Scheduling and Timezone Support

### T3.1: Schedule report for specific time

**Objective:** Verify scheduler delivers report at configured time

**Steps:**
1. Send `/configure_report_time HH:MM` (set to 1 minute from now)
2. Send `/configure_report_timezone UTC`
3. Wait for 2 minutes
4. Observe if report received at scheduled time

**Expected Results:**
- Report delivered approximately 1 minute after configuration
- Delivery time matches configured time (within 1 minute tolerance)
- Message received at correct time
- Database `daily_reports` entry created with `generated_by = 'scheduled'`
- Scheduler executed job successfully
- No duplicate messages

**Pass Criteria:**
- Report delivered at scheduled time
- Single delivery (no duplicates)
- Database record created with correct timestamp

---

### T3.2: Timezone-aware scheduling

**Objective:** Verify scheduler respects user's timezone

**Steps:**
1. Set timezone to `US/Pacific`
2. Set time to 08:00
3. Note current UTC offset for Pacific time
4. Verify scheduler created job with correct timezone

**Expected Results:**
- Job trigger shows correct timezone
- Cron expression calculated for specified timezone
- Report delivered at 08:00 Pacific (not 08:00 UTC)
- Logs show timezone used in calculation

**Pass Criteria:**
- Job uses correct timezone
- Report timing reflects timezone offset
- Logs confirm timezone handling

---

### T3.3: Reschedule existing job

**Objective:** Verify scheduler updates existing jobs

**Steps:**
1. Configure time to 10:00
2. Configure timezone to US/Eastern
3. Wait 30 seconds
4. Reconfigure time to 14:00
5. Verify job updated (not duplicated)

**Expected Results:**
- Old job cancelled
- New job created with new time
- No duplicate jobs in scheduler
- Only one active job per user
- Latest configuration used

**Pass Criteria:**
- Job properly rescheduled
- No duplicate jobs
- Updated time is active

---

### T3.4: Bot restart preserves schedules

**Objective:** Verify scheduler restarts with persisted config

**Steps:**
1. Configure reports (time, timezone, enable)
2. Stop the bot
3. Restart the bot
4. Check scheduler status
5. Verify job still scheduled

**Expected Results:**
- Configuration persisted in database
- Scheduler reads config on startup
- Jobs recreated from database
- Schedule continues as expected
- No manual reconfiguration needed

**Pass Criteria:**
- Config persisted across restarts
- Jobs restored on restart
- Scheduling continues uninterrupted

---

## Test Suite 4: Database Logging and Audit Trail

### T4.1: Report generation logged in database

**Objective:** Verify all report generations recorded

**Steps:**
1. Send `/daily_report` (on-demand)
2. Let scheduled report run (or trigger manually)
3. Query `daily_reports` table
4. Verify entries exist

**Expected Results:**
- Row in `daily_reports` for each generation
- Columns populated:
  - `user_id`: Correct user ID
  - `report_date`: Today's date
  - `joplin_items_count`: Correct count
  - `google_tasks_count`: Correct count
  - `clarification_items_count`: Count of pending
  - `critical_items`, `high_items`, `medium_items`, `low_items`: Correct counts
  - `generated_by`: 'on_demand' or 'scheduled'
  - `created_at`: Current timestamp
- `UNIQUE(user_id, report_date)` constraint prevents duplicates

**Pass Criteria:**
- All report generations logged
- All fields populated correctly
- Database constraints working

---

### T4.2: Configuration changes logged

**Objective:** Verify configuration persistence

**Steps:**
1. Send multiple configuration commands
2. Query `report_configurations` table
3. Verify all changes persisted

**Expected Results:**
- Row exists for user in `report_configurations`
- All settings correctly stored:
  - `enabled`: Boolean
  - `delivery_time`: HH:MM format
  - `timezone`: Valid pytz timezone
  - `include_critical`: Boolean
  - `include_high`: Boolean
  - `include_medium`: Boolean
  - `include_low`: Boolean
  - `include_google_tasks`: Boolean
  - `include_clarification_pending`: Boolean
  - `detail_level`: 'detailed' or other
  - `updated_at`: Updated on each config change

**Pass Criteria:**
- Config table properly populated
- All settings persist correctly
- Timestamps accurate

---

### T4.3: Task sync history recorded

**Objective:** Verify task synchronization tracked (if Google Tasks enabled)

**Steps:**
1. Enable Google Tasks
2. Trigger a report that includes Google Tasks
3. Query `task_sync_history` table
4. Verify entries

**Expected Results:**
- Entries in `task_sync_history` for each sync operation
- Fields populated:
  - `user_id`: Correct user
  - `google_task_id`: Task ID from Google
  - `action`: 'created', 'updated', 'completed', or 'deleted'
  - `sync_direction`: 'joplin_to_google' or 'google_to_joplin'
  - `sync_result`: 'success', 'failed', or 'partial'
  - `created_at`: When sync occurred

**Pass Criteria:**
- Sync operations properly recorded
- All fields populated
- Audit trail complete

---

## Test Suite 5: Content Filtering and Priority Scoring

### T5.1: Priority scoring accuracy

**Objective:** Verify items ranked by priority formula

**Steps:**
1. Create notes with varying priorities
2. Send `/daily_report`
3. Verify ordering in response

**Expected Results:**
- Items within category sorted by priority score
- Formula applied: (Priority×10) + (Urgency×8) + (Impact×5) - (Overdue×2)
- Overdue items ranked higher than new items (if same priority)
- Critical items always appear before high items
- Correct ordering maintained

**Pass Criteria:**
- Items properly ranked
- Scoring formula working correctly
- Categories properly ordered

---

### T5.2: Filter critical items only

**Objective:** Verify content filtering works

**Steps:**
1. Configure content to include only critical
2. Set include_critical=true, include_high=false, etc.
3. Send `/daily_report`

**Expected Results:**
- Only critical items shown
- Other priorities filtered out
- Report still generates successfully
- Configuration respected

**Pass Criteria:**
- Filters applied correctly
- Only selected priorities shown

---

### T5.3: Empty report handling

**Objective:** Verify graceful handling when no items match filters

**Steps:**
1. Configure filters for a priority level with no items
2. Send `/daily_report`
3. Observe response

**Expected Results:**
- Report generated successfully
- Shows "No items in this priority level"
- Does not error or crash
- Properly formatted with summary

**Pass Criteria:**
- Empty reports handled gracefully
- No errors or crashes
- Message still informative

---

## Test Suite 6: Edge Cases and Error Handling

### E6.1: Joplin API unavailable

**Objective:** Verify graceful degradation when Joplin is down

**Steps:**
1. Stop Joplin instance
2. Send `/daily_report`
3. Observe response

**Expected Results:**
- Report still generates (uses Google Tasks if available)
- Error logged but not sent to user
- Graceful message if no data available
- Bot doesn't crash

**Pass Criteria:**
- Graceful error handling
- Bot remains functional
- Informative user message

---

### E6.2: Google Tasks API unavailable

**Objective:** Verify graceful degradation when Google Tasks is down

**Steps:**
1. Disable or corrupt Google Tasks credentials
2. Send `/daily_report`
3. Observe response

**Expected Results:**
- Report includes only Joplin notes (if available)
- Error logged but handled gracefully
- User not impacted
- Bot remains functional

**Pass Criteria:**
- Graceful fallback to Joplin only
- No crashes or exceptions
- User informed if appropriate

---

### E6.3: User not in whitelist

**Objective:** Verify whitelist enforcement

**Steps:**
1. Use a non-whitelisted Telegram user ID
2. Send `/daily_report` or configuration commands
3. Observe response

**Expected Results:**
- Command rejected with auth error
- No report generated
- No configuration saved
- No database entries created

**Pass Criteria:**
- Unauthorized access prevented
- Proper rejection message shown

---

### E6.4: Invalid database state

**Objective:** Verify recovery from missing or corrupt config

**Steps:**
1. Manually delete user's config from database
2. Try to get report config
3. Send `/daily_report`

**Expected Results:**
- System creates default config
- Report generates with defaults
- No errors or crashes
- User can then configure

**Pass Criteria:**
- Graceful handling of missing config
- Sensible defaults applied
- System recovers without manual intervention

---

### E6.5: Concurrent requests handling

**Objective:** Verify no race conditions with async operations

**Steps:**
1. Send multiple `/daily_report` commands rapidly
2. Rapidly change configuration while report generating
3. Observe behavior

**Expected Results:**
- All requests processed
- No duplicate reports
- No configuration corruption
- Consistent state maintained

**Pass Criteria:**
- No race conditions observed
- Consistent results
- No data corruption

---

## Test Suite 7: Message Formatting and User Experience

### UX7.1: Detailed report format

**Objective:** Verify detailed report formatting

**Steps:**
1. Configure detail_level = 'detailed'
2. Send `/daily_report` with multiple items
3. Examine message format

**Expected Results:**
- Report includes item descriptions
- Multiple sections clearly separated by emojis
- Summary at top with total counts
- Items grouped by priority
- Proper spacing and readability
- No truncation of important info

**Pass Criteria:**
- Format is readable and professional
- All sections clearly visible
- Information complete

---

### UX7.2: Compact report format

**Objective:** Verify compact formatting (if implemented)

**Steps:**
1. Configure detail_level = 'compact'
2. Send `/daily_report`
3. Compare with detailed format

**Expected Results:**
- Report more concise than detailed
- Still includes key information
- Easier to scan
- Less verbose descriptions

**Pass Criteria:**
- Format more compact than detailed
- Still readable and useful

---

### UX7.3: Configuration feedback clarity

**Objective:** Verify user feedback on configuration changes

**Steps:**
1. Execute each configuration command
2. Observe feedback messages

**Expected Results:**
- Clear confirmation of what changed
- Current related settings shown
- Success/failure clearly indicated
- Scheduling status confirmed
- No confusing or contradictory messages

**Pass Criteria:**
- Feedback messages clear and helpful
- User knows what happened
- Status clearly communicated

---

## Test Suite 8: Integration with Other Features

### INT8.1: Interaction with note creation

**Objective:** Verify reports include newly created notes

**Steps:**
1. Send a message to create a Joplin note
2. Wait for note to be created
3. Send `/daily_report`
4. Verify new note appears in report

**Expected Results:**
- New note included in report immediately
- Correct priority assigned
- Proper source indication

**Pass Criteria:**
- New notes appear in reports
- Integration working correctly

---

### INT8.2: Interaction with Google Tasks creation

**Objective:** Verify reports include newly created tasks

**Steps:**
1. Create a task via Google Tasks interface
2. Wait 30 seconds for sync
3. Send `/daily_report`
4. Verify new task appears in report

**Expected Results:**
- New task included in next report
- Correct priority assigned
- Source clearly indicated

**Pass Criteria:**
- New tasks appear in reports
- Integration working correctly

---

### INT8.3: Clarification flows in reports

**Objective:** Verify pending clarifications appear in reports

**Steps:**
1. Create a note with ambiguous info
2. Trigger clarification flow
3. Send `/daily_report`
4. Verify clarification shown in pending section

**Expected Results:**
- Clarification items shown in report
- Clearly marked as pending clarification
- Easy to identify and address

**Pass Criteria:**
- Clarifications properly displayed
- Integration with clarification system working

---

## Manual Testing Checklist

Use this checklist to track testing progress:

### Test Suite 1: On-Demand Reports
- [ ] T1.1: Basic /daily_report command
- [ ] T1.2: Report with only Joplin notes
- [ ] T1.3: Report with Joplin and Google Tasks
- [ ] T1.4: Report respects content filters

### Test Suite 2: Configuration Commands
- [ ] T2.1: Configure report delivery time
- [ ] T2.2: Configure report timezone
- [ ] T2.3: Invalid timezone handling
- [ ] T2.4: Invalid time format handling
- [ ] T2.5: Show report configuration
- [ ] T2.6: Toggle daily reports on
- [ ] T2.7: Toggle daily reports off
- [ ] T2.8: Toggle with various formats
- [ ] T2.9: Report help command

### Test Suite 3: Scheduling and Timezone
- [ ] T3.1: Schedule report for specific time
- [ ] T3.2: Timezone-aware scheduling
- [ ] T3.3: Reschedule existing job
- [ ] T3.4: Bot restart preserves schedules

### Test Suite 4: Database Logging
- [ ] T4.1: Report generation logged
- [ ] T4.2: Configuration changes logged
- [ ] T4.3: Task sync history recorded

### Test Suite 5: Content Filtering
- [ ] T5.1: Priority scoring accuracy
- [ ] T5.2: Filter critical items only
- [ ] T5.3: Empty report handling

### Test Suite 6: Edge Cases
- [ ] E6.1: Joplin API unavailable
- [ ] E6.2: Google Tasks API unavailable
- [ ] E6.3: User not in whitelist
- [ ] E6.4: Invalid database state
- [ ] E6.5: Concurrent requests handling

### Test Suite 7: Message Formatting
- [ ] UX7.1: Detailed report format
- [ ] UX7.2: Compact report format
- [ ] UX7.3: Configuration feedback clarity

### Test Suite 8: Integration
- [ ] INT8.1: Interaction with note creation
- [ ] INT8.2: Interaction with Google Tasks creation
- [ ] INT8.3: Clarification flows in reports

---

## Bug Reporting Template

If issues are found, use this template:

```
## Bug: [Brief Title]

**Test Case:** [Which test found this]
**Severity:** [Critical/High/Medium/Low]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. ...

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Logs/Evidence:**
[Relevant log lines or screenshots]

**Database State:**
[Relevant database queries/results]

**Notes:**
[Any additional context]
```

---

## Performance Baseline

Track performance metrics during testing:

- **Report Generation Time:** [Should be < 5 seconds]
- **Scheduler Job Trigger Accuracy:** [Should be within ±1 minute]
- **Database Query Performance:** [Should be < 500ms for typical queries]
- **Message Delivery Time:** [Should be < 2 seconds]
- **Memory Usage:** [Should remain stable]
- **CPU Usage During Scheduled Jobs:** [Should be minimal]

---

## Sign-Off Criteria

Feature is considered **ready for production** when:

- [ ] All test cases in Test Suites 1-5 pass
- [ ] At least 4 of 5 edge cases (Suite 6) pass
- [ ] All UX tests (Suite 7) pass
- [ ] Integration tests (Suite 8) pass
- [ ] No critical or high severity bugs open
- [ ] Performance metrics within acceptable ranges
- [ ] Documentation complete and reviewed
- [ ] At least 2 hours of real-world usage without issues

---

## Notes for Testers

1. **Test Environment Isolation:** Use a dedicated test user ID to avoid interfering with production data
2. **Database Cleanup:** Keep database clean between test runs; consider backup before/after testing
3. **Log Monitoring:** Keep application logs open during testing for real-time error visibility
4. **Time Awareness:** Some tests require waiting (e.g., scheduling tests); plan test execution accordingly
5. **Timezone Testing:** Consider running tests in different timezones or using timezone manipulation tools
6. **Backup:** Back up database before starting edge case testing in case recovery is needed

---

**Document Version:** 1.0
**Created:** Sprint 6 Development
**Last Updated:** During Integration Phase
**Status:** Ready for Manual Testing
