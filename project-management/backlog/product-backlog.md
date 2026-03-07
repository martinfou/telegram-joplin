---
template_version: 1.1.0
last_updated: 2026-03-07
compatible_with: [feature-request, bug-fix, sprint-planning]
requires: [markdown-support]
---

# Product Backlog

This is the main product backlog tracking all feature requests and bug fixes for the Telegram-Joplin Bot project.

**Last Updated**: 2026-03-06 (Sprint 13 ✅, Sprint 14 ✅, Sprint 15 ✅ completed)

## Project Overview

**Project Name**: Intelligent Telegram-Joplin Bot
**Current Sprint**: Sprint 16 (next)
**Status**: ⏳ In Progress - 91% Complete (227/248 story points)
**Timeline**: Sprint 10 ✅; Sprint 11 ✅; Sprint 12 ✅; Sprint 9 (FR-016) ~55%; Sprint 13 planned
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

**Sprints Completed**: 11 of 12 planned
**Current Sprint**: Sprint 12 (FR-026 Semantic Search)
**Next Sprint**: Sprint 16 (FR-034 Project Sync)
**Major Milestones**: Foundation ✅ → Components ✅ → Enhancements ✅ → Google Tasks ✅ → Tag Display ✅ → Reports ✅ → GTD Expert ✅ → Stoic Journal ✅ → Weekly Reports ✅ → Database Org (Sprint 9 ~55%) → Core UX (Sprint 10) ✅ → New Modalities (Sprint 11) ✅

## Feature Requests

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| [FR-001](features/FR-001-git-commit-template.md) | Add Git Commit Message Template | 🟠 High | 5 | ✅ | Sprint 1 | 2026-01-01 | 2026-01-01 |
| [FR-002](features/FR-002-mermaid-workflow-diagrams.md) | Add Mermaid Workflow Diagrams for Backlog Management | 🟠 High | 5 | ✅ | Sprint 1 | 2026-01-01 | 2026-01-01 |
| [FR-003](features/FR-003-update-quick-start-with-setup-script.md) | Update Quick Start Guide to Use Setup Script | 🟠 High | 3 | ✅ | Sprint 3 | 2026-01-01 | 2025-01-27 |
| [FR-004](features/FR-004-telegram-bot-interface.md) | Telegram Bot Interface | 🟠 High | 8 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [FR-005](features/FR-005-joplin-rest-api-client.md) | Joplin REST API Client | 🟠 High | 5 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [FR-006](features/FR-006-llm-integration-for-note-generation.md) | LLM Integration for Note Generation | 🟠 High | 8 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [FR-007](features/FR-007-conversation-state-management.md) | Conversation State Management | 🟠 High | 3 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [FR-008](features/FR-008-security-and-error-handling.md) | Security and Error Handling | 🟠 High | 3 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [FR-009](features/FR-009-initial-setup-and-configuration.md) | Initial Setup and Configuration | 🟠 High | 5 | ✅ | Sprint 2 | 2026-01-20 | 2026-01-20 |
| [FR-010](features/FR-010-database-logging-telegram-llm-decisions.md) | Database for Logging Telegram Conversations and LLM Decisions | 🟡 Medium | 8 | ✅ | Sprint 3 | 2025-01-27 | 2025-01-24 |
| [FR-011](features/FR-011-comprehensive-project-documentation.md) | Comprehensive Project Documentation for Multiple Audiences | 🟡 Medium | 13 | ✅ | Sprint 3 | 2025-01-27 | 2025-01-27 |
| [FR-012](features/FR-012-google-tasks-integration.md) | Google Tasks Integration for Task Logging | 🟡 Medium | 8 | ✅ | Sprint 4 | 2025-01-27 | 2025-01-23 |
| [FR-013](features/FR-013-display-tags-in-ai-response.md) | Display Tags in AI Response to Telegram | 🟡 Medium | 5 | ✅ | Sprint 5 | 2025-01-23 | 2025-01-24 |
| [FR-014](features/FR-014-daily-priority-report.md) | Daily Priority Report for Review and Action Items | 🟠 High | 8 | ✅ | Sprint 6 | 2025-01-23 | 2026-01-24 |
| [FR-015](features/FR-015-weekly-review-report.md) | Weekly Review and Report | 🟠 High | 13 | ✅ | Sprint 8 | 2025-01-23 | 2026-03-03 |
| [FR-016](features/FR-016-joplin-database-reorganization.md) | Joplin Database Reorganization, Tag Management, and Entry Enrichment | 🟠 High | 21 | ⏳ | Sprint 9 | 2025-01-23 | 2026-01-24 |
| [FR-017](features/FR-017-gtd-expert-persona.md) | GTD Expert Persona for 15-Minute Brain Dumping | 🟠 High | 8 | ✅ | Sprint 7 | 2026-01-24 | 2026-01-24 |
| [FR-018](features/FR-018-docker-compose-setup.md) | Docker Compose Setup for Bot and Joplin Server | 🟠 High | 8 | ⏳ | Backlog | 2026-01-24 | 2026-03-01 |
| [FR-019](features/FR-019-stoic-journal.md) | Stoic Journal with Morning/Evening Guided Reflection | 🟠 High | 5 | ✅ | Sprint 7 | 2026-02-15 | 2026-03-01 |
| [FR-020](features/FR-020-marketing-readme.md) | Marketing-Focused README with GTD + Second Brain Pitch | 🟠 High | 3 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [FR-021](features/FR-021-remove-ci-docker-build-step.md) | Remove Redundant Docker Build Step from CI | 🟡 Medium | 1 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [FR-022](features/FR-022-enforce-single-machine-limit.md) | Enforce Single Machine Limit on Fly.io | 🟠 High | 1 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [FR-023](features/FR-023-intelligent-content-routing.md) | Intelligent Content Routing (Notes vs Tasks) | 🟠 High | 8 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [FR-024](features/FR-024-greeting-and-command-help.md) | Greeting Response and Command Discovery | 🟡 Medium | 3 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [FR-025](features/FR-025-jungian-dream-analysis.md) | Jungian Dream Analysis with Image Generation | 🟡 Medium | 8 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [FR-026](features/FR-026-semantic-search-qa.md) | Semantic Search and Q&A Over Notes | 🟠 High | 13 | ✅ | Sprint 12 | 2026-03-05 | 2026-03-06 |
| [FR-027](features/FR-027-weekly-planning-session.md) | Weekly Planning Session | 🟡 Medium | 8 | ✅ | Sprint 12 | 2026-03-05 | 2026-03-05 |
| [FR-028](features/FR-028-read-later-queue.md) | Read Later Queue | 🟡 Medium | 5 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [FR-029](features/FR-029-quick-note-search.md) | Quick Note Search | 🟡 Medium | 3 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [FR-030](features/FR-030-photo-ocr-capture.md) | Photo/Screenshot OCR Capture | 🟡 Medium | 5 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [FR-031](features/FR-031-monthly-review-report.md) | Monthly Review Report | 🟢 Low | 5 | ✅ | Sprint 10 | 2026-03-05 | 2026-03-05 |
| [FR-032](features/FR-032-habit-tracking.md) | Habit Check-ins and Tracking | 🟢 Low | 5 | ✅ | Sprint 11 | 2026-03-05 | 2026-03-05 |
| [FR-033](features/FR-033-flashcard.md) | Flashcard Practice from Notes | 🟠 High | 8 | ✅ | Sprint 14 | 2026-03-05 | 2026-03-06 |
| [FR-034](features/FR-034-joplin-google-tasks-project-sync.md) | Joplin Projects ↔ Google Tasks Sync (Project = Task, Tasks = Subtasks) | 🟠 High | 13 | ⭕ | Backlog | 2026-03-05 | 2026-03-05 |
| [FR-035](features/FR-035-world-class-brain-dump.md) | World-Class Brain Dump Experience (modes, time awareness, recovery, personalization) | 🟠 High | 13 | ⭕ | Backlog | 2026-03-05 | 2026-03-05 |
| [FR-036](features/FR-036-documentation-code-consistency-review.md) | Documentation-Code Consistency Review (pre-sprint planning, hybrid, report) | 🟠 High | 8 | ✅ | Sprint 13 | 2026-03-05 | 2026-03-05 |
| [FR-037](features/FR-037-reports-great-on-telegram.md) | Reports Look Great on Telegram | 🟡 Medium | 5 | ✅ | Backlog | 2026-03-05 | 2026-03-06 |
| [FR-038](features/FR-038-ai-identity-user-profile-chat-history.md) | AI Identity, User Profile, and Chat History | 🟡 Medium | 8 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-039](features/FR-039-star-on-task-as-high-priority.md) | Treat Star on Task as High Priority | 🟡 Medium | 3 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |
| [FR-040](features/FR-040-check-existing-task-note-update-append.md) | Check if Task or Note Exists, Offer Update or Append | 🟡 Medium | 8 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-041](features/FR-041-project-management-commit-style-and-doc-sync.md) | Project Management: Commit Style and Document Sync Sections | 🟡 Medium | 5 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-042](features/FR-042-stoic-what-i-learned-today.md) | Stoic Journal: "What I Learned Today" Section | 🟡 Medium | 4 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-043](features/FR-043-report-generation-speed-and-ui-updates.md) | Report Generation: Speed Up with Async and Chat UI Updates | 🟡 Medium | 5 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-044](features/FR-044-project-new-command.md) | /project_new Command to Create Project with Default Folders | 🟡 Medium | 5 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |
| [FR-045](features/FR-045-photo-folder-quick-reply.md) | Photo OCR: Folder Quick-Reply for NEED_INFO | 🟡 Medium | 3 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-046](features/FR-046-photo-ocr-unprocessable-test.md) | Photo OCR: Test for OCRUnprocessableImageError | 🟡 Medium | 1 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-047](features/FR-047-photo-ocr-retry-transient.md) | Photo OCR: Retry on Transient Failures | 🟡 Medium | 2 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-048](features/FR-048-photo-albums.md) | Photo OCR: Photo Albums Support | 🟢 Low | 5 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-049](features/FR-049-photo-ocr-cost-logging.md) | Photo OCR: Cost Logging | 🟢 Low | 2 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |
| [FR-050](features/FR-050-photo-send-as-file-hint.md) | Photo OCR: "Send as File" Hint in Help | 🟢 Low | 1 | ⭕ | Backlog | 2026-03-06 | 2026-03-06 |

## Bug Fixes

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| [BF-001](bugs/BF-001-google-tasks-sync-no-token.md) | Google Tasks Sync Fails: No Google token found for user | 🟠 High | 2 | ✅ | Backlog | 2026-03-01 | 2026-03-01 |
| [BF-002](bugs/BF-002-github-actions-build-failure.md) | GitHub Actions Build Failure | 🔴 Critical | 3 | ✅ | Backlog | 2026-03-01 | 2026-03-03 |
| [BF-003](bugs/BF-003-scheduler-not-working.md) | Scheduler Not Working — App Down | 🔴 Critical | 5 | ✅ | Backlog | 2026-03-01 | 2026-03-03 |
| [BF-004](bugs/BF-004-flyctl-deploy-no-access-token.md) | Fly.io Deploy Fails: No Access Token Available | 🔴 Critical | 1 | ✅ | Backlog | 2026-03-03 | 2026-03-03 |
| [BF-005](bugs/BF-005-stoic-journal-timezone-and-data-loss.md) | Stoic Journal: Timezone Mismatch & Data Loss on Update | 🔴 Critical | 5 | ✅ | Backlog | 2026-03-03 | 2026-03-05 |
| [BF-006](bugs/BF-006-stoic-session-stuck-loop-no-cancel.md) | Stoic Session Stuck in Loop with No Cancel | 🟠 High | 3 | ✅ | Backlog | 2026-03-04 | 2026-03-05 |
| [BF-007](bugs/BF-007-url-screenshot-no-content-validation.md) | URL Screenshots: No Validation That Content Matches URL | 🟠 High | 5 | ✅ | Sprint 13 | 2026-03-04 | 2026-03-05 |
| [BF-008](bugs/BF-008-stoic-evening-deletes-morning.md) | Stoic Evening Deletes Morning Reflection | 🔴 Critical | 5 | ✅ | Backlog | 2026-03-04 | 2026-03-05 |
| [BF-009](bugs/BF-009-stoic-questions-template-mismatch.md) | Stoic Journal: Questions Do Not Match Template | 🟠 High | 3 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-010](bugs/BF-010-greeting-parse-entities-error.md) | Greeting Response: "Something Went Wrong" (Parse Entities) | 🟠 High | 2 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-011](bugs/BF-011-content-decision-validation-error.md) | ContentDecision Validation + Greeting Shows Menu | 🟠 High | 1 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-012](bugs/BF-012-mypy-module-resolution.md) | Mypy Module Resolution Error | 🟡 Medium | 0.5 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-013](bugs/BF-013-double-check-mark-success.md) | Double Check Mark on Task/Note Creation Success | 🟢 Low | 0.5 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-014](bugs/BF-014-dream-parse-entities-error.md) | /dream Parse Entities Error (BadRequest) | 🟠 High | 2 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-015](bugs/BF-015-mypy-type-errors.md) | Mypy Type Errors (60 errors in 23 files) | 🟡 Medium | 5 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-016](bugs/BF-016-dream-parse-error-user-report.md) | /dream Parse Error: User Receives Nothing | 🟠 High | 2 | ✅ | Backlog | 2026-03-05 | 2026-03-05 |
| [BF-017](bugs/BF-017-dream-command-crash.md) | /dream Command Crashes Agent on Invocation | 🟠 High | 1 | ✅ | Sprint 14 | 2026-03-05 | 2026-03-06 |
| [BF-018](bugs/BF-018-weekly-report-incorrect-numbers.md) | Weekly Report Shows Incorrect Numbers (0 Notes/Tasks) | 🟠 High | 3 | ✅ | Backlog | 2026-03-05 | 2026-03-06 |
| [BF-019](bugs/BF-019-dream-message-too-long.md) | Dream Analysis: "Message is too long" Error | 🟠 High | 2 | ✅ | Backlog | 2026-03-06 | 2026-03-06 |
| [BF-020](bugs/BF-020-daily-report-column-overlap.md) | Daily Report: Column Overlap, SOURCE Column Not Required | 🟡 Medium | 1 | ✅ | Backlog | 2026-03-06 | 2026-03-06 |
| [BF-021](bugs/BF-021-weekly-report-ugly-formatting.md) | Weekly Report: Ugly Formatting, Needs Pretty Tables | 🟡 Medium | 2 | ✅ | Backlog | 2026-03-06 | 2026-03-06 |
| [BF-022](bugs/BF-022-find-command-flyio-error.md) | /find Command Error in Fly.io Logs | 🟠 High | 2 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |
| [BF-023](bugs/BF-023-ask-command-crash.md) | /ask Command Crashes on Certain Prompts | 🟠 High | 2 | ✅ | Sprint 15 | 2026-03-06 | 2026-03-06 |

---

## Status Values

- ⭕ **Not Started**: Item not yet started
- ⏳ **In Progress**: Item currently being worked on
- ✅ **Completed**: Item finished and verified

## Priority Levels

- 🔴 **Critical**: Blocks core functionality, must be fixed/implemented immediately
- 🟠 **High**: Important feature/bug, should be addressed soon
- 🟡 **Medium**: Nice to have, can wait
- 🟢 **Low**: Future consideration, low priority

## Column Definitions

- **ID**: Unique identifier (FR-XXX for features, BF-XXX for bugs)
  - Link to detailed item: `[FR-001](features/FR-001-feature-name.md)`
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
| **Sprint 5** | Jan 27-31 | FR-013 (Tag Display) | 5 | ✅ Complete |
| **Sprint 6** | Feb 3-16 | FR-014 (Daily Reports) | 8 | ✅ Complete |
| **Sprint 7** | Jan 24-31 (Accelerated) | FR-017 (GTD Expert), FR-019 (Stoic Journal) | 13 | ✅ Complete |
| **Sprint 8** | Feb 24-Mar 9 | FR-015 (Weekly Reports) | 13 | ✅ Complete |
| **Sprint 9** | Mar 10-31 | FR-016 (DB Reorganization) | 21 | ⏳ ~55% Complete |
| **Sprint 10** | Mar 10-23 | Core UX + Joplin 24/7 (FR-024, FR-029, FR-023, FR-031) | 20 | ✅ Complete |
| **Sprint 11** | Mar 24-Apr 6 | FR-030, FR-028, FR-025, FR-032, FR-027 (New Modalities) | 31 | ✅ Complete |
| **Sprint 12** | Apr 7-20 | FR-026 (Semantic Search), FR-027 (Weekly Planning) | 21 | ✅ Complete |
| **Sprint 13** | Apr 21-May 4 | BF-007 (URL validation), FR-036 (Doc-code review) | 13 | ✅ Complete |
| **Sprint 14** | May 5-18 | BF-017 (Dream fix), FR-033 (Flashcard) | 9 | ✅ Complete |
| **Sprint 15** | May 19-Jun 1 | BF-022, BF-023, FR-044 (/project_new), FR-039 (Star) | 12 | ✅ Complete |

**Remaining Backlog**: 47 points (FR-016 ~55%, FR-018 ~30%, FR-034, FR-035)
**Projected Completion**: TBD — CI/CD operational, new features added to backlog

## Notes

- Feature request details: See `features/FR-XXX-*.md` files
- Bug fix details: See `bugs/BF-XXX-*.md` files
- Sprint assignments: See `../sprints/sprint-XX-*.md` files
- Sprint & Backlog Planning: See `../docs/sprint-and-backlog-planning.md`
- Historical velocity: ~14 points/week average

## Backlog Statistics

**Total Items**: 50 Features + 20 Bugs = 70 items

**Features by Status**:
- ⭕ Not Started: 13 (FR-034, FR-035, FR-038, FR-040, FR-041, FR-042, FR-043, FR-045, FR-046, FR-047, FR-048, FR-049, FR-050)
- ⏳ In Progress: 3 (FR-016, FR-018, FR-036)
- ✅ Completed: 29 (FR-001–FR-015, FR-017, FR-019–FR-024, FR-025, FR-027–FR-032)

**Bugs by Status**:
- ⏳ In Progress: 0
- ⭕ Not Started: 0
- ✅ Completed: 16 (BF-001–BF-006, BF-008–BF-016, BF-018–BF-021)

**By Priority (all items)**:
- 🔴 Critical: 5 (BF-002, BF-003, BF-004, BF-005, BF-008 resolved)
- 🟠 High: 13
- 🟡 Medium: 15
- 🟢 Low: 3

**Feature Story Points**: 260
  - Completed: 227 points (FR-001–FR-015, FR-017, FR-019–FR-025, FR-027–FR-033, FR-036, FR-039, FR-044) — 85%
  - In Progress: 29 points (FR-016 ~55%, FR-018 ~30%)
  - Not Started: 66 points (FR-034, FR-035, FR-038, FR-040, FR-041, FR-042, FR-043, FR-045–FR-050)

**Bug Story Points**: 48
  - Completed: 48 points (BF-001–BF-006, BF-008–BF-017, BF-018–BF-019, BF-022, BF-023)
  - In Progress: 0 points
  - Not Started: 0 points

**Overall Completion Rate**: 91% features completed (227/248 points)
**Current**: 91% (227/248 points) ✅
**Full Completion Target**: TBD — FR-016, FR-018, FR-026, FR-033, FR-034, FR-035, FR-036, FR-037, FR-038, FR-039, FR-040, FR-041, FR-042, FR-043, FR-044 remaining

---

## Sprint Summary

### All Sprints

| Sprint | Duration | Goal | Points | Status | Velocity |
|--------|----------|------|--------|--------|----------|
| [Sprint 1](../sprints/sprint-01-foundation-templates.md) | Jan 1-10 | Foundation Templates | 5 | ✅ | 5 pts |
| [Sprint 2](../sprints/sprint-02-foundation-components.md) | Jan 10-20 | Foundation Components | 26 | ✅ | 26 pts |
| [Sprint 3](../sprints/sprint-03-foundation-enhancements.md) | Jan 20-27 | Foundation Enhancements | 35 | ✅ | 35 pts |
| [Sprint 4](../sprints/sprint-04-google-tasks-integration.md) | Jan 23-24 | Google Tasks Integration | 8 | ✅ | 8 pts |
| [Sprint 5](../sprints/sprint-05-user-engagement-features.md) | Jan 27-31 | Display Tags (FR-013) | 5 | ✅ | 5 pts |
| [Sprint 6](../sprints/sprint-06-daily-priority-reports.md) | Feb 3-16 | Daily Reports (FR-014) | 8 | ✅ | 8 pts |
| [Sprint 7](../sprints/sprint-07-gtd-expert-persona.md) | Jan 24-31 | GTD Expert (FR-017) + Stoic Journal (FR-019) | 13 | ✅ | 13 pts |
| Sprint 8 | Feb 24-Mar 9 | Weekly Reports (FR-015) | 13 | ✅ | 13 pts |
| Sprint 9 | Mar 10-31 | Database Reorganization (FR-016) | 21 | ⏳ ~55% | — |
| [Sprint 10](../sprints/sprint-10-core-ux.md) | Mar 10-23 | Core UX + Joplin 24/7 (FR-024, FR-029, FR-023, FR-031) | 20 | ✅ Complete | 20 pts |
| [Sprint 11](../sprints/sprint-11-new-modalities.md) | Mar 24-Apr 6 | New Modalities (FR-030, FR-028, FR-025, FR-032, FR-027) | 31 | ✅ Complete | 31 pts |
| [Sprint 12](../sprints/sprint-12-advanced-intelligence.md) | Apr 7-20 | Advanced Intelligence (FR-026) | 13 | ✅ Complete | 13 pts |
| [Sprint 13](../sprints/sprint-13-quality-and-validation.md) | Apr 21-May 4 | Quality and Validation (BF-007, FR-036) | 13 | ✅ Complete | 13 pts |
| [Sprint 14](../sprints/sprint-14-flashcard-and-dream-fix.md) | May 5-18 | Flashcard & Dream Fix (BF-017, FR-033) | 9 | ✅ Complete | 9 pts |
| [Sprint 15](../sprints/sprint-15-stability-and-project-foundation.md) | May 19-Jun 1 | Stability & Project Foundation (BF-022, BF-023, FR-044, FR-039) | 12 | ✅ Complete | 12 pts |
| **TOTAL** | | | **282 pts** | **198 Complete, 84 Planned** | **14 avg** |

**Completion Status**: 82% Complete (198/248 points)
  - Sprint 10 Complete: FR-023, FR-024, FR-029, FR-031, Joplin 24/7 ✅
  - Sprint 11 Complete: FR-025, FR-027, FR-028, FR-030, FR-032 ✅
  - Sprint 12 Complete: FR-026 (Semantic Search), FR-027 ✅
  - Sprint 9 (Mar 10–31): FR-016 ~55% complete
  - Sprint 13: BF-007, FR-036 ✅ complete
  - Sprint 14: BF-017, FR-033 ✅ complete
  - Sprint 15: BF-022, BF-023, FR-044, FR-039 ✅ complete
  - Backlog: FR-018 ~30%, FR-034, FR-035, FR-038, FR-040, FR-041, FR-042, FR-043

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
| [FR-042](features/FR-042-user-authentication.md) | User Authentication | 🟠 High | 13 | ⏳ | Sprint 5 | 2024-01-10 | 2024-01-15 |

This entry indicates:
- Feature Request #42 about User Authentication
- High priority
- Estimated at 13 story points
- Currently in progress
- Assigned to Sprint 5
- Created on January 10, 2024
- Last updated on January 15, 2024
- Clicking FR-042 links to detailed document

---

## Template Validation Checklist

Before finalizing backlog table, ensure:

- [ ] "Last Updated" date is current
- [ ] All feature requests from backlog are included
- [ ] All bug fixes from backlog are included
- [ ] IDs link correctly to detailed files
- [ ] Priorities are assigned (🔴 🟠 🟡 🟢)
- [ ] Story points are estimated
- [ ] Status is current (⭕ ⏳ ✅)
- [ ] Sprint assignments are accurate
- [ ] Created and Updated dates are correct
- [ ] Table is sorted by priority (Critical → High → Medium → Low)
- [ ] Statistics are updated (if using)
- [ ] File is saved as `product-backlog.md`

