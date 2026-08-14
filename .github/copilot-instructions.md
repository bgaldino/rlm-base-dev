# Copilot Instructions — Revenue Cloud Base Foundations

This repository uses `AGENTS.md` (at the repo root) as the canonical
AI agent instructions file. Read it for:

- Project overview and technology stack
- Safety-critical DO NOT rules
- SFDMU v5 compliance rules
- Org identity (CCI vs SF CLI aliases)
- Common workflows and PR review checklist
- Skill index with detailed guides for every task type

## Quick Start

1. Read `AGENTS.md` at the repo root
2. Find the relevant skill in the Skill Index section
3. Read that skill's `SKILL.md` for detailed guidance
4. When creating, updating, registering, or testing skills, read `.cursor/skills/skill-authoring/SKILL.md`
5. For a focused topic, use the skill's **sub-files** — each `SKILL.md` lists its own, which is the only registry (`AGENTS.md` carries no second-level index). E.g. Robot setup UI + shadow DOM (`.cursor/skills/robot-testing/setup-ui-shadow-dom.md`), UX assembly vs retrieve (`.cursor/skills/repo-integration/ux-assembly-retrieve.md`)
6. Before a PR: follow **Pre-merge checklists for AI agents** in `AGENTS.md` (SFDMU, `cumulusci.yml`, merge diffs)

## Reviewing a pull request

Read **`REVIEW.md`** at the repo root — severity rubric, what to look for, the defect
classes this repository actually produces, and push discipline. Its governing rule:
**only report findings that are real problems; if there are none, say so and return
nothing.** An empty review on a clean diff is a correct review.

## Entry Points

| File | Purpose |
|------|---------|
| `AGENTS.md` | Canonical AI agent instructions |
| `REVIEW.md` | How pull requests get reviewed: severity rubric, defect classes, push discipline |
| `.cursor/skills/*/SKILL.md` | Detailed per-topic guides (plain markdown) |
| `.cursor/rules/*.mdc` | Cursor-specific auto-injection rules |
| `scripts/ai/` | AI utility scripts (ERD query, CCI reference generator) |
