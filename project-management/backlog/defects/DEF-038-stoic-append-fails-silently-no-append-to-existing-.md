# Defect: DEF-038 - Stoic append fails silently — no content saved

[← Back to Product Backlog](../product-backlog.md)

**Status**: ⭕ To Do
**Priority**: 🟠 High
**Story Points**: 3
**Created**: 2026-04-01
**Updated**: 2026-04-01
**Assigned Sprint**: Backlog

## Description

User completed a morning stoic session on 2026-04-01. The bot detected an existing session (2026-03-31 note) and offered Replace/Append options. User chose "append" but: (1) nothing was appended to the 2026-03-31 note, and (2) no new 2026-04-01 note was created.

This likely occurred at the date boundary (Montreal ~22:00 March 31 = UTC April 1). The DEF-037 fix was deployed mid-session, which may have affected timezone resolution between the start of the session and the append action.

## Steps to Reproduce

1. Have an existing stoic note for 2026-03-31 with a morning section
2. Start `/stoic` morning near midnight Montreal time
3. Bot detects existing morning section, offers Replace/Append
4. Choose `/stoic_append`
5. Check Joplin — nothing was saved

## Expected Behavior

The morning reflection content is appended to the existing note, or a new note is created for the new date.

## Actual Behavior

No content saved anywhere. No error message to the user.

## Possible Root Causes

1. **Deploy mid-session**: DEF-037 fix deployed between duplicate detection and append action. If the bot restarted, the state in SQLite should survive, but the state's `existing_body` may now be stale if Joplin note was modified.

2. **Date boundary mismatch**: Session started when Montreal date was March 31, but by the time append was triggered, Montreal date crossed to April 1. The `date_str` used to find the existing note might no longer match.

3. **State corruption**: The `pending_action`, `existing_note_id`, or `new_section_content` keys in state may have been cleared or overwritten between the duplicate prompt and the append command.

4. **Silent failure in `_apply_append_action`**: The `update_note` Joplin API call may have failed, and while the error handler sends a message, the user might not have noticed it.

5. **`_stoic_append` handler returns silently on failure**: At `stoic.py:1174`, if `_apply_append_action` returns False, the handler does nothing — no cleanup, no guidance to the user.

## Technical References

- `src/handlers/stoic.py:685-722` — `_apply_append_action()`
- `src/handlers/stoic.py:1162-1183` — `_stoic_append()` handler
- `src/handlers/stoic.py:795-806` — duplicate detection and state setup
- `src/handlers/stoic.py:739` — `get_current_date_str()` for date resolution

## Testing

- [ ] Add logging to `_apply_append_action` entry/exit
- [ ] Test append across date boundary (start session March 31 ~23:55, append April 1 ~00:05)
- [ ] Verify state persistence across bot restarts
- [ ] Manual test: complete stoic session, trigger duplicate, choose append

## Acceptance Verification

- [ ] Append action saves content to the note
- [ ] User receives confirmation or clear error message
- [ ] Works correctly across date boundaries

## History

- 2026-04-01 - Created
