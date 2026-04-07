---
template_version: 1.1.0
last_updated: 2025-01-27
compatible_with: [feature-request, defect-fix, product-backlog]
requires: [markdown-support]
---

# Sprint Planning Template

This template provides the structure for sprint planning documents. Adapt this template to your team's Agile/Scrum practices.

## Usage

0. **Before planning**: Run Documentation-Code Consistency Review (`./scripts/doc-code-review.sh`). See [Definition of Done](../definition-of-done.md).

1. Copy this template for each sprint
2. Fill in sprint header information
3. Add user stories from the product backlog
4. Break down stories into tasks
5. Estimate tasks and track progress
6. Save as: `sprints/sprint-[XX]-[sprint-name].md`

---

# Sprint [Number]: [Sprint Name]

**Sprint Goal**: [Clear, measurable goal for this sprint]

**Duration**: [Start Date] - [End Date] ([X] weeks)  
**Team Velocity**: [Previous sprint velocity or target velocity]  
**Sprint Planning Date**: [Date]  
**Sprint Review Date**: [Date]  
**Sprint Retrospective Date**: [Date]

## Sprint Overview

**Focus Areas**:
- [Primary focus area 1]
- [Primary focus area 2]
- [Primary focus area 3]

**Key Deliverables**:
- [Deliverable 1]
- [Deliverable 2]
- [Deliverable 3]

**Dependencies**:
- [Dependency 1 - what must be completed first]
- [Dependency 2 - what must be completed first]

**Risks & Blockers**:
- [Risk/Blocker 1]
- [Risk/Blocker 2]

---

## User Stories

### Story [Number]: [Story Title] - [X] Points

**User Story**: As a [user type], I want [functionality], so that [benefit].

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Reference Documents**:
- [Document Name 1] - [Section/Page]
- [Document Name 2] - [Section/Page]

**Technical References**:
- Architecture: [Link to architecture documentation]
- Feature Spec: [Link to feature specification]
- Data Models: [Link to data models documentation]

**Story Points**: [X] (Fibonacci: 1, 2, 3, 5, 8, 13)

**Priority**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low

**Status**: ⭕ Not Started / ⏳ In Progress / ✅ Completed

**Backlog Reference**: [US-XXX or DEF-XXX] - [Link to backlog item]

**Tasks**:

| Task ID | Task Description | Class/Method Reference | Document Reference | Status | Points | Assignee |
|---------|------------------|------------------------|---------------------|--------|--------|----------|
| T-001 | [Task description] | `ClassName.methodName()` | [Document Name] - [Section] | ⭕ | [X] | [Name] |
| T-002 | [Task description] | `ClassName.methodName()` | [Document Name] - [Section] | ⭕ | [X] | [Name] |

**Total Task Points**: [X]

---

### Story [Number]: [Story Title] - [X] Points

[Repeat structure above for each story]

---

## Sprint Summary

**Total Story Points**: [X]  
**Total Task Points**: [X]  
**Estimated Velocity**: [X] points (based on story points)

**Sprint Burndown**:
- Day 1: [X] points completed
- Day 2: [X] points completed
- ...
- Day [N]: [X] points completed

**Sprint Review Notes**:
- [ ] Documentation-Code Consistency Review run this sprint (or since last sprint); no unresolved high-priority contradictions
- [Notes from sprint review meeting]
- [Completed features demonstrated]
- [Feedback received]
- [ ] [RELEASE_NOTES.md](../../../RELEASE_NOTES.md) updated (see [release-notes-process.md](../processes/release-notes-process.md))

**Sprint Retrospective Notes**:
- **What went well?**
  - [Item 1]
  - [Item 2]
  
- **What could be improved?**
  - [Item 1]
  - [Item 2]
  
- **Action items for next sprint**
  - [Action item 1]
  - [Action item 2]

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

### Estimation Factors

Consider:
- **Complexity**: How complex is the task?
- **Uncertainty**: How much is unknown?
- **Effort**: How much work is required?
- **Risk**: What are the risks?

---

## Task Breakdown Guidelines

### Good Task Characteristics

- **Specific**: Clear what needs to be done
- **Actionable**: Can be started immediately
- **Testable**: Has clear completion criteria
- **Referenced**: Links to technical documents
- **Estimated**: Has story points assigned
- **Small**: Can be completed in 1-2 days (ideally)

### Technical References

Each task should reference:
- **Class/Method**: Specific code location
- **Document**: Relevant specification document
- **Section**: Specific section in document

**Format examples**:
- Class: `FlashcardService` (or domain-specific class)
- Method: `get_due_cards()` (or domain-specific method)
- File: `src/flashcard_service.py` (or `src/handlers/flashcard.py`)
- API Endpoint: `POST /api/v1/users` (if applicable)
- Database: `users` table

---

## Sprint Tracking

### Daily Standup Format

- What did I complete yesterday?
- What will I work on today?
- Are there any blockers?

### Sprint Burndown

Track daily progress:
- Story points completed
- Tasks completed
- Remaining work
- Velocity tracking

### Sprint Review

- Demo completed features
- Review acceptance criteria
- Gather feedback from stakeholders
- Update backlog based on feedback

### Sprint Retrospective

- What went well?
- What could be improved?
- Action items for next sprint
- Process improvements

---

## Status Values

### Story/Task Status
- ⭕ **Not Started**: Not yet begun
- ⏳ **In Progress**: Currently being worked on
- ✅ **Completed**: Finished and verified

### Priority Levels
- 🔴 **Critical**: Must be completed this sprint
- 🟠 **High**: Important, should be completed
- 🟡 **Medium**: Nice to have
- 🟢 **Low**: Can be deferred if needed

---

## Example Sprint Entry

```markdown
### Story 1: User Authentication - 13 Points

**User Story**: As a user, I want to log in with email and password, so that I can access my account securely.

**Acceptance Criteria**:
- [ ] User can log in with valid email and password
- [ ] Error message shown for invalid credentials
- [ ] Session persists across browser restarts
- [ ] User can log out
- [ ] Password is securely hashed

**Reference Documents**:
- Architecture documentation - Authentication section
- Security requirements - Password handling

**Technical References**:
- Service: `AuthService`
- Method: `AuthService.login()`
- Database: `users` table

**Story Points**: 13

**Priority**: 🟠 High

**Status**: ⏳ In Progress

**Tasks**:

| Task ID | Task Description | Class/Method Reference | Document Reference | Status | Points | Assignee |
|---------|------------------|------------------------|---------------------|--------|--------|----------|
| T-001 | Create AuthService class | `AuthService` | Architecture docs | ✅ | 3 | Alice |
| T-002 | Implement login method | `AuthService.login()` | Security requirements | ⏳ | 5 | Alice |
| T-003 | Add password hashing | `PasswordHasher.hash()` | Security requirements | ⭕ | 3 | Bob |
| T-004 | Create login UI component | `LoginForm` | UI wireframes | ⭕ | 5 | Carol |
| T-005 | Write unit tests | `AuthServiceTest` | Test specifications | ⭕ | 3 | Alice |

**Total Task Points**: 19
```

---

## Notes

- Adjust sprint duration based on your team's cadence (common: 1-3 weeks)
- Update burndown chart daily during sprint
- Review and refine tasks during sprint planning
- Break down large tasks (> 8 points) into smaller subtasks
- Update status regularly to reflect current progress

---

## Template Validation Checklist

Before finalizing sprint planning, ensure:

- [ ] Sprint goal is clear and measurable
- [ ] Sprint duration and dates are specified
- [ ] Team velocity is documented (previous or target)
- [ ] All user stories are added from backlog
- [ ] User stories have acceptance criteria
- [ ] Stories are broken down into tasks
- [ ] Tasks have technical references
- [ ] Story points are estimated for stories
- [ ] Task points are estimated (if using)
- [ ] Total story points match team capacity
- [ ] Dependencies are identified
- [ ] Risks and blockers are documented
- [ ] Sprint planning date is set
- [ ] Sprint review and retrospective dates are set
- [ ] File is saved with correct naming convention: `sprint-XX-sprint-name.md`
- [ ] Backlog items are updated with sprint assignment

