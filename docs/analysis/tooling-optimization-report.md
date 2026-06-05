# Agent Tooling Optimization Report

Generated: `2026-06-05T23:42:57Z`

## Summary

- Overall status: **PASS**
- Required files: **4/4** present
- Skills inventoried: **37** Markdown files under `.cursor/skills/`
- Cursor rules inventoried: **10** `.mdc` files under `.cursor/rules/`
- AGENTS.md skill references: **29** checked, **0** missing
- Generated CCI references: **3/3** present
- Errors: **0**
- Warnings: **0**

## Required Agent Entry Points

- ✅ `AGENTS.md` — Found AGENTS.md
- ✅ `.github/copilot-instructions.md` — Found .github/copilot-instructions.md
- ✅ `.claude/skill-manifest.yml` — Found .claude/skill-manifest.yml
- ✅ `.cursor/skills/README.md` — Found .cursor/skills/README.md

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

- ✅ `.cursor/skills/**/*.md`
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
- ✅ `.cursor/skills/revenue-cloud-data-model/domains/*.md`
- ✅ `.cursor/skills/revenue-cloud-docs/SKILL.md`
- ✅ `.cursor/skills/rlm-business-apis/SKILL.md`
- ✅ `.cursor/skills/robot-testing/SKILL.md`
- ✅ `.cursor/skills/robot-testing/patterns.md`
- ✅ `.cursor/skills/robot-testing/setup-ui-shadow-dom.md`
- ✅ `.cursor/skills/schema-validation/SKILL.md`
- ✅ `.cursor/skills/sfdmu-data-plans/SKILL.md`
- ✅ `.cursor/skills/sfdmu-data-plans/object-plan-mapping.md`
- ✅ `.cursor/skills/sfdmu-data-plans/plan-dependency-graph.md`
- ✅ `.cursor/skills/troubleshooting/SKILL.md`

## Cursor Rule Coverage

- ✅ `apex-classes.mdc` — has explicit stand-alone note (*(stand-alone — sharing keywords, `Id.valueOf` validation, SOQL safety, test patterns; complements `repo-integration/SKILL.md` for placement)*)
- ✅ `apex-scripts.mdc` — mapped to `.cursor/skills/troubleshooting/SKILL.md`
- ✅ `cci-python-tasks.mdc` — mapped to `.cursor/skills/cci-orchestration/custom-task-authoring.md`
- ✅ `cci-task-definitions.mdc` — mapped to `.cursor/skills/cci-orchestration/SKILL.md`
- ✅ `doc-review.mdc` — mapped to `.cursor/skills/doc-consistency/SKILL.md`
- ✅ `lwc-components.mdc` — has explicit stand-alone note (*(stand-alone — template syntax, ARIA/accessibility, performance, error messages; complements `repo-integration/SKILL.md` for placement)*)
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
- Parser: `line-oriented fallback`
- Manifest version: `2`
- Last verified: `2026-05-23`
- Active Salesforce release: `262`
- Manifest skill count: **20**
  - `cci-orchestration`
  - `check_pmos_prd`
  - `doc-consistency`
  - `mfg/en-US`
  - `pmos-integration`
  - `q3/en-US`
  - `qb-demo-script`
  - `qb/en-US`
  - `qb/ja`
  - `release-enablement`
  - `repo-integration`
  - `revenue-cloud-data-model`
  - `revenue-cloud-docs`
  - `rlm-business-apis`
  - `robot-testing`
  - `schema-validation`
  - `sfdmu-data-plans`
  - `snapshot_salesforce_help`
  - `troubleshooting`
  - `validate_setup`

## Findings

- ✅ No blocking errors found.

## Notes

- This report is generated by `scripts/ai/analyze_agent_tooling.py`.
- The analyzer intentionally avoids mandatory third-party dependencies. If PyYAML is installed, manifest reporting is richer; otherwise the line-oriented fallback is used.
