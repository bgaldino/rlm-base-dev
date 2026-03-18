# Revenue Cloud Foundations: The Build Process

**How `prepare_rlm_org` Stands Up a Fully Configured Revenue Cloud Org**

> Audience: Semi-technical stakeholders, enablement engineers, and new team members
> Last Updated: March 2026 | Salesforce Release 260 (Spring '26) | API v66.0

---

## What This Document Covers

Revenue Cloud Foundations automates the creation and configuration of Salesforce Revenue Lifecycle Management (RLM) environments. The centerpiece of this automation is the `prepare_rlm_org` flow — a 28-step orchestration that transforms a bare Salesforce org into a fully functional Revenue Cloud environment, complete with product catalogs, pricing engines, billing configurations, and more.

This guide walks through that build process from start to finish, explaining not just *what* happens at each stage, but *why* each step exists and how the pieces fit together. Whether you're onboarding to the team, preparing a demo environment, or troubleshooting a failed build, this document gives you the full picture.

---

## The Technology Behind the Build

Before diving into the flow itself, it helps to understand the tools that power it.

**CumulusCI (CCI)** is the orchestration engine. Think of it as the conductor of the orchestra — it defines the order of operations, manages dependencies between steps, and provides the runtime for executing tasks against a Salesforce org. Every step in `prepare_rlm_org` is either a CCI task (a single unit of work) or a CCI flow (a sequence of tasks grouped together).

**SFDMU (Salesforce Data Move Utility) v5** handles all data loading. When the build needs to insert product catalogs, pricing records, billing configurations, or any other data, SFDMU reads CSV files from the repository and loads them into the org. Version 5 is critical — it introduced breaking changes from v4, and all our data plans are built for v5's composite key patterns.

**Salesforce DX / sf CLI** handles metadata deployment — pushing configuration, custom objects, permission sets, and other metadata to the org.

**Python** powers the custom task classes that wrap SFDMU operations, manage context definitions, handle constraint model imports, and perform other specialized work.

**Robot Framework** drives browser automation for the handful of Salesforce Setup UI configurations that have no API equivalent — things like toggling revenue settings switches that can only be clicked through the UI.

---

## Feature Flags: How the Build Adapts

One of the most important concepts to understand is that `prepare_rlm_org` is not a fixed sequence — it's a *conditional* sequence controlled by around 30 feature flags. These flags live in `cumulusci.yml` under `project.custom` and determine which steps execute for a given build.

For example, if you're building an org that doesn't need billing capabilities, you set `billing: false` and the entire billing data load, activation, and settings deployment is skipped. If you want the QuantumBit product dataset (the default demo data shape), `qb: true` enables it. If you're building a Trialforce Source Org for trial generation, `tso: true` activates additional permission sets and metadata bundles specific to that org type.

This flag-driven design means a single flow definition serves dozens of different org configurations — from minimal developer scratch orgs to fully loaded demo environments to Trialforce Source Orgs.

The most commonly used flags and their defaults:

- **qb: true** — Enables the QuantumBit product dataset (the primary demo data shape)
- **billing: true** — Billing terms, schedules, legal entities, GL accounts
- **tax: true** — Tax policies, treatments, and the tax engine
- **dro: true** — Dynamic Revenue Orchestration fulfillment plans
- **rating: true** — Usage-based rating design-time data
- **rates: true** — Rate cards and rate card entries
- **clm: true** — Contract Lifecycle Management metadata
- **prm: true** — Partner Relationship Management
- **docgen: true** — Document Generation templates
- **constraints: true** — Constraint Builder / product configuration rules
- **tso: false** — Trialforce Source Org mode (off by default for dev orgs)

---

## The Build Process: Phase by Phase

The 28 steps of `prepare_rlm_org` can be understood as seven logical phases. Each phase builds on the previous one — you can't load product data before the metadata that defines those objects is deployed, and you can't activate billing records before they're inserted.

---

### Phase 1: Foundation (Steps 1–3)

**What happens:** The build validates the local environment, assigns permission set licenses and groups, extends context definitions, cleans up settings incompatible with the target org type, and prepares decision tables and expression sets.

**Why it matters:** This is the scaffolding that everything else depends on. Permission set licenses (PSLs) unlock Salesforce features at the platform level — without the `RatingDesignTimePsl`, for instance, the org physically cannot store usage rating records. Permission set groups (PSGs) bundle the fine-grained permissions that users need to interact with RLM features.

**Key sub-flow: `prepare_core`** runs first and performs the heaviest lifting:

1. **Environment validation** (`validate_setup`) — Confirms that Python, CCI, sf CLI, SFDMU v5, and Node.js are all installed and at compatible versions. This catches common "it works on my machine" problems before the build even starts.

2. **Permission set license assignment** — Assigns 30+ PSLs covering core RLM, billing, rating, AI, CLM, and other capabilities. These are assigned in waves because some licenses depend on others being present first.

3. **Settings cleanup** (scratch orgs only) — Removes metadata settings that don't apply to scratch orgs, preventing deployment failures from unsupported configuration.

4. **Decision table scaffolding** (scratch orgs only) — Temporarily excludes active decision tables, deploys pre-deployment metadata bundles (settings, PSGs, tax metadata), then restores the decision tables. This dance is necessary because some decision tables reference metadata that must exist before they can be deployed.

5. **Context definition extension** — Extends 11 standard RLM context definitions with custom attributes via the Context Service API. Contexts are how Revenue Cloud maps business processes to data — the Sales Transaction Context maps quotes, the Billing Context maps billing schedules, and so on. Each context needs custom extensions to support the demo data model.

6. **Rule library creation** — Creates pricing and DRO rule libraries that the pricing and fulfillment engines reference at runtime.

**`prepare_decision_tables`** (Step 2) activates all decision tables. The `cleanup_settings_for_dev` task and the decision table exclude/restore steps run for all org types (the scratch-only guards are not active in the current flow). Decision tables are the lookup structures that drive pricing calculations, rate resolution, and tax computation. They must be active before any data that references them is loaded.

**`prepare_expression_sets`** (Step 3) deactivates existing expression sets. On scratch orgs it also validates pricing schedule prerequisites and deploys expression sets in draft state (`ensure_pricing_schedules` and `deploy_expression_sets` are gated on `org_config.scratch`); on non-scratch orgs only the deactivation step runs. Expression sets are the business logic rules that Revenue Cloud evaluates during transactions — they're deployed as drafts now and activated later (in Step 19) after all dependent data is in place.

---

### Phase 2: Metadata Deployment (Steps 4–9)

**What happens:** The core Salesforce metadata is deployed, payments infrastructure is set up, price adjustment schedules are activated, scratch org seed data is inserted, and the QuantumBit-specific metadata and permissions are applied.

**Why it matters:** Metadata deployment is what gives the org its *shape* — the custom objects, fields, page layouts, flows, and settings that define how Revenue Cloud operates. Without this metadata, there's nowhere to put the data that comes in later phases.

**Payments webhook creation** (Step 4, conditional on `payments` flag) — Creates the Experience Cloud site that serves as the payments webhook endpoint. This must happen early because the site takes time to provision and later steps depend on it.

**`deploy_full`** (Step 5) — This is the single largest step in the build. It deploys the core SFDX package from `force-app/main/default`. The `unpackaged/pre/` bundle is deployed earlier (before this step), and `unpackaged/post_*/` bundles (payments, billing portal, PRM, TSO, etc.) are deployed in their respective sub-flows later in the sequence. This single step pushes hundreds of metadata components to the org.

**Price adjustment schedule activation** (Step 6, scratch orgs only) — Activates price adjustment schedules that control how pricing rules apply discounts, markups, and other adjustments. These must be active before pricing data can be loaded.

**Scratch org seed data** (Step 7, scratch orgs only, not TSO) — Inserts basic Account and Contact records that other data plans reference. In production-like orgs, these records already exist; in fresh scratch orgs, we need to create them.

**Payments site deployment** (Step 8, conditional on `payments` flag) — Deploys the payments site metadata and settings, then publishes the Experience Cloud community. Because `Payments_Webhook.site-meta.xml` stores a placeholder username in the repo, a patch task replaces the placeholder with the org's actual username immediately before the deploy, and a revert task restores the placeholder immediately after — so no real username is ever committed.

**QuantumBit preparation** (Step 9) — Deploys QuantumBit-specific metadata (UI themes, utility flows, billing flexipages), sets up approval workflows, assigns the QuantumBit permission set, and enables CALM (Customer Asset Lifecycle Management) delete permissions.

---

### Phase 3: Product Catalog and Pricing (Steps 10–11)

**What happens:** The product catalog master (PCM) data is loaded, product images are attached, and pricing data (price books, adjustments, tiers) is inserted.

**Why it matters:** Products and pricing are the foundation of every Revenue Cloud transaction. A quote can't be created without products to sell, and those products can't be priced without price book entries and adjustment rules.

**Product data loading** (Step 10) — For the QuantumBit data shape, this loads 28 objects including Product2, ProductCategory, ProductCatalog, ProductSellingModel, ProductSellingModelOption, and their relationships. The PCM data defines the full product hierarchy — what products exist, how they're categorized, what selling models they use (one-time, subscription, usage-based), and how they relate to each other as bundles and components. Product images are loaded in a separate pass because image records (ContentVersion/ContentDocumentLink) require the product records to already exist.

**Pricing data loading** (Step 11) — Loads 16 objects including PricebookEntry, PriceAdjustmentSchedule, PriceAdjustmentTier, and their relationships. Before loading, existing pricing data is deleted to prevent duplicates — this is a clean-load pattern rather than an upsert, because SFDMU v5 has known limitations with composite-key upserts on pricing objects.

---

### Phase 4: Business Process Configuration (Steps 12–18)

**What happens:** Each major Revenue Cloud capability gets its data loaded and activated — document generation, dynamic revenue orchestration, tax, billing, analytics, CLM, and usage rating.

**Why it matters:** This is where the org goes from having a product catalog to being able to actually *do things* with it — generate quotes with documents, calculate taxes, create billing schedules, rate usage, and orchestrate fulfillment.

**Document Generation** (Step 12, `docgen` flag) — Creates the DocGen template library, enables the Document Builder toggle via Robot Framework (this is one of those settings with no API), deploys document templates and seller fields, and activates templates. DocGen allows users to generate PDF quotes and contracts directly from Salesforce.

**Dynamic Revenue Orchestration** (Step 13, `dro` flag) — Loads fulfillment plan data that defines how orders are decomposed and routed for fulfillment. DRO data includes dynamic user assignment — the build queries the target org for the running user and injects that user's Name into the data, because fulfillment assignments are user-specific.

**Tax** (Step 14, `tax` flag) — Creates the tax engine instance, loads tax policies and treatments, and activates tax records. The tax engine is a Revenue Cloud component that calculates tax at transaction time. It must be created via Apex before tax policy data can reference it.

**Billing** (Step 15, `billing` flag) — The most complex data load in the build. Billing data is loaded in three passes because of circular dependencies between billing objects — for example, billing treatments reference legal entities, but legal entity assignments reference billing treatments. After data loading, the build activates billing flows, sets the default payment term, activates billing records, and deploys billing-specific settings including ID resolution settings (which tell the billing engine how to resolve record references) and invoice template settings.

**Analytics** (Step 16, `analytics` flag) — Enables Data Sync/Connections replication, which allows Revenue Cloud data to flow to CRM Analytics for reporting.

**CLM** (Step 17, `clm` + `clm_data` flags) — Loads Contract Lifecycle Management reference data including contract templates, clause libraries, and related configuration.

**Rating** (Step 18, `rating` + `rates` flags) — Loads usage rating design-time data and rate cards. Rating data is loaded in two passes due to self-referential relationships between Product Usage Resources (PURs), Product Usage Resource Periods (PURPs), and Product Usage Groups (PUGs). Rate card data is loaded separately. After both are loaded, a complex 7-step Apex activation script runs to activate PURs, PUGs, and rate card entries in the correct platform-required order.

---

### Phase 5: Expression Sets and Permissions (Steps 19–23)

**What happens:** Expression sets are re-deployed from draft to active state, TSO-specific permissions are applied, procedure plans are created, PRM community is published, and Agentforce agents are deployed.

**Why it matters:** Expression sets are the business logic engine of Revenue Cloud — they evaluate pricing rules, validation rules, and product qualification rules at transaction time. They were deployed as drafts in Phase 1 because they reference data that didn't exist yet. Now that all data is loaded, they can be activated.

**Expression set activation** (Step 19) — Re-deploys expression sets with active status using XPath transformation of the metadata XML. This is a deliberate two-pass approach: deploy as draft first to avoid validation errors against missing data, then activate once all data is in place.

**TSO preparation** (Step 20, `tso` flag) — Assigns additional permission set licenses, permission set groups, and metadata bundles specific to Trialforce Source Orgs. TSOs have a superset of permissions because they're used to generate trial orgs that need to work out of the box.

**Procedure plans** (Step 21, `procedureplans` flag) — Creates Procedure Plan Definitions and their associated sections and options via the Connect API and SFDMU data loading. Procedure plans define the step-by-step flows for quote pricing and other revenue processes.

**PRM** (Step 22, `prm` flag) — Creates the Partner Central community, publishes it, deploys sharing rules, loads PRM-specific data, and extends the Sales Transaction Context with partner account attributes.

**Agentforce agents** (Step 23, `agents` flag) — Deploys Agentforce AI agent configurations, settings, and assigns the quoting agent permission set.

---

### Phase 6: Constraints and Guided Selling (Steps 24–25)

**What happens:** The Constraint Model Library (CML) is imported, constraint settings are configured via Robot Framework, and guided selling data is loaded.

**Why it matters:** Constraints define the product configuration rules — what products can be combined, what options are required, what configurations are invalid. These are critical for CPQ (Configure, Price, Quote) workflows where users build complex product bundles.

**Constraints** (Step 24) — This is a multi-step process: load transaction processing types, deploy constraint metadata (classes, triggers, UI components), configure constraint settings via Robot Framework (another UI-only setting), validate the CML data structure, import two constraint model datasets (QuantumBitComplete and Server2) with polymorphic ID resolution, and activate the expression set versions. The CML import is particularly sophisticated — it resolves polymorphic IDs across Product2, ProductClassification, and ProductRelatedComponent records using Salesforce ID prefix detection.

**Guided Selling** (Step 25, `guidedselling` flag) — Loads guided selling assessment data and deploys the guided selling metadata. Guided selling creates interactive discovery flows that recommend products based on customer responses.

---

### Phase 7: Final Configuration (Steps 26–28)

**What happens:** Revenue settings are configured via Robot Framework, pricing discovery is reconfigured for scratch orgs, and all decision tables are refreshed.

**Why it matters:** This phase is the "polish" — it ensures that all the pieces assembled in previous phases are properly wired together and that runtime configurations reflect the current state of all loaded data.

**Revenue settings configuration** (Step 26) — Uses Robot Framework to navigate the Revenue Cloud Setup UI and configure settings including the pricing procedure, usage rating toggle, instant pricing toggle, and create orders flow. These are among the last settings configured because they reference components deployed and activated in earlier phases.

**Pricing discovery reconfiguration** (Step 27, scratch orgs only, not TSO) — Fixes the pricing discovery procedure by reconfiguring an expression set. This addresses a platform behavior where scratch org provisioning creates a default pricing discovery configuration that conflicts with the one we deploy.

**Decision table refresh** (Step 28) — The final step syncs pricing data and refreshes all decision table categories: pricing discovery, asset, rating, rating discovery, and commerce (if enabled). Decision tables are the lookup caches that the pricing and rating engines use at runtime — refreshing them ensures they reflect all the data loaded during the build. This step must always run last because it materializes the current state of all reference data into the decision table engine.

---

## How Long Does It Take?

A typical `prepare_rlm_org` run with default flags (QuantumBit data shape, billing, tax, rating, DRO, CLM, constraints, PRM, and DocGen all enabled) takes approximately 45–75 minutes for a scratch org, depending on network conditions and Salesforce instance load. The longest individual steps are typically `deploy_full` (metadata deployment), the billing data load (three-pass), and the decision table refresh at the end.

---

## Running the Build

```bash
# Full build against a scratch org named "beta"
cci flow run prepare_rlm_org --org beta

# Check which flags are active
cci project info

# Override a flag for a single run
cci flow run prepare_rlm_org --org beta -o billing false
```

---

## When Things Go Wrong

The most common failure points and how to address them:

**Permission set license assignment failures** — Usually caused by the org edition not supporting a particular license. The build assigns PSLs with retry logic, but some licenses are only available in specific editions (Enterprise, Unlimited, etc.).

**Metadata deployment failures** — Often caused by missing dependencies or settings incompatible with the org type. The `cleanup_settings_for_dev` task in Phase 1 handles most of these for scratch orgs, but new settings introduced by Salesforce releases can cause unexpected failures.

**Data load failures** — Most commonly caused by SFDMU v5 composite key issues or missing prerequisite records. The project's SFDMU v5 compliance rules (documented in `CLAUDE.md`) explain the known bugs and workarounds.

**Robot Framework failures** — The browser automation steps can fail if Chrome/ChromeDriver versions are mismatched or if Salesforce UI elements have changed between releases. Running `validate_setup` first catches ChromeDriver issues.

**Decision table refresh timeouts** — Large decision tables can take several minutes to refresh. The platform has built-in timeout handling, but very large orgs may need retry.

---

## Key Concepts Glossary

- **CCI (CumulusCI)** — Open-source Salesforce project automation framework by Salesforce.org
- **SFDMU** — Salesforce Data Move Utility, a data migration tool
- **PCM** — Product Catalog Management, the Salesforce object model for products
- **DRO** — Dynamic Revenue Orchestration, the fulfillment planning engine
- **PUR** — Product Usage Resource, a rating object for usage-based products
- **PURP** — Product Usage Resource Period, a time-bound rating interval
- **PUG** — Product Usage Group, a grouping of usage resources
- **CML** — Constraint Model Library, the product configuration rules engine
- **PSL** — Permission Set License, a Salesforce platform-level feature entitlement
- **PSG** — Permission Set Group, a bundle of permission sets
- **Decision Table** — A lookup structure used by pricing/rating engines at runtime
- **Expression Set** — A business logic rule evaluated during revenue transactions
- **Context Definition** — A mapping between a business process and its data model
- **TSO** — Trialforce Source Org, used to generate Salesforce trial orgs
- **CALM** — Customer Asset Lifecycle Management
