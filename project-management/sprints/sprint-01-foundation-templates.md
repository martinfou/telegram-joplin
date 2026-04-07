---
template_version: 1.1.0
last_updated: 2026-01-01
compatible_with: [feature-request, defect-fix, product-backlog]
requires: [markdown-support]
---

# Sprint 1: Foundation Templates

**Sprint Goal**: Establish core templates and documentation workflows for the backlog toolkit, including git commit templates and visual workflow diagrams.

**Duration**: 2026-01-01 - 2026-01-15 (2 weeks)  
**Team Velocity**: 10 points (initial sprint, target based on selected backlog items)  
**Sprint Planning Date**: 2026-01-01  
**Sprint Review Date**: 2026-01-15  
**Sprint Retrospective Date**: 2026-01-15

## Sprint Overview

**Focus Areas**:
- Complete git commit message template implementation
- Add Mermaid workflow diagrams to backlog management process
- Establish documentation standards and templates

**Key Deliverables**:
- Completed git commit message template (US-001)
- Mermaid workflow diagrams integrated into process documentation (US-002)
- Updated backlog management process document with visual workflows

**Dependencies**:
- None - both features are independent

**Risks & Blockers**:
- Mermaid.js rendering compatibility across different markdown viewers
- Ensuring diagrams accurately represent the workflow process

---

## User Stories

### Story 1: Add Git Commit Message Template - 5 Points

**User Story**: As a developer working on this project, I want a standardized git commit message template, so that all commits follow a consistent format that links to backlog items, clearly describes business value, and provides technical details for other developers.

**Acceptance Criteria**:
- [x] Git commit message template created (markdown format with guidelines)
- [x] Git commit message template created (text format for direct git integration)
- [x] Git commit message examples document created with multiple scenarios
- [x] Template includes task number format (US-XXX or DEF-XXX)
- [x] Template includes business description section
- [x] Template includes technical changes section
- [x] Template documented in template-catalog.md
- [x] Examples demonstrate proper usage for features, bugs, and small changes
- [x] Changelog updated to reflect new templates

**Reference Documents**:
- Git Commit Template: `templates/git-commit-template.md`
- Git Commit Examples: `examples/git-commit-example.md`
- Template Catalog: `template-catalog.md`
- Changelog: `changelog.md`

**Technical References**:
- Template file: `backlog-toolkit/templates/git-commit-template.md`
- Template file (txt): `backlog-toolkit/templates/git-commit-template.txt`
- Example file: `backlog-toolkit/examples/git-commit-example.md`
- Product backlog: `backlog-toolkit/project-management/backlog/product-backlog.md`

**Story Points**: 5

**Priority**: 🟠 High

**Status**: ✅ Completed

**Backlog Reference**: [US-001](../backlog/user-stories/US-001-git-commit-template.md) - Add Git Commit Message Template

**Tasks**:

| Task ID | Task Description | Class/Method Reference | Document Reference | Status | Points | Assignee |
|---------|------------------|------------------------|---------------------|--------|--------|----------|
| T-001 | Verify all acceptance criteria are met | N/A | US-001 acceptance criteria | ✅ | 1 | Team |
| T-002 | Review template files for completeness | `templates/git-commit-template.md` | Template documentation | ✅ | 1 | Team |
| T-003 | Verify examples document covers all scenarios | `examples/git-commit-example.md` | Examples documentation | ✅ | 1 | Team |
| T-004 | Confirm template-catalog.md includes new template | `template-catalog.md` | Template catalog | ✅ | 1 | Team |
| T-005 | Final review and mark story as complete | N/A | Sprint review | ✅ | 1 | Team |

**Total Task Points**: 5

---

### Story 2: Add Mermaid Workflow Diagrams for Backlog Management - 5 Points

**User Story**: As a team member (developer, product owner, or scrum master), I want visual workflow diagrams using Mermaid.js that show how feature requests and defect fixes flow from creation to sprint planning, so that I can quickly understand the process, identify where items are in the workflow, and ensure proper procedures are followed.

**Acceptance Criteria**:
- [x] Mermaid flowchart diagram created showing feature request workflow (creation → backlog → refinement → sprint planning)
- [x] Mermaid flowchart diagram created showing defect fix workflow (creation → backlog → immediate action/sprint planning)
- [x] Mermaid state diagram created showing status lifecycle (Not Started → In Progress → Completed)
- [x] Diagrams integrated into backlog management process document
- [x] Diagrams include decision points (e.g., critical defect vs. regular defect)
- [x] Diagrams include all key steps from the process document
- [x] Diagrams are properly formatted and render correctly in markdown viewers
- [x] Diagrams reference relevant sections of the process document
- [x] Example diagrams added to examples folder for reference

**Reference Documents**:
- Backlog Management Process: `backlog-toolkit/processes/backlog-management-process.md`
- Product Backlog Structure: `backlog-toolkit/processes/product-backlog-structure.md`
- Sprint Planning Template: `backlog-toolkit/templates/sprint-planning-template.md`

**Technical References**:
- Process document: `backlog-toolkit/processes/backlog-management-process.md`
- Examples folder: `backlog-toolkit/examples/`
- Mermaid.js documentation: https://mermaid.js.org/

**Story Points**: 5

**Priority**: 🟠 High

**Status**: ✅ Completed

**Backlog Reference**: [US-002](../backlog/user-stories/US-002-mermaid-workflow-diagrams.md) - Add Mermaid Workflow Diagrams for Backlog Management

**Tasks**:

| Task ID | Task Description | Class/Method Reference | Document Reference | Status | Points | Assignee |
|---------|------------------|------------------------|---------------------|--------|--------|----------|
| T-006 | Review proposed diagrams in US-002 for accuracy | `US-002-mermaid-workflow-diagrams.md` | Feature request document | ✅ | 1 | Team |
| T-007 | Integrate feature request workflow diagram into process doc | `processes/backlog-management-process.md` | Backlog management process | ✅ | 1 | Team |
| T-008 | Integrate defect fix workflow diagram into process doc | `processes/backlog-management-process.md` | Backlog management process | ✅ | 1 | Team |
| T-009 | Integrate status lifecycle diagram into process doc | `processes/backlog-management-process.md` | Backlog management process | ✅ | 1 | Team |
| T-010 | Test diagram rendering in multiple markdown viewers | N/A | Testing documentation | ✅ | 1 | Team |
| T-011 | Add example diagrams to examples folder | `examples/` | Examples documentation | ✅ | 1 | Team |

**Total Task Points**: 6

---

## Sprint Summary

**Total Story Points**: 10  
**Total Task Points**: 11  
**Estimated Velocity**: 10 points (based on story points)

**Sprint Burndown**:
- Day 1 (2026-01-01): 0 points completed (Sprint planning)
- Day 1 (2026-01-01): 6 points completed (Story 2 tasks completed)
- Day 2: [X] points completed
- Day 3: [X] points completed
- ...
- Day 14 (2026-01-15): [X] points completed

**Sprint Review Notes**:
- [To be filled during sprint review]

**Sprint Retrospective Notes**:
- **What went well?**
  - [To be filled during retrospective]
  
- **What could be improved?**
  - [To be filled during retrospective]
  
- **Action items for next sprint**
  - [To be filled during retrospective]

---

## Story Point Estimation Guide

### Fibonacci Sequence

Use Fibonacci sequence for story point estimation:
- **1 Point**: Trivial task, < 1 hour
- **2 Points**: Simple task, 1-4 hours
- **3 Points**: Small task, 4-8 hours
- **5 Points**: Medium task, 1-2 days
- **8 Points**: Large task, 2-3 days
- **13 Points**: Very large task, 3-5 days (should be broken down)

---

## Notes

- Both stories are high priority and foundational for the backlog toolkit
- US-001 is already in progress with most acceptance criteria met
- US-002 needs implementation of diagrams into the process document
- Diagrams proposed in US-002 should be reviewed and refined before integration
- Test Mermaid.js rendering in GitHub, GitLab, VS Code, and other common viewers

