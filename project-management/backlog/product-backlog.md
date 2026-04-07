---
template_version: 1.1.0
last_updated: 2026-04-06
compatible_with: [feature-request, defect-fix, sprint-planning]
requires: [markdown-support]
---

# Product Backlog

This is the main product backlog tracking all feature requests and defect fixes for the Telegram-Joplin Bot project.

**Last Updated**: 2026-04-06 (Sprint 17 ✅, Sprint 18 ✅, Sprint 19 ✅, Sprint 20 ✅)

## Project Overview

**Project Name**: Intelligent Telegram-Joplin Bot
**Current Sprint**: Sprint 21 (⏳ In Progress — [sprint-21-next.md](../sprints/sprint-21-next.md))
**Status**: Sprint 21 — **US-063** done (Stoic → Google Tasks); **US-057** in progress (health: import + goals; weekly Joplin / wizard backlog). **US-062** web UI not in this sprint.
**Timeline**: Sprint 10–20 ✅; Sprint 9 (US-016) ~55%
**Quality**: Production Ready ✅

## Executive Summary

The Telegram-Joplin Bot is a productivity tool that bridges note-taking (Joplin) with task management (Google Tasks). Users can send messages to the bot which intelligently:
- Creates structured notes in Joplin with automatic folder/tag organization
- Extracts action items and creates Google Tasks automatically
- Maintains conversation history and logging for audit trails
- Provides seamless integration with AI/LLM for intelligent processing
- (Sprint 5) Displays tags applied by AI in success messages
- (Sprint 6) Delivers daily priority reports aggregating Joplin + Google Tasks
- (Sprint 7) Provides GTD expert persona for brain dump sessions
- (Sprint 7b) Provides stoic journaling with morning/evening guided reflection
- (Sprint 8) Generates weekly productivity reviews with trends
- (Sprint 9) Reorganizes Joplin with PARA methodology
- (Sprint 10) Greeting & command help, quick note search (/find, /search), intelligent content routing (note/task/both), monthly report, Joplin 24/7
- (Sprint 11) Photo OCR, read-later queue (/readlater, /reading), Jungian dream analysis (/dream), habit tracking (/habits), weekly planning (/plan)

**Sprints Completed**: Through Sprint 20 (rolling); Sprint 9 (US-016) still partial
**Current Sprint**: Sprint 21 — [sprint-21-next.md](../sprints/sprint-21-next.md) (US-063 + US-057 stretch; US-062 deferred)
**Major Milestones**: Foundation ✅ → Components ✅ → Enhancements ✅ → Google Tasks ✅ → Tag Display ✅ → Reports ✅ → GTD Expert ✅ → Stoic Journal ✅ → Weekly Reports ✅ → Database Org (Sprint 9 ~55%) → Core UX (Sprint 10) ✅ → New Modalities (Sprint 11) ✅ → GTD cockpit & project intelligence (Sprint 20) ✅

## User Stories

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| [US-062](user-stories/US-062-web-interface-for-telegram-joplin-app-laravel-vuej.md) | Web interface for Telegram-Joplin app (Laravel + V | 🟠 High | 13 | ⭕ | - | 2026-03-29 | 2026-03-29 |
| [US-063](user-stories/US-063-stoic-session-create-google-tasks-from-top-3-prior.md) | Stoic Session: Create Google Tasks from Top 3 Prio | 🟠 High | 5 | ✅ | Sprint 21 | 2026-03-24 | 2026-04-06 |
| [US-064](user-stories/US-064-use-uv-as-sole-python-package-manager.md) | Use uv as sole Python package manager | 🟡 Medium | 5 | ✅ | - | 2026-04-06 | 2026-04-06 |
| [US-001](user-stories/US-001-git-commit-template.md) | Add Git Commit Message Template | 🟠 High | 5 | ✅ | Sprint 1 | 2026-01-01 | 2026-01-01 |
| [US-002](user-stories/US-002-mermaid-workflow-diagrams.md) | Add Mermaid Workflow Diagrams for Backlog Management | 🟠 High | 5 | ✅ | Sprint 1 | 2026-01-01 | 2026-01-01 |
| [US-003](user-stories/US-003-update-quick-start-with-setup-script.md) | Update Quick Start Guide to Use Setup Script | 🟠 High | 3 | ✅ | Sprint 3 | 2026-01-01 | 2025-01-27 |
| [US-004](user-stories/US-004-telegram-bot-interface.md) | Telegram Bot Interface | 🟠 High | 8 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [US-005](user-stories/US-005-joplin-rest-api-client.md) | Joplin REST API Client | 🟠 High | 5 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [US-006](user-stories/US-006-llm-integration-for-note-generation.md) | LLM Integration for Note Generation | 🟠 High | 8 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [US-007](user-stories/US-007-conversation-state-management.md) | Conversation State Management | 🟠 High | 3 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [US-008](user-stories/US-008-security-and-error-handling.md) | Security and Error Handling | 🟠 High | 3 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [US-009](user-stories/US-009-initial-setup-and-configuration.md) | Initial Setup and Configuration | 🟠 High | 5 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [US-010](user-stories/US-010-database-logging-telegram-llm-decisions.md) | Database for Logging Telegram Conversations and LLM Decisions | 🟡 Medium | 8 | ✅ | Sprint 3 | 2025-01-27 | 2025-01-24 |
| [US-011](user-stories/US-011-comprehensive-project-documentation.md) | Comprehensive Project Documentation for Multiple Audiences | 🟡 Medium | 13 | ✅ | Sprint 3 | 2025-01-27 | 2025-01-27 |
| [US-012](user-stories/US-012-google-tasks-integration.md) | Google Tasks Integration for Task Logging | 🟡 Medium | 8 | ✅ | Sprint 4 | 2025-01-27 | 2025-01-23 |
| [US-013](user-stories/US-013-display-tags-in-ai-response.md) | Display Tags in AI Response to Telegram | 🟡 Medium | 5 | ✅ | Sprint 5 | 2025-01-23 | 2025-01-24 |
| [US-014](user-stories/US-014-daily-priority-report.md) | Daily Priority Report for Review and Action Items | 🟠 High | 8 | ✅ | Sprint 6 | 2025-01-23 | 2026-01-24 |
| [US-015](user-stories/US-015-weekly-review-report.md) | Weekly Review and Report | 🟠 High | 13 | ✅ | Sprint 8 | 2025-01-23 | 2026-03-03 |
| [US-016](user-stories/US-016-joplin-database-reorganization.md) | Joplin Database Reorganization, Tag Management, and Entry Enrichment | 🟢 Low | 21 | ⭕ | Backlog | 2025-01-23 | 2026-03-08 |
| [US-017](user-stories/US-017-gtd-expert-persona.md) | GTD Expert Persona for 15-Minute Brain Dumping | 🟠 High | 8 | ✅ | Sprint 7 | 2026-01-24 | 2026-01-24 |
| [US-018](user-stories/US-018-docker-compose-setup.md) | Docker Compose Setup for Bot and Joplin Server | 🟢 Low | 8 | ⭕ | Backlog | 2026-01-24 | 2026-03-08 |
| [US-019](user-stories/US-019-stoic-journal.md) | Stoic Journal with Morning/Evening Guided Reflection | 🟠 High | 5 | ✅ | Sprint 7 | 2026-02-15 | 2026-03-01 |
| [US-020](user-stories/US-020-marketing-readme.md) | Marketing-Focused README with GTD + Second Brain Pitch | 🟠 High | 3 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [US-021](user-stories/US-021-remove-ci-docker-build-step.md) | Remove Redundant Docker Build Step from CI | 🟡 Medium | 1 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [US-022](user-stories/US-022-enforce-single-machine-limit.md) | Enforce Single Machine Limit on Fly.io | 🟠 High | 1 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [US-023](user-stories/US-023-intelligent-content-routing.md) | Intelligent Content Routing (Notes vs Tasks) | 🟠 High | 8 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [US-024](user-stories/US-024-greeting-and-command-help.md) | Greeting Response and Command Discovery | 🟡 Medium | 3 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [US-025](user-stories/US-025-jungian-dream-analysis.md) | Jungian Dream Analysis with Image Generation | 🟡 Medium | 8 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [US-026](user-stories/US-026-semantic-search-qa.md) | Semantic Search and Q&A Over Notes | 🟠 High | 13 | ✅ | Sprint 12 | 2026-03-05 | 2026-03-06 |
| [US-027](user-stories/US-027-weekly-planning-session.md) | Weekly Planning Session | 🟡 Medium | 8 | ✅ | Sprint 12 | 2026-03-05 | 2026-03-05 |
| [US-028](user-stories/US-028-read-later-queue.md) | Read Later Queue | 🟡 Medium | 5 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [US-029](user-stories/US-029-quick-note-search.md) | Quick Note Search | 🟡 Medium | 3 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [US-030](user-stories/US-030-photo-ocr-capture.md) | Photo/Screenshot OCR Capture | 🟡 Medium | 5 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [US-031](user-stories/US-031-monthly-review-report.md) | Monthly Review Report | 🟢 Low | 5 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [US-032](user-stories/US-032-habit-tracking.md) | Habit Check-ins and Tracking | 🟢 Low | 5 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [US-033](user-stories/US-033-flashcard.md) | Flashcard Practice from Notes | 🟠 High | 8 | ✅ | Sprint 14 | 2026-03-05 | 2026-03-06 |
| [US-034](user-stories/US-034-joplin-google-tasks-project-sync.md) | Joplin Projects ↔ Google Tasks Sync (Project = Task, Tasks = Subtasks) | 🟠 High | 13 | ✅ | Sprint 16 | 2026-03-05 | 2026-03-09 |
| [US-035](user-stories/US-035-world-class-brain-dump.md) | World-Class Brain Dump Experience (modes, time awareness, recovery, personalization) | 🟠 High | 13 | ✅ | Sprint 17 | 2026-03-05 | 2026-03-08 |
| [US-036](user-stories/US-036-documentation-code-consistency-review.md) | Documentation-Code Consistency Review (pre-sprint planning, hybrid, report) | 🟠 High | 8 | ✅ | Sprint 13 | 2026-03-05 | 2026-03-05 |
| [US-037](user-stories/US-037-reports-great-on-telegram.md) | Reports Look Great on Telegram | 🟡 Medium | 5 | ✅ | Backlog | 2026-03-05 | 2026-03-06 |
| [US-038](user-stories/US-038-ai-identity-user-profile-chat-history.md) | AI Identity, User Profile, and Chat History | 🟡 Medium | 8 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [US-039](user-stories/US-039-star-on-task-as-high-priority.md) | Treat Star on Task as High Priority | 🟡 Medium | 3 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |
| [US-040](user-stories/US-040-check-existing-task-note-update-append.md) | Check if Task or Note Exists, Offer Update or Append | 🟡 Medium | 8 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [US-041](user-stories/US-041-project-management-commit-style-and-doc-sync.md) | Project Management: Commit Style and Document Sync Sections | 🟡 Medium | 5 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [US-042](user-stories/US-042-stoic-what-i-learned-today.md) | Stoic Journal: "What I Learned Today" Section | 🟡 Medium | 4 | ✅ | Sprint 18 | 2026-03-06 | 2026-03-08 |
| [US-043](user-stories/US-043-report-generation-speed-and-ui-updates.md) | Report Generation: Speed Up with Async and Chat UI Updates | 🟡 Medium | 5 | ✅ | Sprint 18 | 2026-03-06 | 2026-03-08 |
| [US-044](user-stories/US-044-project-new-command.md) | /project_new Command to Create Project with Default Folders | 🟡 Medium | 5 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |
| [US-045](user-stories/US-045-photo-folder-quick-reply.md) | Photo OCR: Folder Quick-Reply for NEED_INFO | 🟡 Medium | 3 | ✅ | Sprint 17 | 2026-03-06 | 2026-03-08 |
| [US-046](user-stories/US-046-photo-ocr-unprocessable-test.md) | Photo OCR: Test for OCRUnprocessableImageError | 🟡 Medium | 1 | ✅ | Sprint 17 | 2026-03-06 | 2026-03-08 |
| [US-047](user-stories/US-047-photo-ocr-retry-transient.md) | Photo OCR: Retry on Transient Failures | 🟡 Medium | 2 | ✅ | Sprint 17 | 2026-03-06 | 2026-03-08 |
| [US-048](user-stories/US-048-photo-albums.md) | Photo OCR: Photo Albums Support | 🟢 Low | 5 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [US-049](user-stories/US-049-photo-ocr-cost-logging.md) | Photo OCR: Cost Logging | 🟢 Low | 2 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [US-050](user-stories/US-050-photo-send-as-file-hint.md) | Photo OCR: "Send as File" Hint in Help | 🟢 Low | 1 | ✅ | Sprint 18 | 2026-03-06 | 2026-03-08 |
| [US-051](user-stories/US-051-bookmark-command.md) | /bookmark Command to Save URLs to Joplin | 🟡 Medium | 5 | ✅ | Sprint 17 | 2026-03-08 | 2026-03-08 |
| [US-052](user-stories/US-052-world-class-stoic-journaling-experience.md) | World-Class Stoic Journaling Experience | 🟠 High | 13 | ✅ | Sprint 18 | 2026-03-08 | 2026-03-08 |
| [US-053](user-stories/US-053-stoic-quick-reply-for-each-answer.md) | Stoic Journal Quick Reply for Each Answer | 🟡 Medium | 3 | ✅ | Sprint 19 | 2026-03-09 | 2026-03-10 |
| [US-054](user-stories/US-054-note-creation-show-full-path-and-auto-sync.md) | Note Creation: Show Full Path and Auto-Sync | 🟡 Medium | 2 | ✅ | Sprint 19 | 2026-03-09 | 2026-03-10 |
| [US-055](user-stories/US-055-google-tasks-duplicate-check-before-add.md) | Google Tasks: Duplicate Check Before Add, Offer Edit/Priority/Cancel | 🟡 Medium | 5 | ✅ | Sprint 20 | 2026-03-09 | 2026-03-10 |
| [US-056](user-stories/US-056-grocery-shopping-price-and-store-search.md) | Grocery/Shopping: Find Stores Nearby and Compare Prices (Local + Online) | 🟡 Medium | 8 | ⭕ | Backlog | 2026-03-09 | 2026-03-09 |
| [US-057](user-stories/US-057-parse-health-data-from-garmin-fatsecret-and-arbole.md) | Parse health data from Garmin, FatSecret, and Arbo | 🟡 Medium | 8 | ⏳ | Sprint 21 | 2026-03-10 | 2026-04-06 |
| [US-058](user-stories/US-058-bot-understands-natural-conversational-intent-from.md) | Bot understands natural conversational intent from user messages | 🟡 Medium | 5 | ✅ | Sprint 20 | 2026-03-10 | 2026-03-28 |
| [US-059](user-stories/US-059-us-059-world-class-gtd-dashboard-tasks_status-as-p.md) | US-059 - World-Class GTD Dashboard: /tasks_status Cockpit | 🟠 High | 5 | ✅ | Sprint 20 | 2026-03-10 | 2026-03-10 |
| [US-060](user-stories/US-060-us-060-world-class-project-report-full-portfolio-v.md) | US-060 - World-Class Project Report: Full Portfolio View | 🟠 High | 8 | ✅ | Sprint 20 | 2026-03-10 | 2026-03-19 |
| [US-061](user-stories/US-061-stoic-llm-image-after-reflection.md) | LLM-generated image after Stoic reflection | 🟠 High | 5 | ✅ | Sprint 20 | 2026-03-17 | 2026-03-24 |

## Defects

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| [DEF-038](defects/DEF-038-stoic-append-fails-silently-no-append-to-existing-.md) | Stoic append fails silently — no append to existin | 🟠 High | 3 | ✅ | - | 2026-04-01 | 2026-04-01 |
| [DEF-037](defects/DEF-037-stoic-morning-reflection-still-shows-utc-time-1144.md) | Stoic morning reflection still shows UTC time (11: | 🟠 High | 3 | ✅ | - | 2026-03-31 | 2026-03-31 |
| [DEF-036](defects/DEF-036-task-duplicate-detection-too-strict-semantic-thres.md) | Task duplicate detection too strict — semantic thr | 🟠 High | 3 | ✅ | - | 2026-03-31 | 2026-03-31 |
| [DEF-035](defects/DEF-035-stoic-journal-morningevening-prompts-use-wrong-tim.md) | Bot uses UTC instead of configurable user timezone | 🟠 High | 5 | ✅ | - | 2026-03-29 | 2026-03-30 |
| [DEF-034](defects/DEF-034-stoic-morning-saved-to-areas-instead-of-numbered.md) | /stoic morning saved to Areas instead of numbered | 🟠 High | 2 | ✅ | - | 2026-03-17 | 2026-03-24 |
| [DEF-033](defects/DEF-033-joplin-agent-fails-to-take-screenshot-of-youtube-v.md) | Joplin agent fails to take screenshot of YouTube v | 🟠 High | 3 | ✅ | Sprint 19 | 2026-03-10 | 2026-03-10 |
| [DEF-032](defects/DEF-032-joplin-did-not-process-voice-message-transcription.md) | Joplin did not process voice message transcription | 🟠 High | 3 | ✅ | Sprint 19 | 2026-03-10 | 2026-03-10 |
| [DEF-001](defects/DEF-001-google-tasks-sync-no-token.md) | Google Tasks Sync Fails: No Google token found for user | 🟠 High | 2 | ✅ | Backlog | 2026-03-01 | 2026-03-01 |
| [DEF-002](defects/DEF-002-github-actions-build-failure.md) | GitHub Actions Build Failure | 🔴 Critical | 3 | ✅ | Backlog | 2026-03-01 | 2026-03-03 |
| [DEF-003](defects/DEF-003-scheduler-not-working.md) | Scheduler Not Working — App Down | 🔴 Critical | 5 | ✅ | Backlog | 2026-03-01 | 2026-03-03 |
| [DEF-004](defects/DEF-004-flyctl-deploy-no-access-token.md) | Fly.io Deploy Fails: No Access Token Available | 🔴 Critical | 1 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [DEF-005](defects/DEF-005-stoic-journal-timezone-and-data-loss.md) | Stoic Journal: Timezone Mismatch & Data Loss on Update | 🔴 Critical | 5 | ✅ | Backlog | 2026-03-03 | 2026-03-05 |
| [DEF-006](defects/DEF-006-stoic-session-stuck-loop-no-cancel.md) | Stoic Session Stuck in Loop with No Cancel | 🟠 High | 3 | ✅ | Backlog | 2026-03-04 | 2026-03-05 |
| [DEF-007](defects/DEF-007-url-screenshot-no-content-validation.md) | URL Screenshots: No Validation That Content Matches URL | 🟠 High | 5 | ✅ | Sprint 13 | 2026-03-04 | 2026-03-05 |
| [DEF-008](defects/DEF-008-stoic-evening-deletes-morning.md) | Stoic Evening Deletes Morning Reflection | 🔴 Critical | 5 | ✅ | Backlog | 2026-03-04 | 2026-03-05 |
| [DEF-009](defects/DEF-009-stoic-questions-template-mismatch.md) | Stoic Journal: Questions Do Not Match Template | 🟠 High | 3 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-010](defects/DEF-010-greeting-parse-entities-error.md) | Greeting Response: "Something Went Wrong" (Parse Entities) | 🟠 High | 2 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-011](defects/DEF-011-content-decision-validation-error.md) | ContentDecision Validation + Greeting Shows Menu | 🟠 High | 1 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-012](defects/DEF-012-mypy-module-resolution.md) | Mypy Module Resolution Error | 🟡 Medium | 0.5 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-013](defects/DEF-013-double-check-mark-success.md) | Double Check Mark on Task/Note Creation Success | 🟢 Low | 0.5 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-014](defects/DEF-014-dream-parse-entities-error.md) | /dream Parse Entities Error (BadRequest) | 🟠 High | 2 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-015](defects/DEF-015-mypy-type-errors.md) | Mypy Type Errors (60 errors in 23 files) | 🟡 Medium | 5 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-016](defects/DEF-016-dream-parse-error-user-report.md) | /dream Parse Error: User Receives Nothing | 🟠 High | 2 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [DEF-017](defects/DEF-017-dream-command-crash.md) | /dream Command Crashes Agent on Invocation | 🟠 High | 1 | ✅ | Sprint 14 | 2026-03-05 | 2026-03-06 |
| [DEF-018](defects/DEF-018-weekly-report-incorrect-numbers.md) | Weekly Report Shows Incorrect Numbers (0 Notes/Tasks) | 🟠 High | 3 | ✅ | Backlog | 2026-03-05 | 2026-03-06 |
| [DEF-019](defects/DEF-019-dream-message-too-long.md) | Dream Analysis: "Message is too long" Error | 🟠 High | 2 | ✅ | Backlog | 2026-03-06 | 2026-03-06 |
| [DEF-020](defects/DEF-020-daily-report-column-overlap.md) | Daily Report: Column Overlap, SOURCE Column Not Required | 🟡 Medium | 1 | ✅ | Backlog | 2026-03-06 | 2026-03-06 |
| [DEF-021](defects/DEF-021-weekly-report-ugly-formatting.md) | Weekly Report: Ugly Formatting, Needs Pretty Tables | 🟡 Medium | 2 | ✅ | Backlog | 2026-03-06 | 2026-03-06 |
| [DEF-022](defects/DEF-022-find-command-flyio-error.md) | /find Command Error in Fly.io Logs | 🟠 High | 2 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |
| [DEF-023](defects/DEF-023-ask-command-crash.md) | /ask Command Crashes on Certain Prompts | 🟠 High | 2 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |
| [DEF-024](defects/DEF-024-photo-image-not-displaying.md) | Photo OCR: Image Not Displaying in Joplin Note | 🟠 High | 2 | ✅ | Backlog | 2026-03-07 | 2026-03-07 |
| [DEF-025](defects/DEF-025-recipe-pasted-text-shows-screenshot-skipped.md) | Recipe Pasted as Text Shows "Screenshot skipped" Incorrectly | 🟡 Medium | 2 | ✅ | Backlog | 2026-03-09 | 2026-03-09 |
| [DEF-026](defects/DEF-026-braindump-and-image-ocr-cannot-save-to-joplin.md) | Braindump and Image OCR Cannot Save to Joplin | 🟠 High | 1 | ✅ | Backlog | 2026-03-09 | 2026-03-09 |
| [DEF-027](defects/DEF-027-braindump-google-tasks-token-expired.md) | Braindump: Google Tasks Creation Fails with token_expired | 🟠 High | 2 | ✅ | Backlog | 2026-03-09 | 2026-03-09 |
| [DEF-028](defects/DEF-028-tasks-status-shows-times-not-in-user-timezone.md) | Tasks Status Shows Times Not in User Timezone | 🟡 Medium | 2 | ✅ | Sprint 19 | 2026-03-09 | 2026-03-10 |
| [DEF-029](defects/DEF-029-task-creation-project-list-incomplete-missing-projects.md) | Task Creation Project List Incomplete — Missing Projects | 🟡 Medium | 3 | ✅ | Sprint 19 | 2026-03-09 | 2026-03-10 |
| [DEF-030](defects/DEF-030-stoic-note-timestamp-utc-instead-of-montreal-time.md) | Stoic Note Timestamp Shows UTC Instead of Montreal Time | 🟡 Medium | 2 | ✅ | Sprint 19 | 2026-03-09 | 2026-03-10 |
| [DEF-031](defects/DEF-031-note-creation-should-show-full-path-and-trigger-sync.md) | Note Creation Should Show Full Path and Trigger Sync | 🟡 Medium | 2 | ✅ | Sprint 19 | 2026-03-09 | 2026-03-10 |

---

## Technical Debt

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|--------|

## Status Values

- ⭕ **Not Started**: Item not yet started
- ⏳ **In Progress**: Item currently being worked on
- ✅ **Completed**: Item finished and verified

## Priority Levels

- 🔴 **Critical**: Blocks core functionality, must be fixed/implemented immediately
- 🟠 **High**: Important feature/defect, should be addressed soon
- 🟡 **Medium**: Nice to have, can wait
- 🟢 **Low**: Future consideration, low priority

## Column Definitions

- **ID**: Unique identifier (US-XXX for user stories, DEF-XXX for defects)
  - Link to detailed item: markdown link to `user-stories/US-001-your-story-slug.md` (use the real filename for that ID)
- **Title**: Short, descriptive title (50 characters or less recommended)
- **Priority**: Visual priority indicator (🔴 🟠 🟡 🟢)
- **Points**: Story points (Fibonacci: 1, 2, 3, 5, 8, 13)
- **Status**: Current status (⭕ ⏳ ✅)
- **Sprint**: Assigned sprint number or "-" if not assigned
- **Created**: Date when item was created (YYYY-MM-DD)
- **Updated**: Date when item was last updated (YYYY-MM-DD)

## Sprint & Backlog Planning

**Current Planning Document**: [Sprint & Backlog Planning](../docs/sprint-and-backlog-planning.md) | [Sprint 15–18 Planning](../docs/sprint-15-18-planning.md)

**Sprint Pipeline**:
| Sprint | Duration | Feature(s) | Points | Status |
|--------|----------|-----------|--------|--------|
| **Sprint 5** | Jan 27-31 | US-013 (Tag Display) | 5 | ✅ Complete |
| **Sprint 6** | Feb 3-16 | US-014 (Daily Reports) | 8 | ✅ Complete |
| **Sprint 7** | Jan 24-31 (Accelerated) | US-017 (GTD Expert), US-019 (Stoic Journal) | 13 | ✅ Complete |
| **Sprint 8** | Feb 24-Mar 9 | US-015 (Weekly Reports) | 13 | ✅ Complete |
| **Sprint 9** | Mar 10-31 | US-016 (DB Reorganization) | 21 | ⏳ ~55% Complete |
| **Sprint 10** | Mar 10-23 | Core UX + Joplin 24/7 (US-024, US-029, US-023, US-031) | 20 | ✅ Complete |
| **Sprint 11** | Mar 24-Apr 6 | US-030, US-028, US-025, US-032, US-027 (New Modalities) | 31 | ✅ Complete |
| **Sprint 12** | Apr 7-20 | US-026 (Semantic Search), US-027 (Weekly Planning) | 21 | ✅ Complete |
| **Sprint 13** | Apr 21-May 4 | DEF-007 (URL validation), US-036 (Doc-code review) | 13 | ✅ Complete |
| **Sprint 14** | May 5-18 | DEF-017 (Dream fix), US-033 (Flashcard) | 9 | ✅ Complete |
| **Sprint 15** | May 19-Jun 1 | DEF-022, DEF-023, US-044 (/project_new), US-039 (Star) | 12 | ✅ Complete |
| **Sprint 16** | Mar 10-23 | US-034 (Project Sync) | 13 | ✅ Complete |
| **Sprint 17** | Mar 24-Apr 6 | US-035 (Brain Dump), US-045/046/047 (Photo OCR), US-051 (/bookmark) | 24 | ✅ Complete |
| **Sprint 18** | Mar 10-23 | US-052 (World-Class Stoic), US-042 (Learnings), US-050 (Photo hint) + US-043 stretch | 23 | ✅ Complete |
| **Sprint 19** | Mar 10-23 | DEF-028–033, US-053 (Stoic quick replies), US-054 (full path + sync) | 19 | ✅ Complete |
| **Sprint 20** | Mar 24-Apr 6 | US-059, US-060, US-055, US-058, US-061 (+ stretch intent) | 25+ | ✅ Complete |
| **Sprint 21** | Apr 7-Apr 20 | US-063 (committed), US-057 stretch ([sprint-21-next.md](../sprints/sprint-21-next.md)) | 5+8 | ⏳ In Progress |

**Remaining Backlog** (high level): US-016, US-018, US-038, US-040, US-041, US-048, US-049, US-056, US-062, and other open rows (US-063 / US-057 are active in Sprint 21)
**Projected Completion**: TBD — CI/CD operational, new features added to backlog

## Notes

- User story details: See `user-stories/US-XXX-*.md` files
- Defect details: See `defects/DEF-XXX-*.md` files
- Sprint assignments: See `../sprints/sprint-XX-*.md` files
- Sprint & Backlog Planning: See `../docs/sprint-and-backlog-planning.md`
- Historical velocity: ~14 points/week average

## Backlog Statistics

**Total Items**: 50 Features + 20 Bugs = 70 items

**Features by Status**:
- ⭕ Not Started: 14 (US-016, US-018, US-035, US-038, US-040, US-041, US-042, US-043, US-045, US-046, US-047, US-048, US-049, US-050)
- ⏳ In Progress: 0
- ✅ Completed: 30 (US-001–US-015, US-017, US-019–US-024, US-025, US-027–US-032, US-034)

**Bugs by Status**:
- ⏳ In Progress: 0
- ⭕ Not Started: 0
- ✅ Completed: 16 (DEF-001–DEF-006, DEF-008–DEF-016, DEF-018–DEF-021)

**By Priority (all items)**:
- 🔴 Critical: 5 (DEF-002, DEF-003, DEF-004, DEF-005, DEF-008 resolved)
- 🟠 High: 13
- 🟡 Medium: 15
- 🟢 Low: 3

**Feature Story Points**: 260
  - Completed: 240 points (US-001–US-015, US-017, US-019–US-025, US-027–US-034, US-036, US-039, US-044) — 92%
  - In Progress: 0 points
  - Not Started: 82 points (US-016, US-018, US-035, US-038, US-040, US-041, US-042, US-043, US-045–US-050)

**Bug Story Points**: 48
  - Completed: 48 points (DEF-001–DEF-006, DEF-008–DEF-017, DEF-018–DEF-019, DEF-022, DEF-023)
  - In Progress: 0 points
  - Not Started: 0 points

**Overall Completion Rate**: 92% features completed (240/248 points)
**Current**: 92% (240/248 points) ✅
**Full Completion Target**: TBD — US-016, US-018, US-035, US-038, US-040, US-041, US-042, US-043 remaining

---

## Sprint Summary

### All Sprints

| Sprint | Duration | Goal | Points | Status | Velocity |
|--------|----------|------|--------|--------|----------|
| [Sprint 1](../sprints/sprint-01-foundation-templates.md) | Jan 1-10 | Foundation Templates | 5 | ✅ | 5 pts |
| [Sprint 2](../sprints/sprint-02-foundation-components.md) | Jan 10-20 | Foundation Components | 26 | ✅ | 26 pts |
| [Sprint 3](../sprints/sprint-03-foundation-enhancements.md) | Jan 20-27 | Foundation Enhancements | 35 | ✅ | 35 pts |
| [Sprint 4](../sprints/sprint-04-google-tasks-integration.md) | Jan 23-24 | Google Tasks Integration | 8 | ✅ | 8 pts |
| [Sprint 5](../sprints/sprint-05-user-engagement-features.md) | Jan 27-31 | Display Tags (US-013) | 5 | ✅ | 5 pts |
| [Sprint 6](../sprints/sprint-06-daily-priority-reports.md) | Feb 3-16 | Daily Reports (US-014) | 8 | ✅ | 8 pts |
| [Sprint 7](../sprints/sprint-07-gtd-expert-persona.md) | Jan 24-31 | GTD Expert (US-017) + Stoic Journal (US-019) | 13 | ✅ | 13 pts |
| Sprint 8 | Feb 24-Mar 9 | Weekly Reports (US-015) | 13 | ✅ | 13 pts |
| Sprint 9 | Mar 10-31 | Database Reorganization (US-016) | 21 | ⏳ ~55% | — |
| [Sprint 10](../sprints/sprint-10-core-ux.md) | Mar 10-23 | Core UX + Joplin 24/7 (US-024, US-029, US-023, US-031) | 20 | ✅ Complete | 20 pts |
| [Sprint 11](../sprints/sprint-11-new-modalities.md) | Mar 24-Apr 6 | New Modalities (US-030, US-028, US-025, US-032, US-027) | 31 | ✅ Complete | 31 pts |
| [Sprint 12](../sprints/sprint-12-advanced-intelligence.md) | Apr 7-20 | Advanced Intelligence (US-026) | 13 | ✅ Complete | 13 pts |
| [Sprint 13](../sprints/sprint-13-quality-and-validation.md) | Apr 21-May 4 | Quality and Validation (DEF-007, US-036) | 13 | ✅ Complete | 13 pts |
| [Sprint 14](../sprints/sprint-14-flashcard-and-dream-fix.md) | May 5-18 | Flashcard & Dream Fix (DEF-017, US-033) | 9 | ✅ Complete | 9 pts |
| [Sprint 15](../sprints/sprint-15-stability-and-project-foundation.md) | May 19-Jun 1 | Stability & Project Foundation (DEF-022, DEF-023, US-044, US-039) | 12 | ✅ Complete | 12 pts |
| [Sprint 16](../sprints/sprint-16-project-sync.md) | Mar 10-23 | Project Sync (US-034) | 13 | ✅ Complete | 13 pts |
| **TOTAL** | | | **295 pts** | **198 Complete, 97 Planned** | **14 avg** |

**Completion Status**: 83% Complete (211/248 points)
  - Sprint 10 Complete: US-023, US-024, US-029, US-031, Joplin 24/7 ✅
  - Sprint 11 Complete: US-025, US-027, US-028, US-030, US-032 ✅
  - Sprint 12 Complete: US-026 (Semantic Search), US-027 ✅
  - Sprint 9 (Mar 10–31): US-016 ~55% complete
  - Sprint 13: DEF-007, US-036 ✅ complete
  - Sprint 14: DEF-017, US-033 ✅ complete
  - Sprint 15: DEF-022, DEF-023, US-044, US-039 ✅ complete
  - Sprint 16: US-034 (Project Sync) ✅ complete
  - Backlog: US-018 ~30%, US-035, US-038, US-040, US-041, US-042, US-043

## Tips for Maintaining the Backlog

1. **Keep it Updated**: Update status and dates when items change
2. **Sort by Priority**: Keep Critical items at top of each section
3. **Link to Details**: Always link IDs to detailed markdown files
4. **Regular Review**: Review and refine backlog regularly (weekly/bi-weekly)
5. **Update Dates**: Keep "Created" and "Updated" dates current
6. **Clear Titles**: Use descriptive, concise titles (update if needed as understanding evolves)
7. **Track Velocity**: Monitor sprint velocity for realistic planning
8. **Review Dependencies**: Ensure feature dependencies are satisfied before sprint assignment

## Example Table Entry

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| US-099 (example) | User Authentication (example row — not a real backlog ID) | 🟠 High | 13 | ⏳ | Sprint 5 | 2024-01-10 | 2024-01-15 |

This entry indicates:
- Feature Request #42 about User Authentication
- High priority
- Estimated at 13 story points
- Currently in progress
- Assigned to Sprint 5
- Created on January 10, 2024
- Last updated on January 15, 2024
- Clicking US-042 links to detailed document

---

## Template Validation Checklist

Before finalizing backlog table, ensure:

- [ ] "Last Updated" date is current
- [ ] All feature requests from backlog are included
- [ ] All defect fixes from backlog are included
- [ ] IDs link correctly to detailed files
- [ ] Priorities are assigned (🔴 🟠 🟡 🟢)
- [ ] Story points are estimated
- [ ] Status is current (⭕ ⏳ ✅)
- [ ] Sprint assignments are accurate
- [ ] Created and Updated dates are correct
- [ ] Table is sorted by priority (Critical → High → Medium → Low)
- [ ] Statistics are updated (if using)
- [ ] File is saved as `product-backlog.md`

