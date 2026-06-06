# Agent Tooling Optimization Report

> **Auto-generated** by `scripts/ai/analyze_agent_tooling.py report`.
> Do not edit manually — re-run the analyzer after changing agent docs,
> skills, rules, or the skill manifest.

## Summary

- Overall status: **PASS**
- Required files: **6/6** present
- Skills inventoried: **38** Markdown files under `.cursor/skills/`
- Cursor rules inventoried: **10** `.mdc` files under `.cursor/rules/`
- AGENTS.md skill references: **28** checked, **0** missing
- Generated CCI references: **3/3** present
- Errors: **0**
- Warnings: **0**

## Required Agent Entry Points

- ✅ `AGENTS.md` — Found AGENTS.md
- ✅ `CLAUDE.md` — Found CLAUDE.md
- ✅ `.github/copilot-instructions.md` — Found .github/copilot-instructions.md
- ✅ `.claude/skill-manifest.yml` — Found .claude/skill-manifest.yml
- ✅ `.cursor/skills/README.md` — Found .cursor/skills/README.md
- ✅ `scripts/ai/README.md` — Found scripts/ai/README.md

## Skill Inventory

- `.cursor/skills/README.md`
- `.cursor/skills/cci-orchestration/SKILL.md`
- `.cursor/skills/cci-orchestration/custom-task-authoring.md`
- `.cursor/skills/cci-orchestration/feature-flags.md`
- `.cursor/skills/cci-orchestration/flows-reference.md`
- `.cursor/skills/cci-orchestration/tasks-reference.md`
- `.cursor/skills/doc-consistency/SKILL.md`
- `.cursor/skills/pmos-integration/SKILL.md`
- `.cursor/skills/qb-demo-script/SKILL.md`
- `.cursor/skills/release-enablement/SKILL.md`
- `.cursor/skills/release-enablement/authoring-patterns.md`
- `.cursor/skills/release-enablement/resume-enablement-work.md`
- `.cursor/skills/repo-integration/SKILL.md`
- `.cursor/skills/repo-integration/dependency-ordering.md`
- `.cursor/skills/repo-integration/new-feature-guide.md`
- `.cursor/skills/repo-integration/ux-assembly-retrieve.md`
- `.cursor/skills/revenue-cloud-data-model/SKILL.md`
- `.cursor/skills/revenue-cloud-data-model/cross-domain-relationships.md`
- `.cursor/skills/revenue-cloud-data-model/domains/approvals.md`
- `.cursor/skills/revenue-cloud-data-model/domains/billing.md`
- `.cursor/skills/revenue-cloud-data-model/domains/configurator.md`
- `.cursor/skills/revenue-cloud-data-model/domains/dro.md`
- `.cursor/skills/revenue-cloud-data-model/domains/pcm.md`
- `.cursor/skills/revenue-cloud-data-model/domains/pricing.md`
- `.cursor/skills/revenue-cloud-data-model/domains/rates.md`
- `.cursor/skills/revenue-cloud-data-model/domains/transactions.md`
- `.cursor/skills/revenue-cloud-data-model/domains/usage.md`
- `.cursor/skills/revenue-cloud-docs/SKILL.md`
- `.cursor/skills/rlm-business-apis/SKILL.md`
- `.cursor/skills/robot-testing/SKILL.md`
- `.cursor/skills/robot-testing/patterns.md`
- `.cursor/skills/robot-testing/setup-ui-shadow-dom.md`
- `.cursor/skills/schema-validation/SKILL.md`
- `.cursor/skills/sfdmu-data-plans/SKILL.md`
- `.cursor/skills/sfdmu-data-plans/object-plan-mapping.md`
- `.cursor/skills/sfdmu-data-plans/plan-dependency-graph.md`
- `.cursor/skills/skill-authoring/SKILL.md`
- `.cursor/skills/troubleshooting/SKILL.md`

## Cursor Rule Inventory

- `.cursor/rules/apex-classes.mdc`
- `.cursor/rules/apex-scripts.mdc`
- `.cursor/rules/cci-python-tasks.mdc`
- `.cursor/rules/cci-task-definitions.mdc`
- `.cursor/rules/doc-review.mdc`
- `.cursor/rules/lwc-components.mdc`
- `.cursor/rules/robot-tests.mdc`
- `.cursor/rules/sfdmu-csv-data.mdc`
- `.cursor/rules/sfdmu-export-json.mdc`
- `.cursor/rules/ux-templates.mdc`

## AGENTS.md Skill Reference Check

- ✅ `.cursor/skills/cci-orchestration/SKILL.md`
- ✅ `.cursor/skills/cci-orchestration/custom-task-authoring.md`
- ✅ `.cursor/skills/cci-orchestration/feature-flags.md`
- ✅ `.cursor/skills/cci-orchestration/flows-reference.md`
- ✅ `.cursor/skills/cci-orchestration/tasks-reference.md`
- ✅ `.cursor/skills/doc-consistency/SKILL.md`
- ✅ `.cursor/skills/pmos-integration/SKILL.md`
- ✅ `.cursor/skills/qb-demo-script/SKILL.md`
- ✅ `.cursor/skills/release-enablement/SKILL.md`
- ✅ `.cursor/skills/release-enablement/authoring-patterns.md`
- ✅ `.cursor/skills/release-enablement/resume-enablement-work.md`
- ✅ `.cursor/skills/repo-integration/SKILL.md`
- ✅ `.cursor/skills/repo-integration/dependency-ordering.md`
- ✅ `.cursor/skills/repo-integration/new-feature-guide.md`
- ✅ `.cursor/skills/repo-integration/ux-assembly-retrieve.md`
- ✅ `.cursor/skills/revenue-cloud-data-model/SKILL.md`
- ✅ `.cursor/skills/revenue-cloud-data-model/cross-domain-relationships.md`
- ✅ `.cursor/skills/revenue-cloud-docs/SKILL.md`
- ✅ `.cursor/skills/rlm-business-apis/SKILL.md`
- ✅ `.cursor/skills/robot-testing/SKILL.md`
- ✅ `.cursor/skills/robot-testing/patterns.md`
- ✅ `.cursor/skills/robot-testing/setup-ui-shadow-dom.md`
- ✅ `.cursor/skills/schema-validation/SKILL.md`
- ✅ `.cursor/skills/sfdmu-data-plans/SKILL.md`
- ✅ `.cursor/skills/sfdmu-data-plans/object-plan-mapping.md`
- ✅ `.cursor/skills/sfdmu-data-plans/plan-dependency-graph.md`
- ✅ `.cursor/skills/skill-authoring/SKILL.md`
- ✅ `.cursor/skills/troubleshooting/SKILL.md`

## Cursor Rule Coverage

Each `.cursor/rules/*.mdc` is checked against the AGENTS.md File-Specific Rules table for an equivalent skill or an explicit stand-alone note. See `.agents/context/rule-skill-coverage.md` for the full coverage matrix and recommendations.

- ✅ `apex-classes.mdc` — explicit stand-alone note
- ✅ `apex-scripts.mdc` — mapped to `.cursor/skills/troubleshooting/SKILL.md`
- ✅ `cci-python-tasks.mdc` — mapped to `.cursor/skills/cci-orchestration/custom-task-authoring.md`
- ✅ `cci-task-definitions.mdc` — mapped to `.cursor/skills/cci-orchestration/SKILL.md`
- ✅ `doc-review.mdc` — mapped to `.cursor/skills/doc-consistency/SKILL.md`
- ✅ `lwc-components.mdc` — explicit stand-alone note
- ✅ `robot-tests.mdc` — mapped to `.cursor/skills/robot-testing/SKILL.md`
- ✅ `sfdmu-csv-data.mdc` — mapped to `.cursor/skills/sfdmu-data-plans/SKILL.md`
- ✅ `sfdmu-export-json.mdc` — mapped to `.cursor/skills/sfdmu-data-plans/SKILL.md`
- ✅ `ux-templates.mdc` — mapped to `.cursor/skills/repo-integration/SKILL.md`

## Generated CCI Reference Files

- ✅ `.cursor/skills/cci-orchestration/tasks-reference.md` — Found .cursor/skills/cci-orchestration/tasks-reference.md
- ✅ `.cursor/skills/cci-orchestration/flows-reference.md` — Found .cursor/skills/cci-orchestration/flows-reference.md
- ✅ `.cursor/skills/cci-orchestration/feature-flags.md` — Found .cursor/skills/cci-orchestration/feature-flags.md

## Skill Manifest Snapshot

- Present: **True**
- Manifest version: `2`
- Last verified: `2026-05-23`
- Active Salesforce release: `262`
- Manifest skill count: **14**
  - `cci-orchestration`
  - `doc-consistency`
  - `pmos-integration`
  - `qb-demo-script`
  - `release-enablement`
  - `repo-integration`
  - `revenue-cloud-data-model`
  - `revenue-cloud-docs`
  - `rlm-business-apis`
  - `robot-testing`
  - `schema-validation`
  - `sfdmu-data-plans`
  - `skill-authoring`
  - `troubleshooting`

## Findings

- ✅ No blocking errors found.

## Notes

- Generated by `scripts/ai/analyze_agent_tooling.py report`.
- The analyzer needs no third-party dependencies. With PyYAML installed, manifest reporting is richer; otherwise a line-oriented fallback is used.
