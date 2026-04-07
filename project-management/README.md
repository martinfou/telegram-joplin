# Project Management

This directory contains the backlog management structure for this project.

## Structure

```
project-management/
├── STATE.md             # Process state — where the AI is in the workflow (read/update when helping)
├── backlog/             # Active backlog items
│   ├── product-backlog.md    # Main backlog overview
│   ├── user-stories/         # User stories (US-XXX-*.md)
│   └── defects/               # Defects (DEF-XXX-*.md)
├── sprints/             # Sprint planning documents
│   └── sprint-XX-*.md
└── docs/                # Reference documentation
    ├── templates/       # Template files
    └── processes/       # Process documentation
```

### Process State (STATE.md)

[STATE.md](STATE.md) tracks which process the AI/user is in (release notes, backlog, sprint planning, pre-commit) and the current step. The AI reads this to provide contextually relevant guidance and updates it when moving between steps.

## Strict Structure Rules

- All user story files and implementation summaries stay under `backlog/user-stories/`.
- All sprint planning and sprint follow-up documents stay under `sprints/`.
- `docs/` at repository root is reserved for product/user/developer guides, not planning artifacts.

## Quick Start

1. **View the backlog**: Open `backlog/product-backlog.md`
2. **Create a user story**: Copy `docs/templates/feature-request-template.md` to `backlog/user-stories/US-XXX-name.md`
3. **Create a defect**: Copy `docs/templates/bug-fix-template.md` to `backlog/defects/DEF-XXX-name.md`
4. **Plan a sprint**: Copy `docs/templates/sprint-planning-template.md` to `sprints/sprint-XX-name.md`

## Workflow

### Before Commit and Push
- **Run lint, mypy, and tests *before* every commit** — not after. CI fails on lint, type, or test errors. See [Pre-Commit Checklist](docs/processes/pre-commit-checklist.md).

### Daily Work
- Update status in `backlog/product-backlog.md`
- Work on items in `backlog/user-stories/` or `backlog/defects/`

### Creating New Items
- Use templates from `docs/templates/`
- Add entry to `backlog/product-backlog.md`
- Follow naming: `US-XXX-feature-name.md` or `DEF-XXX-defect-slug.md`

### Sprint Planning
- Create sprint document in `sprints/`
- Reference backlog items
- Update backlog with sprint assignments

## Reference Materials

- **Templates**: See `docs/templates/` for creating new items
- **Processes**: See `docs/processes/` for workflow guidance
- **Documentation**: See `docs/README.md` for detailed reference guide
- **Documentation Standards**: Use **Mermaid** for charts and graphs — see [documentation-standards.md](docs/processes/documentation-standards.md)

## Status Values

- ⭕ **Not Started**: Item not yet started
- ⏳ **In Progress**: Item currently being worked on
- ✅ **Completed**: Item finished and verified

## Priority Levels

- 🔴 **Critical**: Must be fixed/implemented immediately
- 🟠 **High**: Should be addressed soon
- 🟡 **Medium**: Nice to have, can wait
- 🟢 **Low**: Future consideration

---

For more information, see the backlog toolkit documentation.
