# Reference Documentation

This directory contains reference materials for backlog management.

## Contents

### Templates (`templates/`)

Template files for creating backlog items:

- **feature-request-template.md** - For new features and enhancements
- **bug-fix-template.md** - For defect reports and fixes
- **sprint-planning-template.md** - For sprint planning
- **product-backlog-table-template.md** - For the main backlog table

**Usage:**
1. Copy the appropriate template
2. Fill in all sections
3. Save to the appropriate directory (`backlog/user-stories/` or `backlog/defects/`)
4. Add entry to `backlog/product-backlog.md`

### Definition of Done (`definition-of-done.md`)

Quality gate for completed work. Includes Documentation-Code Consistency Review requirement. See [Definition of Done](definition-of-done.md).

### Processes (`processes/`)

Process documentation explaining workflows:

- **pre-commit-checklist.md** - **Run lint, mypy, and tests before every commit**
- **release-notes-process.md** - How to create and update RELEASE_NOTES.md
- **backlog-management-process.md** - How to manage the backlog
- **product-backlog-structure.md** - Backlog structure and conventions
- **documentation-standards.md** - Use Mermaid for charts and graphs
- **documentation-code-consistency-problems.md** - Taxonomy of 16 doc/code problem categories (for US-036)

**Usage:**
- Reference when learning the process
- Review during backlog refinement
- Share with new team members

## Quick Reference

### Before Every Commit
Run **lint, mypy, and tests** before committing. See [Pre-Commit Checklist](processes/pre-commit-checklist.md).

### Creating a Feature Request

```bash
cp docs/templates/feature-request-template.md backlog/user-stories/US-001-feature-name.md
# Edit US-001-feature-name.md
# Add entry to backlog/product-backlog.md
```

### Creating a Bug Fix

```bash
cp docs/templates/bug-fix-template.md backlog/defects/DEF-001-defect-description.md
# Edit DEF-001-defect-description.md
# Add entry to backlog/product-backlog.md
```

### Planning a Sprint

1. **Before planning**: Run Documentation-Code Consistency Review: `./scripts/doc-code-review.sh`
2. Review report at `project-management/reports/doc-code-consistency-latest.md`
3. Create sprint document:

```bash
cp docs/templates/sprint-planning-template.md sprints/sprint-01-sprint-name.md
# Edit sprint-01-sprint-name.md
# Add user stories from backlog
```

## File Naming Conventions

- **User Stories**: `US-XXX-feature-name.md` (e.g., `US-042-user-authentication.md`)
- **Defects**: `DEF-XXX-defect-description.md` (e.g., `DEF-015-email-validation.md`)
- **Sprints**: `sprint-XX-sprint-name.md` (e.g., `sprint-05-user-auth.md`)

Use kebab-case (lowercase with hyphens) for names.

## Best Practices

1. **Always use templates** - Don't create files from scratch
2. **Fill all sections** - Complete templates ensure consistency
3. **Update regularly** - Keep status and dates current
4. **Link properly** - Use correct relative paths in links
5. **Follow naming** - Use consistent ID formats and naming
6. **Use Mermaid for charts and graphs** - Never ASCII art or images for flowcharts, sequences, or architecture. See [Documentation Standards](processes/documentation-standards.md).

---

For more help, see the main backlog toolkit documentation.
