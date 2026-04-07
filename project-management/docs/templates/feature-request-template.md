---
template_version: 1.1.0
last_updated: 2025-01-27
compatible_with: [defect-fix, sprint-planning, product-backlog]
requires: [markdown-support]
---

# Feature Request Template

This is a generic template for creating feature requests. Copy this template when adding new features to your product backlog.

## Usage

1. Copy this template
2. Assign unique ID (e.g., US-001, US-042, or use your ID format)
3. Fill in all sections
4. Save to: `backlog/user-stories/[ID]-[feature-name].md`
5. Add entry to main product backlog table

---

# Feature Request: [ID] - [Feature Title]

**Status**: ⭕ Not Started  
**Priority**: 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low  
**Story Points**: [X] (Fibonacci: 1, 2, 3, 5, 8, 13)  
**Created**: [YYYY-MM-DD]  
**Updated**: [YYYY-MM-DD]  
**Assigned Sprint**: [Sprint Number or "Backlog"]

## Description

[Clear description of the feature request. Explain what needs to be built and why.]

## User Story

As a [user type: e.g., "registered user", "admin", "mobile app user"], 
I want [functionality: e.g., "to filter search results by date"], 
so that [benefit: e.g., "I can quickly find recent items"].

**Tips**:
- Start with user role
- Use action verbs (filter, create, delete, view)
- Focus on value, not implementation
- Be specific about the benefit

**Examples**:
- As a registered user, I want to filter search results by date, so that I can quickly find recent items.
- As an admin, I want to export user data to CSV, so that I can generate reports.
- As a mobile app user, I want to save items offline, so that I can access them without internet.

## Acceptance Criteria

- [ ] Criterion 1 (specific, testable)
- [ ] Criterion 2 (specific, testable)
- [ ] Criterion 3 (specific, testable)

**Tips for Good Acceptance Criteria**:
- Be specific and testable
- Use measurable outcomes
- Include edge cases if relevant
- Cover both happy path and error scenarios

## Business Value

[Why this feature is important and what problem it solves. Include user impact and business benefits.]

Examples:
- Improves user experience by reducing steps from 5 to 2
- Increases user engagement by enabling key workflow
- Reduces support tickets by 30%
- Enables new revenue stream

## Technical Requirements

[Technical implementation details and requirements. Include any constraints, performance requirements, or technical considerations.]

**Note**: Use **Mermaid** for architecture diagrams, flowcharts, or sequence diagrams. See [documentation-standards.md](../processes/documentation-standards.md).

Examples:
- Must support 1000+ concurrent users
- Response time < 200ms
- Requires database migration
- Must be backward compatible
- API rate limits: 1000 requests/hour

## Reference Documents

- [Document Name 1] - [Section/Page/Section Name]
- [Document Name 2] - [Section/Page/Section Name]

**Examples**:
- Architecture documentation - Feature design section
- UI/UX wireframes - Feature mockups
- API documentation - Endpoint specifications
- Requirements document - Feature requirements

## Technical References

[Links to specific code locations, classes, or technical specifications. Adapt format to your tech stack.]

**Format examples**:
- Class: `HabitService` (or domain-specific class)
- Method: `add_habit()` (or domain-specific method)
- File: `src/habit_service.py` (or `src/handlers/habits.py`)
- API Endpoint: `POST /api/v1/feature` (if applicable)
- Database Table: `habits` (or domain-specific table)

## Dependencies

- [Dependency 1 - what must be completed first]
- [Dependency 2 - what must be completed first]

Examples:
- Authentication system must be implemented
- Database schema migration must be deployed
- External API integration must be completed
- Feature X must be merged first

## Notes

[Additional notes, considerations, context, or open questions.]

Examples:
- This is a critical feature for MVP
- Alternative approach discussed but rejected because...
- User research shows high demand for this feature
- Technical spike needed to evaluate performance impact

## History

- [YYYY-MM-DD] - Created
- [YYYY-MM-DD] - Status changed to ⏳ In Progress
- [YYYY-MM-DD] - Assigned to Sprint [X]
- [YYYY-MM-DD] - Status changed to ✅ Completed

---

## Status Values

- ⭕ **Not Started**: Item not yet started
- ⏳ **In Progress**: Item currently being worked on
- ✅ **Completed**: Item finished and verified

## Priority Levels

- 🔴 **Critical**: Blocks core functionality, must be fixed immediately
- 🟠 **High**: Important feature, should be addressed soon
- 🟡 **Medium**: Nice to have, can wait
- 🟢 **Low**: Future consideration, low priority

## Story Points Guide (Fibonacci)

- **1 Point**: Trivial task, < 1 hour
- **2 Points**: Simple task, 1-4 hours
- **3 Points**: Small task, 4-8 hours
- **5 Points**: Medium task, 1-2 days
- **8 Points**: Large task, 2-3 days
- **13 Points**: Very large task, 3-5 days (consider breaking down)

---

## Template Validation Checklist

Before submitting, ensure:

- [ ] All required fields are filled (Status, Priority, Story Points, Dates)
- [ ] User story follows "As a... I want... So that..." format
- [ ] At least 3 acceptance criteria are defined
- [ ] Acceptance criteria are specific and testable
- [ ] Business value is clearly documented
- [ ] Technical requirements are specified (if applicable)
- [ ] Dependencies are identified (if any)
- [ ] Story points are estimated using Fibonacci sequence
- [ ] Priority is assigned based on business value and urgency
- [ ] Technical references are included (if applicable)
- [ ] Links to related documents are correct
- [ ] File is saved with correct naming convention: `US-XXX-feature-name.md`
- [ ] Entry is added to product backlog table
- [ ] Any charts/diagrams use **Mermaid** (see [documentation-standards.md](../processes/documentation-standards.md))
- [ ] Mermaid diagrams validate (wrap labels with `/`, `=`, `:`, etc. in double quotes; test at [mermaid.live](https://mermaid.live/))

