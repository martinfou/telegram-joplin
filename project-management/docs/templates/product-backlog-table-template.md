---
template_version: 1.1.0
last_updated: 2025-01-27
compatible_with: [feature-request, defect-fix, sprint-planning]
requires: [markdown-support]
---

# Product Backlog Table Template

This template provides the structure for your main product backlog tracking table. This table provides a high-level overview of all feature requests and defect fixes.

## Usage

1. Copy this template to create your `product-backlog.md` file
2. Update the table as items are added, modified, or completed
3. Keep the table sorted by priority (Critical → High → Medium → Low)
4. Update "Last Updated" date when making changes

---

# Product Backlog

This is the main product backlog tracking all feature requests and defect fixes.

**Last Updated**: [YYYY-MM-DD]

## Feature Requests

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| [US-001](user-stories/US-001-feature-name.md) | [Feature Title] | 🔴 Critical | [X] | ⭕ | - | [YYYY-MM-DD] | [YYYY-MM-DD] |
| [US-002](user-stories/US-002-feature-name.md) | [Feature Title] | 🟠 High | [X] | ⏳ | Sprint 1 | [YYYY-MM-DD] | [YYYY-MM-DD] |
| [US-003](user-stories/US-003-feature-name.md) | [Feature Title] | 🟡 Medium | [X] | ✅ | Sprint 1 | [YYYY-MM-DD] | [YYYY-MM-DD] |

## Bug Fixes

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| [DEF-001](defects/DEF-001-defect-description.md) | [Defect description] | 🔴 Critical | [X] | ⭕ | - | [YYYY-MM-DD] | [YYYY-MM-DD] |
| [DEF-002](defects/DEF-002-defect-description.md) | [Defect description] | 🟠 High | [X] | ⏳ | Sprint 1 | [YYYY-MM-DD] | [YYYY-MM-DD] |
| [DEF-003](defects/DEF-003-defect-description.md) | [Defect description] | 🟡 Medium | [X] | ✅ | Sprint 1 | [YYYY-MM-DD] | [YYYY-MM-DD] |

---

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
  - Link to detailed item: `[US-001](user-stories/US-001-feature-name.md)`
- **Title**: Short, descriptive title (50 characters or less recommended)
- **Priority**: Visual priority indicator (🔴 🟠 🟡 🟢)
- **Points**: Story points (Fibonacci: 1, 2, 3, 5, 8, 13)
- **Status**: Current status (⭕ ⏳ ✅)
- **Sprint**: Assigned sprint number or "-" if not assigned
- **Created**: Date when item was created (YYYY-MM-DD)
- **Updated**: Date when item was last updated (YYYY-MM-DD)

## Notes

- Feature request details: See `user-stories/US-XXX-*.md` files
- Defect fix details: See `defects/DEF-XXX-*.md` files
- Sprint assignments: See `../sprints/sprint-XX-*.md` files (if using sprint planning)

## Backlog Statistics (Optional)

**Total Items**: [X]  
**By Status**:
- ⭕ Not Started: [X]
- ⏳ In Progress: [X]
- ✅ Completed: [X]

**By Priority**:
- 🔴 Critical: [X]
- 🟠 High: [X]
- 🟡 Medium: [X]
- 🟢 Low: [X]

**Total Story Points**: [X]

---

## Tips for Maintaining the Backlog

1. **Keep it Updated**: Update status and dates when items change
2. **Sort by Priority**: Keep Critical items at top of each section
3. **Link to Details**: Always link IDs to detailed markdown files
4. **Regular Review**: Review and refine backlog regularly (weekly/bi-weekly)
5. **Update Dates**: Keep "Created" and "Updated" dates current
6. **Clear Titles**: Use descriptive, concise titles (update if needed as understanding evolves)

## Example Table Entry

| ID | Title | Priority | Points | Status | Sprint | Created | Updated |
|----|-------|----------|--------|--------|--------|---------|---------|
| [US-042](user-stories/US-042-user-authentication.md) | User Authentication | 🟠 High | 13 | ⏳ | Sprint 5 | 2024-01-10 | 2024-01-15 |

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

