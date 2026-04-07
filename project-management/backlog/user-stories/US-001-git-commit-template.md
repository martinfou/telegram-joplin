---
template_version: 1.1.0
last_updated: 2026-01-01
compatible_with: [defect-fix, sprint-planning, product-backlog]
requires: [markdown-support]
---

# User Story: US-001 - Add Git Commit Message Template

**Status**: ✅ Completed  
**Priority**: 🟠 High  
**Story Points**: 5 (Fibonacci: 1, 2, 3, 5, 8, 13)  
**Created**: 2026-01-01  
**Updated**: 2026-01-01  
**Assigned Sprint**: Sprint 1

## Description

Add a comprehensive git commit message template with examples to standardize commit messages across the project. This template will help ensure all commits follow a consistent format that combines business context with technical details, making commit history more meaningful for both business and technical stakeholders.

## User Story

As a developer working on this project, I want a standardized git commit message template, so that all commits follow a consistent format that links to backlog items, clearly describes business value, and provides technical details for other developers.

## Acceptance Criteria

- [x] Git commit message template created (markdown format with guidelines)
- [x] Git commit message template created (text format for direct git integration)
- [x] Git commit message examples document created with multiple scenarios
- [x] Template includes task number format (US-XXX or DEF-XXX)
- [x] Template includes business description section
- [x] Template includes technical changes section
- [x] Template documented in template-catalog.md
- [x] Examples demonstrate proper usage for features, bugs, and small changes
- [x] Changelog updated to reflect new templates

## Business Value

This feature improves project maintainability and traceability by:
- Ensuring all commits link back to backlog items (FR-XXX, BF-XXX)
- Making commit history readable for both business and technical stakeholders
- Providing clear context about what changed and why
- Enabling better project tracking and reporting
- Establishing best practices for the team from the start

## Technical Requirements

- Create `git-commit-template.md` with structured format guidelines
- Create `git-commit-template.txt` for direct git integration (commented format)
- Create `git-commit-example.md` with multiple usage examples
- Update `template-catalog.md` to include new template
- Update `changelog.md` to document the addition
- Ensure templates follow existing template structure with metadata headers
- Include validation checklist in template documentation

## Reference Documents

- Git Commit Template: `templates/git-commit-template.md`
- Git Commit Examples: `examples/git-commit-example.md`
- Template Catalog: `template-catalog.md`
- Changelog: `changelog.md`

## Technical References

- Template file: `backlog-toolkit/templates/git-commit-template.md`
- Template file (txt): `backlog-toolkit/templates/git-commit-template.txt`
- Example file: `backlog-toolkit/examples/git-commit-example.md`
- Product backlog: `backlog-toolkit/project-management/backlog/product-backlog.md`

## Dependencies

- None - This is the first feature request and establishes the foundation for future commits

## Notes

- This is the first feature request (US-001) for the backlog toolkit project
- The template format combines business context with technical details
- Template supports both detailed and simplified commit message formats
- Examples cover various scenarios: features, bugs, refactoring, documentation
- Template integrates with backlog management by requiring task numbers

## History

- 2026-01-01 - Created
- 2026-01-01 - Status changed to ⏳ In Progress
- 2026-01-01 - Assigned to Sprint 1
- 2026-01-01 - Status changed to ✅ Completed

