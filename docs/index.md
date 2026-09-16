# Documentation

[Home](../README.md) · [Skill catalog](../.cursor/skills/README.md)

## Start here

| Goal | Guide |
|---|---|
| Use a coding agent with this repository | [Skills quick start](../README.md#start-with-a-skill) |
| Enable native skill discovery or use the catalog fallback | [Agent skill discovery](guides/agent-skill-discovery.md) |
| Install tools and connect an org | [Local installation](guides/local-installation.md) |
| Use the container or a devcontainer | [Docker environment](../docker/README.md) |
| Build, configure or troubleshoot an org | [Org operations](guides/org-operations.md) |
| Understand the environment build | [Build process](guides/prepare-rlm-org-build-guide.md) |
| Browse or validate datasets | [Data plans](guides/data-plans.md) |
| Find source files and generated outputs | [Repository layout](references/repository-layout.md) |

## CumulusCI references

These references are generated from `cumulusci.yml`; use them for task options,
flow ordering and feature-flag conditions.

- [Tasks](../.cursor/skills/cci-orchestration/tasks-reference.md)
- [Flows](../.cursor/skills/cci-orchestration/flows-reference.md)
- [Feature flags](../.cursor/skills/cci-orchestration/feature-flags.md)
- [Authoring custom tasks](../.cursor/skills/cci-orchestration/custom-task-authoring.md)

## Primary Guides

| Document | Description |
|----------|-------------|
| [Dev Environment Setup](guides/dev-environment-setup.md) | Canonical local toolchain architecture — shell config layout, direnv `.envrc` per-project pinning, major-line update strategy, replication on new workstations |
| [Constraints Utility Guide](../datasets/constraints/README.md) | CML constraint model export, import, validate -- architecture, workflows, polymorphic resolution |
| [Constraints Setup](guides/constraints-setup.md) | `prepare_constraints` flow order, feature flags, deployment phases |
| [CumulusCI Tasks Reference](../.cursor/skills/cci-orchestration/tasks-reference.md) | Generated CCI task reference; flow and feature flag references live alongside it |
| [Decision Table Examples](references/decision-table-examples.md) | Comprehensive examples for Decision Table management tasks |
| [Decision Table API Reference](references/decision-table-api-reference.md) | Programmatic management of Decision Table definitions and data |
| [Expression Set API Reference](references/expression-set-connect-api-reference.md) | Setup and administration of Expression Sets and pricing procedures |
| [Revenue Cloud Permissions](references/revenue-cloud-permissions.md) | Permission set licenses, groups, feature flags, and assignment order |
| [Task Examples](references/task-examples.md) | Examples for Flow and Expression Set management tasks |
| [Context Service Utility](references/context-service-utility.md) | Context Service utility usage and plan examples |
| [Context Service PATCH Shapes](references/context-service-patch-shapes.md) | Reference for the Context Service Connect/SObject PATCH request shapes (node mapping, attribute, transient, default-mapping) used by the standalone toolkit |
| [DocGen Setup](guides/docgen-setup.md) | Document Generation architecture, deployment flow, Metadata API binary bug, seller token implementation |
| [Transaction Data Harness](guides/txn-data-harness.md) | Standalone tool that mints high-volume demo data (Quotes → Orders → Posted Invoices) by driving the real transaction lifecycle; usage, verification, cleanup |
| [Usage & Consumption Runbook](guides/usage-consumption-runbook.md) | Step-by-step: build a backdated asset, record usage, orchestrate, verify, reset — plus a symptom→cause table for when a consumption demo misbehaves |
| [QB Consumption Demo Scenarios](guides/qb-consumption-demo-scenarios.md) | Nine usage/consumption demo scenarios (1–8 historically verified on Release 262; scenario 6 requires re-verification with current grant sizes; 9 platform-blocked), with worked arithmetic and execution-order guidance |
| [Post-Billing Portal](guides/post-billing-portal.md) | Billing portal module setup and deployment |
| [Prepare RLM Org Build Guide](guides/prepare-rlm-org-build-guide.md) | Walkthrough of the `prepare_rlm_org` flow steps |
| [CCI / SF CLI Token Workaround](guides/cci-sf-cli-token-workaround.md) | `INVALID_AUTH_HEADER` on a healthy scratch org — cause and workaround |
| [Build Harness](guides/build-harness.md) | Build harness profiles, resume, and reporting |

## Analysis & Planning

| Document | Description |
|----------|-------------|
| [Composite Key Optimizations](references/sfdmu-composite-key-optimizations.md) | SFDMU v5 migration, composite key analysis, idempotency verification |

## SFDMU Data Plan READMEs

Each SFDMU data plan has its own detailed README documenting objects, fields, load order, external IDs, and optimization opportunities:

- [qb-pcm README](../datasets/sfdmu/qb/en-US/qb-pcm/README.md) -- Product Catalog Management
- [qb-product-images README](../datasets/sfdmu/qb/en-US/qb-product-images/README.md) -- Product Images
- [qb-pricing README](../datasets/sfdmu/qb/en-US/qb-pricing/README.md) -- Pricing
- [qb-tax README](../datasets/sfdmu/qb/en-US/qb-tax/README.md) -- Tax
- [qb-billing README](../datasets/sfdmu/qb/en-US/qb-billing/README.md) -- Billing
- [qb-dro README](../datasets/sfdmu/qb/en-US/qb-dro/README.md) -- Dynamic Revenue Orchestration
- [qb-transactionprocessingtypes README](../datasets/sfdmu/qb/en-US/qb-transactionprocessingtypes/README.md) -- Transaction Processing Types
- [qb-rating README](../datasets/sfdmu/qb/en-US/qb-rating/README.md) -- Rating
- [qb-rates README](../datasets/sfdmu/qb/en-US/qb-rates/README.md) -- Rates
- [qb-prm README](../datasets/sfdmu/qb/en-US/qb-prm/README.md) -- Partner Relationship Management
- [qb-prm-pricing README](../datasets/sfdmu/qb/en-US/qb-prm-pricing/README.md) -- PRM Pricing Overlay
- [qb-accounting README](../datasets/sfdmu/qb/en-US/qb-accounting/README.md) -- General ledger and billing accounting reference data (not wired into CCI)
- [qb-approvals README](../datasets/sfdmu/qb/en-US/qb-approvals/README.md) -- Advanced Approvals notification records
- [qb-clm README](../datasets/sfdmu/qb/en-US/qb-clm/README.md) -- Contract clauses and lifecycle state definitions
- [qb-guidedselling-products README](../datasets/sfdmu/qb/en-US/qb-guidedselling-products/README.md) -- Guided-selling attributes for existing products
- [procedure-plans README](../datasets/sfdmu/procedure-plans/README.md) -- Procedure Plans
- [mfg README](../datasets/sfdmu/mfg/README.md) -- Manufacturing data shape (add plans under mfg/en-US/; same patterns as qb)

## Features

| Document | Description |
|----------|-------------|
| [Composable Quote Approvals](features/composable-quote-approvals.md) | QuantumBit approval workflow and approval chains |
| [Dynamic UX Assembly](features/dynamic-ux-assembly.md) | UX templates, feature patches, and metadata assembly |
| [E2E Test Framework](features/e2e-test-framework.md) | End-to-end UI tests, shadow DOM handling, and debugging |
| [Git Commit Stamping](features/git-commit-stamping.md) | Build provenance recorded in Salesforce orgs |
| [Headless Configurator Context Plan](features/headless-configurator-context-plan.md) | Context-mapping setup plan and its recorded validation status |

## Robot Framework

- [Robot Setup README](../robot/rlm-base/tests/setup/README.md) -- Browser automation for setup page toggles and picklists (Document Builder, Constraints Settings, Revenue Settings, Pricing Setup, Product Discovery, Timeline)
- [E2E Test Framework](features/e2e-test-framework.md) -- End-to-end UI tests (Quote-to-Order flow), shadow DOM architecture, and debugging guide

## Configuration Files

- **`cumulusci.yml`** -- Main CumulusCI configuration with all tasks, flows, and project settings
- **`sfdx-project.json`** -- Salesforce DX project configuration
- **`orgs/`** -- Scratch org definition files for different scenarios

## Release context

`main` is now the Release 264 (Winter '27, API v68.0) line, promoted from the `264` branch (the two are in sync). 264 is preview / pre-GA. The `262` branch carries remaining Release 262 (Summer '26, API v67.0) patches through 262 GA, and `release/262` is the frozen 262 GA reference.

Use the checked-in Winter '27 references below for Release 264. Verify behavior against a live 264 org where documentation and implementation disagree; an upgraded 262 org can retain settings and schema that a fresh 264 org lacks. Because the dev hub is on API 68.0, every scratch org it creates is a 264 org regardless of branch, and `main` (the 264 line) builds against it.

## Release 264 Salesforce references

- [Revenue Management Developer Guide — Winter '27 snapshot](salesforce/264/dev-guide/index.md)
- [Salesforce Help — Winter '27 snapshot](salesforce/264/help/index.md)

These are checked-in snapshots, not continuously updated documentation. Each index records its capture date, coverage, and capture errors.

## Additional Resources

- [CumulusCI Documentation](https://cumulusci.readthedocs.io/)
- [Salesforce CLI Documentation](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/)
- [SFDMU Documentation](https://help.sfdmu.com/)
- [Revenue Cloud Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm) (latest online version; not pinned to 264)
- [Revenue Cloud Developer Guide (Release 260)](https://developer.salesforce.com/docs/atlas.en-us.260.0.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rlm_get_started.htm) (historical reference)
- [Revenue Cloud Help Documentation](https://help.salesforce.com/s/articleView?id=ind.revenue_lifecycle_management_get_started.htm&type=5)
