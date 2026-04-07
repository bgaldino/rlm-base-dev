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
| Write a Python CCI task class | Custom Task Authoring | `cci-orchestration/custom-task-authoring.md` |
| Create/modify SFDMU data plans | SFDMU Data Plans | `sfdmu-data-plans/SKILL.md` |
| Understand RLM objects/relationships | Revenue Cloud Data Model | `revenue-cloud-data-model/SKILL.md` |
| Use Revenue Cloud REST APIs | Business APIs | `rlm-business-apis/SKILL.md` |
| Write Robot Framework tests | Robot Testing | `robot-testing/SKILL.md` |
| Set up Distill/Aegis integration workspace | Integration Testing | `integration-testing/SKILL.md` |
| Debug a build/deploy failure | Troubleshooting | `troubleshooting/SKILL.md` |

## How Skills Are Structured

Each skill has:
1. **Quick Rules** — 5-8 numbered rules at the top for fast reference
2. **DO NOT** — explicit safety constraints for that topic
3. **Main content** — tables, code examples, decision guides
4. **Sub-files** — detailed reference split into separate files (read on demand)

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
| `integration-docs.mdc` | `docs/integration/**`, `scripts/validate_integration_prereqs.sh` | `integration-testing/SKILL.md` |
