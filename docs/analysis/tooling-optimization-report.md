# Agent Tooling Optimization Report

> **Auto-generated** by `scripts/ai/analyze_agent_tooling.py report`.
> Do not edit manually — re-run the analyzer after changing agent docs,
> skills, rules, or the skill manifest.

## Summary

- Overall status: **PASS**
- Required files: **6/6** present
- Skills inventoried: **181** Markdown files under `.cursor/skills/`
- Cursor rules inventoried: **12** `.mdc` files under `.cursor/rules/`
- AGENTS.md skill references: **7** checked, **0** missing
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
- `.cursor/skills/advanced-approvals/SKILL.md`
- `.cursor/skills/advanced-approvals/actions-and-objects.md`
- `.cursor/skills/advanced-approvals/limitations.md`
- `.cursor/skills/advanced-approvals/matrix-modeling.md`
- `.cursor/skills/apex-security-hardening/SKILL.md`
- `.cursor/skills/asset-lifecycle-changes/SKILL.md`
- `.cursor/skills/asset-lifecycle-changes/change-policy-mapping.md`
- `.cursor/skills/asset-lifecycle-changes/verification.md`
- `.cursor/skills/audit-review/SKILL.md`
- `.cursor/skills/audit-review/external-review-briefing.md`
- `.cursor/skills/audit-review/merge-and-review-procedures.md`
- `.cursor/skills/billing-operations/SKILL.md`
- `.cursor/skills/billing-operations/accounting.md`
- `.cursor/skills/billing-operations/invoicing.md`
- `.cursor/skills/billing-operations/payments-and-credits.md`
- `.cursor/skills/billing-operations/tax.md`
- `.cursor/skills/billing-setup/SKILL.md`
- `.cursor/skills/billing-setup/measured-264.md`
- `.cursor/skills/billing-setup/shipped-billing.md`
- `.cursor/skills/build-harness/SKILL.md`
- `.cursor/skills/cci-orchestration/SKILL.md`
- `.cursor/skills/cci-orchestration/custom-task-authoring.md`
- `.cursor/skills/cci-orchestration/feature-flags.md`
- `.cursor/skills/cci-orchestration/flows-reference.md`
- `.cursor/skills/cci-orchestration/org-cleanup.md`
- `.cursor/skills/cci-orchestration/tasks-reference.md`
- `.cursor/skills/constraint-models/SKILL.md`
- `.cursor/skills/constraint-models/quantities-from-attributes.md`
- `.cursor/skills/context-service/SKILL.md`
- `.cursor/skills/context-service/authoring-and-lifecycle.md`
- `.cursor/skills/context-service/data-model-and-api.md`
- `.cursor/skills/context-service/runtime-and-persistence.md`
- `.cursor/skills/decision-tables/SKILL.md`
- `.cursor/skills/decision-tables/authoring-and-data-model.md`
- `.cursor/skills/decision-tables/lifecycle-and-refresh.md`
- `.cursor/skills/df-workshop-setup/SKILL.md`
- `.cursor/skills/doc-consistency/SKILL.md`
- `.cursor/skills/doc-consistency/erd-count-drift.md`
- `.cursor/skills/document-generation/SKILL.md`
- `.cursor/skills/document-generation/data-mapper-authoring.md`
- `.cursor/skills/document-generation/dynamic-images.md`
- `.cursor/skills/document-generation/extract-engine-reference.md`
- `.cursor/skills/dro-plans/SKILL.md`
- `.cursor/skills/dro-plans/authoring-and-deployment.md`
- `.cursor/skills/dro-plans/csv-and-sfdmu.md`
- `.cursor/skills/dro-plans/examples-and-grounding.md`
- `.cursor/skills/dro-plans/objects-and-relationships.md`
- `.cursor/skills/dro-plans/updates-and-runtime.md`
- `.cursor/skills/expression-sets/SKILL.md`
- `.cursor/skills/expression-sets/authoring-and-overlays.md`
- `.cursor/skills/expression-sets/metadata-vs-connect.md`
- `.cursor/skills/implementation-planning/SKILL.md`
- `.cursor/skills/implementation-planning/acceptance-chain.md`
- `.cursor/skills/implementation-planning/build-order.md`
- `.cursor/skills/implementation-planning/concept-map.md`
- `.cursor/skills/implementation-planning/knowledge-sources.md`
- `.cursor/skills/implementation-planning/plan-template.md`
- `.cursor/skills/implementation-planning/prediction-checks.md`
- `.cursor/skills/implementation-planning/session-orchestration.md`
- `.cursor/skills/inapp-framework/SKILL.md`
- `.cursor/skills/mcp-integration/SKILL.md`
- `.cursor/skills/odt-authoring/SKILL.md`
- `.cursor/skills/pde-org-build/SKILL.md`
- `.cursor/skills/pmos-integration/SKILL.md`
- `.cursor/skills/pricing-procedures/SKILL.md`
- `.cursor/skills/pricing-procedures/discovery-procedures.md`
- `.cursor/skills/pricing-procedures/elements/aggregate-price.md`
- `.cursor/skills/pricing-procedures/elements/assignment.md`
- `.cursor/skills/pricing-procedures/elements/attribute-adjustment-matrix.md`
- `.cursor/skills/pricing-procedures/elements/attribute-based-price.md`
- `.cursor/skills/pricing-procedures/elements/bundle-based-price.md`
- `.cursor/skills/pricing-procedures/elements/commitment-term-discount.md`
- `.cursor/skills/pricing-procedures/elements/decision-table-lookups.md`
- `.cursor/skills/pricing-procedures/elements/derived-price.md`
- `.cursor/skills/pricing-procedures/elements/discount-distribution-service.md`
- `.cursor/skills/pricing-procedures/elements/formula-based-pricing.md`
- `.cursor/skills/pricing-procedures/elements/list-group-and-list-operation.md`
- `.cursor/skills/pricing-procedures/elements/list-price.md`
- `.cursor/skills/pricing-procedures/elements/manual-discount.md`
- `.cursor/skills/pricing-procedures/elements/map-line-item.md`
- `.cursor/skills/pricing-procedures/elements/price-adjustment-matrix.md`
- `.cursor/skills/pricing-procedures/elements/price-propagation.md`
- `.cursor/skills/pricing-procedures/elements/price-revision-compound-uplift.md`
- `.cursor/skills/pricing-procedures/elements/price-revision.md`
- `.cursor/skills/pricing-procedures/elements/price-tracking.md`
- `.cursor/skills/pricing-procedures/elements/pricing-setting.md`
- `.cursor/skills/pricing-procedures/elements/promotion-execution.md`
- `.cursor/skills/pricing-procedures/elements/proration-and-subscription.md`
- `.cursor/skills/pricing-procedures/elements/root-answer-child-price.md`
- `.cursor/skills/pricing-procedures/elements/rounding-values.md`
- `.cursor/skills/pricing-procedures/elements/stop-pricing.md`
- `.cursor/skills/pricing-procedures/elements/volume-and-tier-discount.md`
- `.cursor/skills/pricing-procedures/operations-and-troubleshooting.md`
- `.cursor/skills/pricing-procedures/procedure-anatomy-and-ordering.md`
- `.cursor/skills/pricing-procedures/runtime-and-observability.md`
- `.cursor/skills/pricing-setup/SKILL.md`
- `.cursor/skills/pricing-setup/cost-books.md`
- `.cursor/skills/pricing-setup/import-export-and-bulk-data.md`
- `.cursor/skills/pricing-setup/org-enablement-and-permissions.md`
- `.cursor/skills/pricing-setup/price-adjustment-schedules.md`
- `.cursor/skills/pricing-setup/price-books.md`
- `.cursor/skills/pricing-setup/price-revision-policies.md`
- `.cursor/skills/pricing-setup/pricing-actions.md`
- `.cursor/skills/pricing-setup/pricing-recipes.md`
- `.cursor/skills/pricing-setup/proration-and-selling-models.md`
- `.cursor/skills/pricing-setup/scenarios/README.md`
- `.cursor/skills/pricing-setup/scenarios/cost-and-margin.md`
- `.cursor/skills/pricing-setup/scenarios/full-term-value.md`
- `.cursor/skills/pricing-setup/scenarios/lowest-price-across-price-books.md`
- `.cursor/skills/pricing-setup/scenarios/pricing-action-button.md`
- `.cursor/skills/pricing-setup/scenarios/sequential-discounts.md`
- `.cursor/skills/pricing-setup/scenarios/simple-pricing-procedure.md`
- `.cursor/skills/pricing-wiring/SKILL.md`
- `.cursor/skills/pricing-wiring/price-revision-cpi.md`
- `.cursor/skills/product-catalog-modeling/SKILL.md`
- `.cursor/skills/product-catalog-modeling/attributes-and-classifications.md`
- `.cursor/skills/product-catalog-modeling/bundles-and-cardinality.md`
- `.cursor/skills/product-catalog-modeling/catalogs-and-loading.md`
- `.cursor/skills/product-catalog-modeling/selling-models-and-lifecycle.md`
- `.cursor/skills/qb-demo-script/SKILL.md`
- `.cursor/skills/quote-negotiation-rounds/SKILL.md`
- `.cursor/skills/quote-negotiation-rounds/deep-clone.md`
- `.cursor/skills/quote-negotiation-rounds/internal-round.md`
- `.cursor/skills/ramped-quotes/SKILL.md`
- `.cursor/skills/ramped-quotes/bundle-children-lifecycle.md`
- `.cursor/skills/ramped-quotes/compound-uplift.md`
- `.cursor/skills/ramped-quotes/field-legality.md`
- `.cursor/skills/ramped-quotes/ui-group-ramp.md`
- `.cursor/skills/rate-management/SKILL.md`
- `.cursor/skills/rate-management/rating-procedures.md`
- `.cursor/skills/release-enablement/SKILL.md`
- `.cursor/skills/release-enablement/authoring-patterns.md`
- `.cursor/skills/release-enablement/resume-enablement-work.md`
- `.cursor/skills/renewal-asset-creation/SKILL.md`
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
- `.cursor/skills/rlm-business-apis/backdated-asset-lifecycle.md`
- `.cursor/skills/robot-testing/SKILL.md`
- `.cursor/skills/robot-testing/patterns.md`
- `.cursor/skills/robot-testing/setup-ui-shadow-dom.md`
- `.cursor/skills/salesforce-contracts/SKILL.md`
- `.cursor/skills/salesforce-contracts/content-and-migration.md`
- `.cursor/skills/salesforce-contracts/data-model-and-queries.md`
- `.cursor/skills/salesforce-contracts/setup-and-diagnostics.md`
- `.cursor/skills/schema-validation/SKILL.md`
- `.cursor/skills/schema-validation/release-data-plan-audit.md`
- `.cursor/skills/sfdmu-data-plans/SKILL.md`
- `.cursor/skills/sfdmu-data-plans/object-plan-mapping.md`
- `.cursor/skills/sfdmu-data-plans/plan-dependency-graph.md`
- `.cursor/skills/skill-authoring/SKILL.md`
- `.cursor/skills/todo-tracker/SKILL.md`
- `.cursor/skills/toolchain/SKILL.md`
- `.cursor/skills/toolchain/managed-workstations.md`
- `.cursor/skills/toolchain/verification-handoff.md`
- `.cursor/skills/toolchain/workstation-audit.md`
- `.cursor/skills/transaction-line-editor/SKILL.md`
- `.cursor/skills/transaction-line-editor/page-configuration.md`
- `.cursor/skills/transaction-line-editor/runtime-behavior.md`
- `.cursor/skills/troubleshooting/SKILL.md`
- `.cursor/skills/troubleshooting/large-deal-preprocess-reference.md`
- `.cursor/skills/txn-data-harness/SKILL.md`
- `.cursor/skills/usage-consumption/SKILL.md`
- `.cursor/skills/usage-consumption/building-usage-assets.md`
- `.cursor/skills/usage-consumption/usage-setup.md`
- `.cursor/skills/usage-consumption/verification.md`

## Cursor Rule Inventory

- `.cursor/rules/analysis-artifacts.mdc`
- `.cursor/rules/apex-classes.mdc`
- `.cursor/rules/apex-scripts.mdc`
- `.cursor/rules/cci-python-tasks.mdc`
- `.cursor/rules/cci-task-definitions.mdc`
- `.cursor/rules/context-plans.mdc`
- `.cursor/rules/doc-review.mdc`
- `.cursor/rules/lwc-components.mdc`
- `.cursor/rules/robot-tests.mdc`
- `.cursor/rules/sfdmu-csv-data.mdc`
- `.cursor/rules/sfdmu-export-json.mdc`
- `.cursor/rules/ux-templates.mdc`

## AGENTS.md Skill Reference Check

- ✅ `.cursor/skills/README.md`
- ✅ `.cursor/skills/audit-review/SKILL.md`
- ✅ `.cursor/skills/cci-orchestration/custom-task-authoring.md`
- ✅ `.cursor/skills/doc-consistency/SKILL.md`
- ✅ `.cursor/skills/repo-integration/ux-assembly-retrieve.md`
- ✅ `.cursor/skills/robot-testing/SKILL.md`
- ✅ `.cursor/skills/sfdmu-data-plans/SKILL.md`

## Cursor Rule Coverage

Each `.cursor/rules/*.mdc` is checked against the `.cursor/skills/README.md` File-Specific Rules table for an equivalent skill or an explicit stand-alone note. See `.agents/context/rule-skill-coverage.md` for the full coverage matrix and recommendations.

- ✅ `analysis-artifacts.mdc` — explicit stand-alone note
- ✅ `apex-classes.mdc` — explicit stand-alone note
- ✅ `apex-scripts.mdc` — mapped to `.cursor/skills/troubleshooting/SKILL.md`
- ✅ `cci-python-tasks.mdc` — mapped to `.cursor/skills/cci-orchestration/custom-task-authoring.md`
- ✅ `cci-task-definitions.mdc` — mapped to `.cursor/skills/cci-orchestration/SKILL.md`
- ✅ `context-plans.mdc` — mapped to `.cursor/skills/context-service/SKILL.md`
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
- Last verified: `2026-10-22`
- Manifest skill count: **47**
  - `advanced-approvals`
  - `apex-security-hardening`
  - `asset-lifecycle-changes`
  - `audit-review`
  - `billing-operations`
  - `billing-setup`
  - `build-harness`
  - `cci-orchestration`
  - `constraint-models`
  - `context-service`
  - `decision-tables`
  - `df-workshop-setup`
  - `doc-consistency`
  - `document-generation`
  - `dro-plans`
  - `expression-sets`
  - `implementation-planning`
  - `inapp-framework`
  - `mcp-integration`
  - `odt-authoring`
  - `pde-org-build`
  - `pmos-integration`
  - `pricing-procedures`
  - `pricing-setup`
  - `pricing-wiring`
  - `product-catalog-modeling`
  - `qb-demo-script`
  - `quote-negotiation-rounds`
  - `ramped-quotes`
  - `rate-management`
  - `release-enablement`
  - `renewal-asset-creation`
  - `repo-integration`
  - `revenue-cloud-data-model`
  - `revenue-cloud-docs`
  - `rlm-business-apis`
  - `robot-testing`
  - `salesforce-contracts`
  - `schema-validation`
  - `sfdmu-data-plans`
  - `skill-authoring`
  - `todo-tracker`
  - `toolchain`
  - `transaction-line-editor`
  - `troubleshooting`
  - `txn-data-harness`
  - `usage-consumption`

## Findings

- ✅ No blocking errors found.

## Notes

- Generated by `scripts/ai/analyze_agent_tooling.py report`.
- `report` needs no third-party dependencies. It parses the skill manifest with PyYAML when installed, otherwise with a line-oriented fallback that gives the same summary for the current manifest.
