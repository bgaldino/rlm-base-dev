# AI Agent Skills — Discovery Index

These skills are **plain markdown files** usable by any AI agent (Cursor,
Claude Code, GitHub Copilot, Codex, Windsurf, Aider, or any tool that
can read files). They live under `.cursor/skills/` for historical
reasons but have no Cursor-specific dependencies.

## Start here

Read [AGENTS.md](../../AGENTS.md) for the shared safety rules, then choose a
capability below. Keep the full repository available: skills link to reference
material, scripts, metadata and datasets outside their own directories.

You can read the checked-in guides without an org connection. Running a tool or
changing an org requires the prerequisites and verification in the selected skill.
Private artifacts and PMOS are optional; neither is needed to use this catalog.

## Skill Router

[Knowledge and APIs](#knowledge-and-apis) ·
[Configuration and pricing](#product-configuration-and-pricing) ·
[Transactions and usage](#transactions-usage-and-documents) ·
[Environment builds](#environment-builds-and-data) ·
[Enablement](#demos-and-enablement) ·
[Repository maintenance](#repository-maintenance) ·
[Optional integrations](#optional-maintainer-integrations)

### Knowledge and APIs

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Understand RLM objects/relationships | Revenue Cloud Data Model | [revenue-cloud-data-model/SKILL.md](revenue-cloud-data-model/SKILL.md) |
| Use Revenue Cloud REST APIs | Business APIs | [rlm-business-apis/SKILL.md](rlm-business-apis/SKILL.md) |
| Ground claims against Salesforce Help | Revenue Cloud Docs | [revenue-cloud-docs/SKILL.md](revenue-cloud-docs/SKILL.md) |
| Set up, query, author, or troubleshoot Salesforce Contracts CLM | Salesforce Contracts | [salesforce-contracts/SKILL.md](salesforce-contracts/SKILL.md) |

### Product configuration and pricing

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Model a product catalog: product vs attribute vs component, bundles and cardinality, classifications, selling models, lifecycle flags, catalogs and categories | Product Catalog Modeling | [product-catalog-modeling/SKILL.md](product-catalog-modeling/SKILL.md) |
| Edit/ship/debug Constraint models (CML) — configurator bundle rules, `.ffxblob` | Constraint Models | [constraint-models/SKILL.md](constraint-models/SKILL.md) |
| Set up Salesforce Pricing in an org: enablement, permissions, price/cost books, adjustment schedules, recipes, proration, revision policies, pricing actions | Pricing Setup | [pricing-setup/SKILL.md](pricing-setup/SKILL.md) |
| Wire pricing recipes, procedures, or lookup table mappings | Pricing Wiring | [pricing-wiring/SKILL.md](pricing-wiring/SKILL.md) |
| Author/CRUD Expression Sets (Connect/Metadata API) and build step overlays | Expression Sets | [expression-sets/SKILL.md](expression-sets/SKILL.md) |
| Configure pricing elements (Aggregate Price, discounts, Price Revision, DDS, …), element ordering, and day-2 pricing-procedure operations | Pricing Procedures | [pricing-procedures/SKILL.md](pricing-procedures/SKILL.md) |
| Inspect/author/manage, refresh, diagnose, or verify decision tables | Decision Tables | [decision-tables/SKILL.md](decision-tables/SKILL.md) |
| Read/extend/apply/deploy/upgrade Context Definitions; inspect/validate context plans | Context Service | [context-service/SKILL.md](context-service/SKILL.md) |

### Transactions, usage and documents

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Design/create/load CSV/SFDMU DRO plans and maintain existing fulfillment configuration | DRO Plans | [dro-plans/SKILL.md](dro-plans/SKILL.md) |
| Model, build, run or verify **Advanced Approvals**: sign-off matrices, cumulative levels, chains, submit/review/recall, the shipped quote approval | Advanced Approvals | [advanced-approvals/SKILL.md](advanced-approvals/SKILL.md) |
| Configure or use the quote/order **line editor** (columns, Adjustment Type, groups, action buttons, Instant Pricing, auto-refresh, configure from a line, amendment lines) | Transaction Line Editor | [transaction-line-editor/SKILL.md](transaction-line-editor/SKILL.md) |
| Model **negotiation or bid rounds** as quote versions: deep clone a quote, what carries over, an internal-only round, per-round discounts and approvals, which round syncs and becomes the order | Quote Negotiation Rounds | [quote-negotiation-rounds/SKILL.md](quote-negotiation-rounds/SKILL.md) |
| Model and verify **amend, swap, cancel and renew** on sold assets: change policies, where prices and attributes land, credits, end-to-end tests | Asset Lifecycle Changes | [asset-lifecycle-changes/SKILL.md](asset-lifecycle-changes/SKILL.md) |
| Set up **billing**: billing frequency vs selling model, advance or arrears treatments, milestone billing for services, payment terms and the approval, what the repo's billing build ships | Billing Setup | [billing-setup/SKILL.md](billing-setup/SKILL.md) |
| Build / verify a multi-year group **ramp** quote + per-segment (compound) uplift | Ramped Quotes | [ramped-quotes/SKILL.md](ramped-quotes/SKILL.md) |
| Create renewal-ready assets across the 4 expiry windows + layer lifecycle event history | Renewal Asset Creation | [renewal-asset-creation/SKILL.md](renewal-asset-creation/SKILL.md) |
| Build, rate, and verify metered consumption demos | Usage & Consumption | [usage-consumption/SKILL.md](usage-consumption/SKILL.md) |
| Generate, inspect, continue, or verify transaction demo data | Transaction Data Harness | [txn-data-harness/SKILL.md](txn-data-harness/SKILL.md) |
| Author, debug, and validate OmniDataTransform (ODT) mappers | ODT Authoring | [odt-authoring/SKILL.md](odt-authoring/SKILL.md) |
| Create/modify `.docx` templates + DocumentTemplate lifecycle | Document Generation | [document-generation/SKILL.md](document-generation/SKILL.md) |

### Environment builds and data

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Add new code, features, metadata | Repository Integration | [repo-integration/SKILL.md](repo-integration/SKILL.md) |
| Work with CCI tasks/flows/CLI, or clean expired orgs and stale SF auth | CCI Orchestration | [cci-orchestration/SKILL.md](cci-orchestration/SKILL.md) |
| Write a Python CCI task class | Custom Task Authoring | [cci-orchestration/custom-task-authoring.md](cci-orchestration/custom-task-authoring.md) |
| Create/modify SFDMU data plans | SFDMU Data Plans | [sfdmu-data-plans/SKILL.md](sfdmu-data-plans/SKILL.md) |
| Run build harness profiles/resume/report | Build Harness | [build-harness/SKILL.md](build-harness/SKILL.md) |
| Set up, audit, update or verify the local dev toolchain (incl. managed workstations) | Toolchain | [toolchain/SKILL.md](toolchain/SKILL.md) |
| Build a PDE (or other org type) via runtime-only feature-flag overrides | PDE Org Build | [pde-org-build/SKILL.md](pde-org-build/SKILL.md) |
| Stand up / inspect / debug the MCP surface on an org (hosted + custom servers, ECA, proxy) | MCP Integration | [mcp-integration/SKILL.md](mcp-integration/SKILL.md) |
| Capture/apply UX drift from org | UX Assembly & Retrieve | [repo-integration/ux-assembly-retrieve.md](repo-integration/ux-assembly-retrieve.md) |
| Validate / refresh / certify the ERD against orgs and Core source | Schema Validation | [schema-validation/SKILL.md](schema-validation/SKILL.md) |
| Write Robot Framework tests | Robot Testing | [robot-testing/SKILL.md](robot-testing/SKILL.md) |
| Debug a build/deploy failure | Troubleshooting | [troubleshooting/SKILL.md](troubleshooting/SKILL.md) |
| Harden Apex CRUD/FLS (USER_MODE) + permission-set self-sufficiency | Apex Security Hardening | [apex-security-hardening/SKILL.md](apex-security-hardening/SKILL.md) |

### Demos and enablement

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Prep a clone as a DF Hands-On workshop org (capture/replay seeded quotes+config, verify before templating) | DF Workshop Setup | [df-workshop-setup/SKILL.md](df-workshop-setup/SKILL.md) |
| Maintain the In-App Learning framework (`inapp`) | In-App Framework | [inapp-framework/SKILL.md](inapp-framework/SKILL.md) |
| Author/update enablement exercises | Release Enablement | [release-enablement/SKILL.md](release-enablement/SKILL.md) |
| Generate the QuantumBit demo-script canvas (per-release) | QB Demo Script Generator | [qb-demo-script/SKILL.md](qb-demo-script/SKILL.md) |

### Repository maintenance

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Review docs before merge | Doc Consistency | [doc-consistency/SKILL.md](doc-consistency/SKILL.md) |
| Create, update, register, or test AI-agent skills | Skill Authoring | [skill-authoring/SKILL.md](skill-authoring/SKILL.md) |
| Process PR reviews / run the pre-merge audit (completeness sweeps) | Audit Review | [audit-review/SKILL.md](audit-review/SKILL.md) |

### Optional maintainer integrations

Use these only when you have access to the corresponding private repository.
Public contributions follow [CONTRIBUTING.md](../../CONTRIBUTING.md); no private
tracker or sibling clone is required.

| I need to... | Skill | Entry Point |
|-------------|-------|-------------|
| Find, claim or close durable work items across workstations and agents | Todo Tracker | [todo-tracker/SKILL.md](todo-tracker/SKILL.md) |
| Cross-repo skill manifest (PMOS ↔ Foundations) | PMOS Integration | [pmos-integration/SKILL.md](pmos-integration/SKILL.md) |

## Help Area to Owning Skill

Route by the prefix of a 264 Help article id (`docs/salesforce/264/help/articles/`).
"No owner yet" means no skill covers the area; start from
[revenue-cloud-docs] and the Help snapshot.

| Help prefix or cluster | Owning skill |
|------------------------|--------------|
| `ind.pricing_` | [pricing-setup] (org setup), [pricing-procedures] (elements, runtime) |
| `ind.product_` | [product-catalog-modeling]; configurator rules: [constraint-models] |
| `ind.qocal_` | [transaction-line-editor], [quote-negotiation-rounds], |
| | [asset-lifecycle-changes], [ramped-quotes] as the topic fits; API calls: [rlm-business-apis] |
| `ind.billing_` setup (policies, treatments, milestones, terms) | [billing-setup] |
| `ind.billing_` runtime (invoicing, tax, payments, memos) | No owner yet; see revenue-cloud-docs |
| `ind.rm_`, `ind.um_` (rate, usage mgmt) | [usage-consumption] (demos); setup: no owner yet |
| `ind.dro_` | [dro-plans] |
| `ind.approvals_` | [advanced-approvals] |
| `ind.sf_contracts_` | [salesforce-contracts] |
| `ind.rev_agent_` (Agentforce for Revenue Cloud) | No owner yet; see revenue-cloud-docs |
| Configurator customization (beyond CML rules) | No owner yet; see revenue-cloud-docs |

Cross-cutting topics:

| Topic | Start here |
|-------|------------|
| Promotions | [promotion-execution]; `ind.pricing_promotion_execution_element` |
| Product discovery | [discovery-procedures] (browse prices), [product-catalog-modeling] |
| Qualification rules | [expression-sets] (QualificationProcedure type) |
| Multi-currency | [import-export-and-bulk-data] |
| PRM and partner setup (`prm` flag, `prepare_prm` flow) | [feature-flags] |
| Place Sales Transaction API | [rlm-business-apis] |

[revenue-cloud-docs]: revenue-cloud-docs/SKILL.md
[pricing-setup]: pricing-setup/SKILL.md
[pricing-procedures]: pricing-procedures/SKILL.md
[product-catalog-modeling]: product-catalog-modeling/SKILL.md
[constraint-models]: constraint-models/SKILL.md
[transaction-line-editor]: transaction-line-editor/SKILL.md
[quote-negotiation-rounds]: quote-negotiation-rounds/SKILL.md
[asset-lifecycle-changes]: asset-lifecycle-changes/SKILL.md
[ramped-quotes]: ramped-quotes/SKILL.md
[rlm-business-apis]: rlm-business-apis/SKILL.md
[billing-setup]: billing-setup/SKILL.md
[usage-consumption]: usage-consumption/SKILL.md
[dro-plans]: dro-plans/SKILL.md
[advanced-approvals]: advanced-approvals/SKILL.md
[salesforce-contracts]: salesforce-contracts/SKILL.md
[promotion-execution]: pricing-procedures/elements/promotion-execution.md
[discovery-procedures]: pricing-procedures/discovery-procedures.md
[expression-sets]: expression-sets/SKILL.md
[import-export-and-bulk-data]: pricing-setup/import-export-and-bulk-data.md#adding-a-currency
[feature-flags]: cci-orchestration/feature-flags.md

Pricing skill split: pricing-setup is org setup (books, schedules, recipes);
pricing-procedures is procedure elements and runtime; pricing-wiring is this
repo's build sequencing; expression-sets is generic expression-set CRUD and
overlays, including non-pricing procedures.

## How Skills Are Structured

Every top-level `SKILL.md` starts with YAML `name` and `description` fields
for discovery: the name matches its directory, and the description explains
what the skill does and when to use it. See the
[authoring requirements](skill-authoring/SKILL.md#discovery-metadata) for the
format and validation constraints. Native discovery paths vary by agent;
the router above remains a plain-file entry point. The repository includes
shared-content links under `.agents/skills/` and `.claude/skills/`; see
[native discovery setup and verification](../../docs/guides/agent-skill-discovery.md).

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

This table is the canonical list — `AGENTS.md` points here rather than repeating it.

| Rule | Triggers On | Equivalent Skill |
|------|-------------|------------------|
| `analysis-artifacts.mdc` | (always applies) | *(stand-alone — AI-generated working docs go in `.agents/artifacts/` under `todos/attachments/<id>/`, an existing `topics/<slug>/` or else `inbox/`; never its root or the public repo)* |
| `sfdmu-export-json.mdc` | `**/export.json` | `sfdmu-data-plans/SKILL.md` |
| `sfdmu-csv-data.mdc` | `datasets/sfdmu/**/*.csv` | `sfdmu-data-plans/SKILL.md` |
| `cci-task-definitions.mdc` | `cumulusci.yml` | `cci-orchestration/SKILL.md` |
| `cci-python-tasks.mdc` | `tasks/**/*.py` | `cci-orchestration/custom-task-authoring.md` |
| `apex-scripts.mdc` | `scripts/apex/**/*.apex` | `troubleshooting/SKILL.md` |
| `apex-classes.mdc` | `unpackaged/**/*.cls`, `force-app/**/*.cls` | *(stand-alone — sharing keywords, `Id.valueOf` validation, SOQL safety, test patterns; `repo-integration/SKILL.md` for placement)* |
| `lwc-components.mdc` | `unpackaged/**/lwc/**/*.{html,js}`, `force-app/**/lwc/**/*.{html,js}` | *(stand-alone — template syntax, ARIA/accessibility, performance, error messages; `repo-integration/SKILL.md` for placement)* |
| `ux-templates.mdc` | `templates/**` | `repo-integration/SKILL.md` |
| `robot-tests.mdc` | `robot/**/*.robot` | `robot-testing/SKILL.md` |
| `doc-review.mdc` | `cumulusci.yml`, `tasks/**/*.py`, `datasets/sfdmu/**/export.json`, `datasets/sfdmu/**/*.csv`, `robot/**/*.robot`, `.cursor/skills/**/*.md` | `doc-consistency/SKILL.md` |
| `context-plans.mdc` | `datasets/context_plans/**/*.json` | `context-service/SKILL.md` |
