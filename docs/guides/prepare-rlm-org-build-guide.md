# Revenue Cloud Base Foundations: The Build Process

**How `prepare_rlm_org` Stands Up a Fully Configured Revenue Cloud Org**

> Audience: Semi-technical stakeholders, enablement engineers, and new team members
> Last Updated: March 2026 | Salesforce Release 262 (Summer '26) | API v67.0

---

## What This Document Covers

Revenue Cloud Base Foundations automates the creation and configuration of Salesforce Revenue Lifecycle Management (RLM) environments. The centerpiece of this automation is the `prepare_rlm_org` flow — a 28-step orchestration that transforms a bare Salesforce org into a fully functional Revenue Cloud environment, complete with product catalogs, pricing engines, billing configurations, and more.

This guide walks through that build process from start to finish, explaining not just *what* happens at each stage, but *why* each step exists and how the pieces fit together. Whether you're onboarding to the team, preparing a demo environment, or troubleshooting a failed build, this document gives you the full picture.

---

## The Technology Behind the Build

Before diving into the flow itself, it helps to understand the tools that power it.

**CumulusCI (CCI)** is the orchestration engine. Think of it as the conductor of the orchestra — it defines the order of operations, manages dependencies between steps, and provides the runtime for executing tasks against a Salesforce org. Every step in `prepare_rlm_org` is either a CCI task (a single unit of work) or a CCI flow (a sequence of tasks grouped together).

**SFDMU (Salesforce Data Move Utility) v5** handles most CSV-based data loading. When the build needs to insert product catalogs, pricing records, billing configurations, or other structured data, SFDMU reads CSV files from the repository and loads them into the org. Version 5 is critical — it introduced breaking changes from v4, and all our data plans are built for v5's composite key patterns. Some data is loaded via other mechanisms: constraint models use the custom CML import task (`tasks/rlm_cml.py`), and Procedure Plan Definitions are created via the Salesforce Connect REST API.

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
- **clm: true** — Enables CLM permission set licenses and CLM context definition extensions; CLM reference data additionally requires `clm_data: true` (defaults to `false`)
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

3. **Settings cleanup** — Removes metadata settings that can cause deployment failures on certain org types. This currently runs for all org types, not just scratch orgs.

4. **Decision table scaffolding** — Temporarily excludes active decision tables, deploys pre-deployment metadata bundles (settings, permission set groups, tax metadata), then restores the decision tables. This currently runs for all org types. The reason for the exclusion-and-restore pattern: some decision tables reference metadata that doesn't exist yet, so they'd fail validation if left active during that deployment.

5. **Context definition extension** — Extends up to 11 standard RLM context definitions with custom attributes via the Context Service API. Two always run (Sales Transaction, Product Discovery) plus Asset; the remaining 8 are conditional: Cart (`commerce`), Billing and Collection Plan Segment (`billing`), Fulfillment Asset (`dro`), Contracts and Contracts Extraction (`clm`), Rate Management and Rating Discovery (`rating`). Contexts are how Revenue Cloud maps business processes to data — the Sales Transaction Context maps quotes, the Billing Context maps billing schedules, and so on. Each context needs custom extensions to support the demo data model.

6. **Rule library creation** (`breconfig` flag) — Creates pricing rule libraries and, when `dro` is also enabled, the DRO rule library. Skipped in default builds where `breconfig: false`.

**`prepare_decision_tables`** (Step 2) activates a specific set of decision tables — but only on scratch orgs. On sandboxes or persistent orgs, this step runs but skips activation, since those orgs are expected to already have their decision tables in place. Decision tables are the lookup structures that drive pricing calculations, rate resolution, and tax computation.

**`prepare_expression_sets`** (Step 3) deactivates existing expression sets on all org types. On scratch orgs it also validates that pricing schedule prerequisites are in place and deploys expression sets in draft state — on sandboxes or persistent orgs, only the deactivation runs. Expression sets are the business logic rules that Revenue Cloud evaluates during transactions — they're deployed as drafts now and activated later (in Step 19) after all dependent data is in place.

---

### Phase 2: Metadata Deployment (Steps 4–9)

**What happens:** The core Salesforce metadata is deployed, payments infrastructure is set up, price adjustment schedules are activated, scratch org seed data is inserted, and the QuantumBit-specific metadata and permissions are applied.

**Why it matters:** Metadata deployment is what gives the org its *shape* — the custom objects, fields, page layouts, flows, and settings that define how Revenue Cloud operates. Without this metadata, there's nowhere to put the data that comes in later phases.

**Payments webhook creation** (Step 4, conditional on `payments` flag) — Creates the Experience Cloud site that serves as the payments webhook endpoint. This must happen early because the site takes time to provision and later steps depend on it.

**`deploy_full`** (Step 5) — This is the single largest step in the build. It deploys the core SFDX package from `force-app/main/default`. The `unpackaged/pre/` bundle is deployed earlier (before this step), and `unpackaged/post_*/` bundles (payments, billing portal, PRM, TSO, etc.) are deployed in their respective sub-flows later in the sequence. This single step pushes hundreds of metadata components to the org.

**Price adjustment schedule activation** (Step 6, scratch orgs only) — Activates price adjustment schedules that control how pricing rules apply discounts, markups, and other adjustments. These must be active before pricing data can be loaded.

**Scratch org seed data** (Step 7, scratch orgs only, not TSO) — Inserts basic Account and Contact records that other data plans reference. In production-like orgs, these records already exist; in fresh scratch orgs, we need to create them.

**Payments site deployment** (Step 8) — This step always runs, but if `payments` is turned off, every task inside it is simply skipped. When Payments is enabled, it deploys the site metadata and settings and publishes the Experience Cloud community. The site metadata in the repository uses a placeholder username to avoid storing real usernames in source control — right before deployment, that placeholder is swapped for the org's actual username, and immediately after deployment it's restored. Nothing sensitive ever gets committed.

**QuantumBit preparation** (Step 9) — This step always runs, but like Payments, if `quantumbit` is off every task inside is simply skipped. When enabled, it deploys QuantumBit-specific metadata (UI themes, utility flows, billing flexipages), sets up approval workflows, assigns the QuantumBit permission set, and enables CALM (Customer Asset Lifecycle Management) delete permissions. Two separate flags control QuantumBit content: `quantumbit` controls this metadata deployment, while the actual product and pricing data loads later in the flow are controlled independently by the `qb` flag.

---

### Phase 3: Product Catalog and Pricing (Steps 10–11)

**What happens:** The product catalog master (PCM) data is loaded, product images are attached, and pricing data (price books, adjustments, tiers) is inserted.

**Why it matters:** Products and pricing are the foundation of every Revenue Cloud transaction. A quote can't be created without products to sell, and those products can't be priced without price book entries and adjustment rules.

**Product data loading** (Step 10) — For the QuantumBit data shape, this loads 28 objects including Product2, ProductCategory, ProductCatalog, ProductSellingModel, ProductSellingModelOption, and their relationships. The PCM data defines the full product hierarchy — what products exist, how they're categorized, what selling models they use (one-time, subscription, usage-based), and how they relate to each other as bundles and components. Product images are loaded in a separate pass because image records (ContentVersion/ContentDocumentLink) require the product records to already exist.

**Pricing data loading** (Step 11) — Loads pricing objects including PricebookEntry, PriceAdjustmentSchedule, PriceAdjustmentTier, and their relationships (the plan has 12 write operations, 3 read-only prerequisite lookups, and 1 excluded object). Before loading, existing pricing data is deleted to prevent duplicates — this is a clean-load pattern rather than an upsert, because SFDMU v5 has known limitations with composite-key upserts on pricing objects.

---

### Phase 4: Business Process Configuration (Steps 12–18)

**What happens:** Each major Revenue Cloud capability gets its data loaded and activated — document generation, dynamic revenue orchestration, tax, billing, analytics, CLM, and usage rating.

**Why it matters:** This is where the org goes from having a product catalog to being able to actually *do things* with it — generate quotes with documents, calculate taxes, create billing schedules, rate usage, and orchestrate fulfillment.

**Document Generation** (Step 12, `docgen` flag) — Creates the DocGen template library, enables the Document Builder toggle via Robot Framework (this is one of those settings with no API), deploys document templates and seller fields, and activates templates. DocGen allows users to generate PDF quotes and contracts directly from Salesforce.

**Dynamic Revenue Orchestration** (Step 13, `dro` flag) — Loads fulfillment plan data that defines how orders are decomposed and routed for fulfillment. DRO data includes dynamic user assignment — the build queries the target org for the running user and injects that user's Name into the data, because fulfillment assignments are user-specific.

**Tax** (Step 14, `tax` flag) — Creates the tax engine instance, loads tax policies and treatments, and activates tax records. The tax engine is a Revenue Cloud component that calculates tax at transaction time. It must be created via Apex before tax policy data can reference it.

**Billing** (Step 15, `billing` flag) — The most complex data load in the build. Billing data is loaded in three passes because of circular dependencies between billing objects — for example, billing treatments reference legal entities, but legal entity assignments reference billing treatments. After data loading, the build activates billing flows, sets the default payment term, activates billing records, and deploys billing-specific settings including ID resolution settings (which tell the billing engine how to resolve record references) and invoice template settings.

**Analytics** (Step 16, `analytics` flag) — Enables full CRM Analytics via browser automation (Robot/Selenium). In Release 262 (Summer '26), the legacy `InsightsSetupSettings` VF iframe approach was removed; the build now clicks "Enable CRM Analytics" on the Analytics Getting Started page (`/lightning/setup/InsightsSetupGettingStarted/home`). This is required for the usage rating engine's data processing. The step is idempotent — if CRM Analytics is already enabled, the button is absent and the task skips the click.

**CLM** (Step 17, `clm` + `clm_data` flags) — Loads Contract Lifecycle Management reference data including contract templates, clause libraries, and related configuration.

**Rating** (Step 18, `rating` and `rates` flags) — Loads usage rating design-time data when `rating` is enabled. Rate card loading and the final activation steps additionally require `rates` to be on. Rating data is loaded in two passes due to self-referential relationships between Product Usage Resources (PURs), Product Usage Resource Policies (PURPs, API name `ProductUsageResourcePolicy`), and Product Usage Groups (PUGs). Rate card data is loaded separately when `rates` is also enabled. Activation happens in two separate steps: a 7-step Apex script activates PURs, PURPs, and PUGs in the platform-required order (with step 2.5a clearing Draft children of duplicate PURs to ensure idempotency on repeated runs), then rate card entries are activated via the Salesforce REST Composite API — in Release 262, `RateCardEntry` DML via the SOAP/Apex Execute Anonymous path raises an `UNKNOWN_EXCEPTION` platform regression; the REST path works correctly.

---

### Phase 5: Expression Sets and Permissions (Steps 19–23)

**What happens:** Expression sets are re-deployed from draft to active state, TSO-specific permissions are applied, procedure plans are created, PRM community is published, and Agentforce agents are deployed.

**Why it matters:** Expression sets are the business logic engine of Revenue Cloud — they evaluate pricing rules, validation rules, and product qualification rules at transaction time. They were deployed as drafts in Phase 1 because they reference data that didn't exist yet. Now that all data is loaded, they can be activated.

**Expression set activation** (Step 19) — Re-deploys expression sets with active status using XPath transformation of the metadata XML. This is a deliberate two-pass approach: deploy as draft first to avoid validation errors against missing data, then activate once all data is in place.

**TSO preparation** (Step 20, `tso` flag) — Assigns additional permission set licenses, permission set groups, and metadata bundles specific to Trialforce Source Orgs. TSOs have a superset of permissions because they're used to generate trial orgs that need to work out of the box.

**Procedure plans** (Step 21, `procedureplans` flag) — Creates Procedure Plan Definitions and their associated sections and options via the Connect REST API and SFDMU data loading. Procedure plans define the step-by-step flows for quote pricing and other revenue processes.

**PRM** (Step 22, `prm` flag) — Creates the Partner Central community, publishes it, and extends the Sales Transaction Context with partner account attributes — all of which happen whenever `prm` is on. Loading the QuantumBit PRM product data additionally requires `qb`; if you're building a Q3-only org, the community is still created and published but that data load is skipped. Two sub-steps are Trialforce Source Org-specific and only run in TSO builds: deploying the full Experience Bundle and assigning the `RLM_PRM` permission set. Sharing rules deployment is its own separate toggle (`sharingsettings`).

**Agentforce agents** (Step 23, `agents` flag) — Deploys Agentforce AI agent configurations, settings, and assigns the quoting agent permission set.

---

### Phase 6: Constraints and Guided Selling (Steps 24–25)

**What happens:** The Constraint Model Library (CML) is imported, constraint settings are configured via Robot Framework, and guided selling data is loaded.

**Why it matters:** Constraints define the product configuration rules — what products can be combined, what options are required, what configurations are invalid. These are critical for CPQ (Configure, Price, Quote) workflows where users build complex product bundles.

**Constraints** (Step 24, `constraints` and `constraints_data` flags) — This is a multi-step process with two independent flags. The `constraints` flag gates: loading transaction processing types (also requires `qb`), deploying constraint metadata (classes, triggers, UI components), and applying the context constraint engine node status. The `constraints_data` flag independently gates: configuring constraint settings via Robot Framework (a UI-only toggle), validating the CML data structure, importing three constraint model datasets (QuantumBitComplete, Server2, and QuantumBitPCM, all also require `qb`) with polymorphic ID resolution, and activating the expression set versions. The flow does not require `constraints` to be set before `constraints_data` steps run — they are independently gated — but in practice both are enabled together for a fully functional constraints setup. The CML import is particularly sophisticated — it resolves polymorphic IDs across Product2, ProductClassification, and ProductRelatedComponent records using Salesforce ID prefix detection.

**Guided Selling** (Step 25, `guidedselling` flag) — Loads guided selling assessment data and deploys the guided selling metadata. Guided selling creates interactive discovery flows that recommend products based on customer responses.

---

### Phase 7: Final Configuration (Steps 26–28)

**What happens:** Revenue settings are configured via Robot Framework, pricing discovery is reconfigured for scratch orgs, and all decision tables are refreshed.

**Why it matters:** This phase is the "polish" — it ensures that all the pieces assembled in previous phases are properly wired together and that runtime configurations reflect the current state of all loaded data.

**Revenue settings configuration** (Step 26) — Uses Robot Framework to navigate the Revenue Cloud Setup UI and configure settings including the pricing procedure, usage rating toggle, instant pricing toggle, and create orders flow. These are among the last settings configured because they reference components deployed and activated in earlier phases.

**Pricing discovery reconfiguration** (Step 27, scratch orgs only, not TSO) — Fixes the pricing discovery procedure by reconfiguring an expression set. This addresses a platform behavior where scratch org provisioning creates a default pricing discovery configuration that conflicts with the one we deploy.

**Decision table refresh** (Step 28) — The final step syncs pricing data and refreshes decision table categories. Pricing discovery always refreshes; the asset, rating, and rating discovery categories only refresh when `rating` is on; the commerce category only refreshes when `commerce` is on. Decision tables are the lookup caches that the pricing and rating engines use at runtime — refreshing them ensures they reflect all the data loaded during the build. This step must always run last because it materializes the current state of all reference data into the decision table engine.

---

## How Long Does It Take?

A typical `prepare_rlm_org` run with a full demo configuration (QuantumBit data shape, billing, tax, rating, DRO, CLM with `clm_data`, constraints, PRM, and DocGen all enabled) takes approximately 45–75 minutes for a scratch org, depending on network conditions and Salesforce instance load. Note that `clm_data` defaults to `false`, so CLM reference data is not loaded in a literal default run. The longest individual steps are typically `deploy_full` (metadata deployment), the billing data load (three-pass), and the decision table refresh at the end.

---

## Running the Build

```bash
# Full build against a scratch org named "beta"
cci flow run prepare_rlm_org --org beta

# Check which flags are active
cci project info

# Override any project.custom flag for a single run with -o <flag> <value>:
cci flow run prepare_constraints --org beta -o constraints_data true

# To change a flag persistently, edit project.custom in cumulusci.yml.
# Use -o for temporary one-off overrides; edit cumulusci.yml for permanent defaults.
```

---

## When Things Go Wrong

The most common failure points and how to address them:

**Permission set license assignment failures** — Usually caused by the org edition not supporting a particular license. The build assigns PSLs with retry logic, but some licenses are only available in specific editions (Enterprise, Unlimited, etc.).

**Metadata deployment failures** — Often caused by missing dependencies or settings incompatible with the org type. The `cleanup_settings_for_dev` task in Phase 1 handles most of these, but new settings introduced by Salesforce releases can cause unexpected failures.

**Data load failures** — Most commonly caused by SFDMU v5 composite key issues or missing prerequisite records. See `docs/references/sfdmu-composite-key-optimizations.md` for the primary reference on v5 migration changes and known bugs; `CLAUDE.md` covers the same rules in a developer-oriented format.

**Robot Framework failures** — The browser automation steps can fail if Chrome/ChromeDriver versions are mismatched or if Salesforce UI elements have changed between releases. Running `validate_setup` first catches ChromeDriver issues.

**Decision table refresh timeouts** — Large decision tables can take several minutes to refresh. The platform has built-in timeout handling, but very large orgs may need retry.

---

## Key Concepts Glossary

- **CCI (CumulusCI)** — Open-source Salesforce project automation framework by Salesforce.org
- **SFDMU** — Salesforce Data Move Utility, a data migration tool
- **PCM** — Product Catalog Management, the Salesforce object model for products
- **DRO** — Dynamic Revenue Orchestration, the fulfillment planning engine
- **PUR** — Product Usage Resource, a rating object for usage-based products
- **PURP** — Product Usage Resource Policy (API name `ProductUsageResourcePolicy`), a policy governing usage resource rating behavior
- **PUG** — Product Usage Group, a grouping of usage resources
- **CML** — Constraint Model Library, the product configuration rules engine
- **PSL** — Permission Set License, a Salesforce platform-level feature entitlement
- **PSG** — Permission Set Group, a bundle of permission sets
- **Decision Table** — A lookup structure used by pricing/rating engines at runtime
- **Expression Set** — A business logic rule evaluated during revenue transactions
- **Context Definition** — A mapping between a business process and its data model
- **TSO** — Trialforce Source Org, used to generate Salesforce trial orgs
- **CALM** — Customer Asset Lifecycle Management
