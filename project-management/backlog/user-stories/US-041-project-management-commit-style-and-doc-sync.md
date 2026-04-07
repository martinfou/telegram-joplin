# User Story: US-041 - Project Management: Commit Style and Document Sync Sections

**Status**: ⭕ Not Started
**Priority**: 🟡 Medium
**Story Points**: 5
**Created**: 2026-03-06
**Updated**: 2026-03-06
**Assigned Sprint**: Backlog

## Description

Add two new sections to the project-management documentation:

1. **Commit Style** — A dedicated section documenting commit message conventions, format, and best practices. Currently the [git-commit-template](../../docs/templates/git-commit-template.md) exists but is not prominently surfaced in the main workflow. A clear "Commit Style" section will make conventions discoverable and consistent.

2. **Document Sync** — A section on how to keep **all** documentation in the repo in sync without error or contradiction. This covers: what to update when, cross-document consistency, avoiding stale or conflicting information, and practical workflows to prevent drift.

## User Story

As a contributor to the project,
I want clear guidance on commit style and how to keep documentation in sync,
so that I can follow conventions consistently and avoid introducing contradictions or outdated information.

## Acceptance Criteria

### Commit Style Section

- [ ] New process document: `docs/processes/commit-style.md`
- [ ] New section in `backlog-management-process.md` that references/summarizes commit style
- [ ] Documents commit message format: **full format required** for all commits (FR/BF prefix, imperative, 72 chars, body, technical bullets)
- [ ] Links to or summarizes the [git-commit-template](../../docs/templates/git-commit-template.md)
- [ ] Includes examples: good vs bad commit messages
- [ ] **Pre-commit hook** (pre-commit framework) validates commit format; blocks by default, `--no-verify` to bypass
- [ ] Referenced from `project-management/README.md` and/or `docs/README.md` in the workflow

### Document Sync Section

- [ ] New process document: `docs/processes/document-sync-guide.md`
- [ ] Scope: **all docs in the repo** (project-management, docs/, README, etc.)
- [ ] Explains **what to update when**:
  - When adding a feature/defect: backlog file + product-backlog.md
  - When starting work: status in both places, sprint assignment
  - When completing: status, dates, release notes
  - When changing code: which docs may need updates (README, feature specs, etc.)
- [ ] Explains **how to avoid contradictions**:
  - Single source of truth for key facts (e.g. command list, option counts)
  - Cross-check before committing: product-backlog vs individual FR/BF files
  - Run doc-code consistency review before sprint planning: `./scripts/doc-code-review.sh` (invokes `scripts/doc_code_review.py`)
- [ ] Provides **checklist or workflow** for common scenarios (new feature, defect fix, sprint completion)
- [ ] Links to US-036 (Documentation-Code Consistency Review) and Definition of Done
- [ ] Referenced from `project-management/README.md` and/or `docs/README.md`

### Integration

- [ ] `project-management/README.md` updated with links to both new sections in Workflow or Reference Materials
- [ ] `docs/README.md` updated to list the new process docs

## Business Value

- **Consistency**: Clear commit style reduces noise in git history and makes `git log` more useful
- **Quality**: Document sync guidance reduces stale docs, contradictions, and confusion
- **Onboarding**: New contributors have explicit guidance instead of inferring from templates
- **Alignment with US-036**: Document sync section complements the doc-code consistency review by explaining the human workflow

## Technical Requirements

### 1. Commit Style Document

Suggested structure:
- **Format**: Full format required for all commits—title line (FR/BF prefix, imperative, 72 chars), body, technical bullets
- **Examples**: Good and bad commit messages
- **References**: Link to git-commit-template.md
- **Pre-commit hook**: Use [pre-commit framework](https://pre-commit.com/) with `.pre-commit-config.yaml`; hook validates commit message format (FR/BF prefix, structure); blocks by default, `git commit --no-verify` to bypass

### 2. Document Sync Document

Suggested structure:
- **When to update**: Table or list mapping actions (add feature, complete defect, etc.) to files to update
- **Consistency rules**: e.g. "Status in product-backlog.md must match status in FR/BF file"
- **Checklist**: Pre-commit, pre-sprint, post-completion
- **Tools**: Reference `./scripts/doc-code-review.sh` (invokes `scripts/doc_code_review.py`), release notes script
- **Common pitfalls**: Stale sprint assignments, mismatched status, forgotten release notes

### 3. Placement

- **Commit style**: Separate file `docs/processes/commit-style.md` **and** new section in `backlog-management-process.md` (references/summarizes commit-style.md)
- **Document sync**: Separate file `docs/processes/document-sync-guide.md`
- Link both from `project-management/README.md` and `docs/README.md`

## Design Decisions (2026-03-06)

- **Commit enforcement**: Pre-commit hook (not CI-only)
- **Doc sync scope**: All docs in the repo
- **Commit style placement**: Separate file + section in backlog-management-process.md
- **Script reference**: Document both `./scripts/doc-code-review.sh` and that it invokes `doc_code_review.py`
- **Commit format**: Full format required for all commits (no one-line shortcut)
- **Pre-commit behavior**: Block by default; `--no-verify` to bypass
- **Pre-commit implementation**: pre-commit framework (industry standard, version-controlled, portable)

## Reference Documents

- [US-001: Git Commit Template](US-001-git-commit-template.md) — existing template (note: US-001 in backlog links to git-commit-template)
- [US-036: Documentation-Code Consistency Review](US-036-documentation-code-consistency-review.md)
- [Pre-Commit Checklist](../../docs/processes/pre-commit-checklist.md)
- [Backlog Management Process](../../docs/processes/backlog-management-process.md)
- [Release Notes Process](../../docs/processes/release-notes-process.md)
- [Definition of Done](../../docs/definition-of-done.md)

## Technical References

- `project-management/README.md` — main entry point, Workflow and Reference Materials sections
- `project-management/docs/README.md` — docs index
- `project-management/docs/templates/git-commit-template.md` — existing commit template
- `project-management/docs/processes/` — process documents
- `scripts/doc-code-review.sh` — consistency review (invokes `scripts/doc_code_review.py`)
- `pre-commit` framework + `.pre-commit-config.yaml` — commit message validation hook

## Dependencies

- None (can be implemented independently)
- US-036 provides the automation; this FR provides the human workflow documentation

## Notes

- US-001 added the git commit template; this FR adds a **process section** that surfaces and explains it
- Document sync is the human counterpart to US-036's automated consistency review
- Consider adding a "Documentation Maintenance" or "Keeping Docs Accurate" section to the main project-management README that links to both the sync guide and US-036

## History

- 2026-03-06 - Created
- 2026-03-06 - Design decisions: pre-commit hook, all docs scope, commit-style in separate file + backlog-management section, full format required
- 2026-03-06 - Story points 5; pre-commit framework; --no-verify bypass
