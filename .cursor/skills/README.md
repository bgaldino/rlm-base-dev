# AI Agent Skills — Discovery Index

These skills are **plain markdown files** usable by any AI agent (Cursor,
Claude Code, GitHub Copilot, Codex, Windsurf, Aider, or any tool that
can read files). They live under `.cursor/skills/` for historical
reasons but have no Cursor-specific dependencies.

For the full project rules and safety guards, read `AGENTS.md` at the
repo root.

## Skill Router

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Add new code, features, metadata | Repository Integration | `repo-integration/SKILL.md` |
| Work with CCI tasks, flows, or CLI | CCI Orchestration | `cci-orchestration/SKILL.md` |
| Wire pricing recipes, procedures, or lookup table mappings | Pricing Wiring | `pricing-wiring/SKILL.md` |
| Run build harness profiles/resume/report | Build Harness | `build-harness/SKILL.md` |
| Write a Python CCI task class | Custom Task Authoring | `cci-orchestration/custom-task-authoring.md` |
| Create/modify SFDMU data plans | SFDMU Data Plans | `sfdmu-data-plans/SKILL.md` |
| Understand RLM objects/relationships | Revenue Cloud Data Model | `revenue-cloud-data-model/SKILL.md` |
| Validate / refresh / certify the ERD against orgs and Core source | Schema Validation | `schema-validation/SKILL.md` |
| Cross-repo skill manifest (PMOS ↔ Foundations) | PMOS Integration | `pmos-integration/SKILL.md` |
| Use Revenue Cloud REST APIs | Business APIs | `rlm-business-apis/SKILL.md` |
| Write Robot Framework tests | Robot Testing | `robot-testing/SKILL.md` |
| Capture/apply UX drift from org | UX Assembly & Retrieve | `repo-integration/ux-assembly-retrieve.md` |
| Review docs before merge | Doc Consistency | `doc-consistency/SKILL.md` |
| Create, update, register, or test AI-agent skills | Skill Authoring | `skill-authoring/SKILL.md` |
| Debug a build/deploy failure | Troubleshooting | `troubleshooting/SKILL.md` |
| Harden Apex CRUD/FLS (USER_MODE) + permission-set self-sufficiency | Apex Security Hardening | `apex-security-hardening/SKILL.md` |
| Process PR reviews / run the pre-merge audit (completeness sweeps) | Audit Review | `audit-review/SKILL.md` |
| Author/update enablement exercises | Release Enablement | `release-enablement/SKILL.md` |
| Generate the QuantumBit demo-script canvas (per-release) | QB Demo Script Generator | `qb-demo-script/SKILL.md` |
| Ground claims against Salesforce Help | Revenue Cloud Docs | `revenue-cloud-docs/SKILL.md` |

## How Skills Are Structured

Each top-level skill should include the sections below. **Quick Rules** is
present in every skill today and **DO NOT** in most; **Entry Conditions**,
**Examples**, and **Validation Checks** are the target structure for new skills,
and existing skills are being migrated to add them incrementally:
1. **Quick Rules** — 5-8 numbered rules at the top for fast reference
2. **DO NOT** — explicit safety constraints for that topic
3. **Entry Conditions** — when to read the skill and when to use adjacent guidance
4. **Main content** — tables, code examples, decision guides
5. **Examples** — concrete usage patterns
6. **Validation Checks** — commands and review checks to run before commit/PR
7. **Sub-files** — detailed reference split into separate files (read on demand)

For the full lifecycle checklist, read `skill-authoring/SKILL.md`.

## File-Specific Rules (Cursor Only)

Rules in `.cursor/rules/` auto-inject when Cursor edits matching files.
Non-Cursor agents can read these files directly or use the equivalent skill:

| Rule | Triggers On | Equivalent Skill |
|------|-------------|------------------|
| `sfdmu-export-json.mdc` | `**/export.json` | `sfdmu-data-plans/SKILL.md` |
| `sfdmu-csv-data.mdc` | `datasets/sfdmu/**/*.csv` | `sfdmu-data-plans/SKILL.md` |
| `cci-task-definitions.mdc` | `cumulusci.yml` | `cci-orchestration/SKILL.md` |
| `cci-python-tasks.mdc` | `tasks/**/*.py` | `cci-orchestration/custom-task-authoring.md` |
| `apex-scripts.mdc` | `scripts/apex/**/*.apex` | `troubleshooting/SKILL.md` |
| `ux-templates.mdc` | `templates/**` | `repo-integration/SKILL.md` |
| `robot-tests.mdc` | `robot/**/*.robot` | `robot-testing/SKILL.md` |
| `doc-review.mdc` | `cumulusci.yml`, `tasks/**/*.py`, `datasets/sfdmu/**/export.json`, `datasets/sfdmu/**/*.csv`, `robot/**/*.robot`, `.cursor/skills/**/*.md` | `doc-consistency/SKILL.md` |
