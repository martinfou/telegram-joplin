---
template_version: 1.1.0
last_updated: 2026-04-06
compatible_with: [feature-request, sprint-planning, product-backlog]
requires: [markdown-support]
---

# User Story: US-063 - Stoic Session: Create Google Tasks from Top 3 Priorities

[← Back to Product Backlog](../product-backlog.md)

**Status**: ⏳ In Progress  
**Priority**: 🟠 High  
**Story Points**: 5  
**Created**: 2026-03-24  
**Updated**: 2026-04-06  
**Assigned Sprint**: Sprint 21  

## Description

After a Stoic reflection session, offer to turn the user’s **top 3 priorities** (or equivalent ranked items from the session) into **Google Tasks**, with clear titles and optional links back to the Stoic note.

## User Story

As a user who finishes a Stoic session,  
I want the bot to offer creating Google Tasks from my top priorities,  
so that my reflections translate into actionable items without manual re-entry.

## Acceptance Criteria

- [ ] After `/stoic_done` (or equivalent completion flow), the bot can detect or ask for the top 3 priorities from the session content.
- [ ] User can confirm, edit task titles, choose task list / project, or cancel.
- [ ] Created tasks respect existing Google Tasks integration (auth, duplicate policies).
- [ ] Errors are surfaced clearly; partial success is reported if some tasks fail.

## Notes

- Renumbered from duplicate **US-062** on 2026-04-06 so **US-062** remains the web interface (Laravel + Vue.js) story.

## History

- 2026-03-24 - Captured in product backlog (was listed as US-062).
- 2026-04-06 - Assigned **US-063**; story file created; backlog link updated.
- 2026-04-06 - **Sprint 21** committed; status ⏳ In Progress.
