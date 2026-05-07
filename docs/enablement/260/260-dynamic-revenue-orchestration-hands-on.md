---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Dynamic Revenue Orchestration"
document_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag)"
  - "DRO data plan loaded (`prepare_dro` flow with `dro=true`) — provisions FulfillmentStepDefinitionGroups, Decomposition Rules, Fulfillment Scenarios for QB products"
  - "Integration Definitions configured if walkthroughs include external callouts"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Dynamic Revenue Orchestrator (pp 928–1100)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — Dynamic Revenue Orchestration section"
  - "docs/salesforce/260/feature-index.md — per-area feature inventory"
  - "datasets/sfdmu/qb/en-US/qb-dro/ — QuantumBit DRO data plan"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
  - ".cursor/skills/revenue-cloud-data-model/domains/dro.md"
---

# Revenue Cloud — Dynamic Revenue Orchestration

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog and DRO data plan loaded. The DRO data plan provisions FulfillmentStepDefinitionGroups, Decomposition Rules, and Fulfillment Scenarios for QB products.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 Solution Overview deck.** Six 260 features captured with Customer Need / Solution / Use Case content. Configuration steps for the new Invocable Actions (Decompose Sales Transaction + Orchestrate Sales Transaction) need 260 org walkthrough validation; flagged `[NEEDS REVIEW]`.

> **Cross-area constraint:** DRO is **not compatible with Swaps/Upgrades/Downgrades** (TM Feature 7). Walkthroughs that combine DRO orchestration with Advanced Amendments swap workflows are unsupported. The TM exercise carries this constraint inline.

---

## Carry-forward inventory (from prior releases)

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Orchestrate Business Processes (Quote Orchestration) | 256 | `docs/enablement/256/Summer '25 - DRO.pdf` | 🔄 **enhanced** in 260 — see Feature 4 ("Orchestrate a Business Process in DRO") which extends DRO orchestration to entities beyond Product2 (Collection Plans, Obligations, SRs) |
| Orchestrate Inflight Changes | 256 | same | ✅ no change |
| Decomposition Workspace | 256 | same | 🔄 **enhanced** in 260 — see Feature 1 (Decomposition Workspace Enhancements) |
| Product Classification Based Orchestration | 256 | same | ✅ no change |
| Expression Based Enrichment | 256 | same | ✅ no change |
| Schedule Fulfillment Steps Flexibly by Using Custom Dates | 258 | `docs/enablement/258/Dynamic Revenue Orchestrator - Winter '26 Revenue Cloud - External.pdf` | ✅ no change |
| Optimize Complex Order Orchestration by Using Custom Scopes | 258 | same | ✅ no change |
| Configure Technical Product Attribute Scopes for Enhanced Flexibility | 258 | same | ✅ no change |

---

## Upgrade Guidance from Winter '26

The master PDF "Upgrade Guidance for Spring '26" section (pp 115–117) does not include a dedicated DRO subsection. The general Rate and Usage Management upgrade guidance (Synchronize Custom Context Definitions for Rate Discovery and Rating Procedures) may apply if your DRO orchestration depends on rating-related context definitions.

→ **For details, see:** `docs/enablement/260/260-usage-management-hands-on.md` § Upgrade Guidance from Winter '26 → Synchronize Custom Context Definitions.

`rlm-base-dev` also has a Spring '26-specific note: the `update_product_fulfillment_decomp_rules` Apex task is run as part of `prepare_dro` to work around a known 260 bug where `ExecuteOnRuleId` is not generated on `INSERT` and must be triggered by an `UPDATE`. This is a build-time remediation (handled by the `prepare_dro` flow), not a customer-facing upgrade step.

---

## Cross-Area Compatibility Constraints

| Workflow | DRO Compatible? | Notes |
|---|---|---|
| Swaps / Upgrades / Downgrades | 🚫 **Not compatible** | Sourced from TM Feature 7 master PDF research (p 882). Plan walkthroughs accordingly. |
| Future-Dated Amendments | ✅ Yes | Future-dated ARC works with DRO; usage-product constraints apply (see TM Feature 8) |
| Multiple Ramp Schedules | ✅ Yes | Ramp deals + DRO orchestration are independent |
| Promotions (Beta) | ✅ Yes | Promotions affect pricing only, not orchestration |
| Advanced Approvals | ✅ Yes | Approval workflows can gate DRO plan generation via custom hooks (see Feature 3 below) |

---

## Release Overview

Spring '26 Dynamic Revenue Orchestration includes the following net-new features:

1. **Decomposition Workspace Enhancements** — view all components of technical bundles regardless of decomposition state; distinguish product-rules vs product-classification-rules in the Workspace
2. **Pause External Callouts During Downtime** — callout steps move to "On Hold" status when the integrated external system is offline, eliminating retry storms and unnecessary API consumption
3. **Hook Custom Logic Before Generating a Plan** — two new Invocable Actions (Decompose Sales Transaction + Orchestrate Sales Transaction) let designers run custom logic between decomposition and plan generation
4. **Orchestrate a Business Process in DRO** — extend DRO orchestration to entities beyond Product2 (Collection Plans, Obligations, SRs), eliminating catalog proliferation and forced product-tagging workarounds
5. **CME Managed Package and DRO Interop (GA)** — submit orders from the Industries CPQ (CME) managed package to DRO for orchestration
6. **Move and Change of Plan Support for CME Managed Package (Pilot)** — orchestrate MACD (Move/Add/Change/Disconnect) orders from Industries CPQ

---

## Feature 1: Decomposition Workspace Enhancements

> **Source:** Solution Overview "Decomp Workspace Enhancements" page.

### Business Objective

Designers managing technical product bundles previously had visibility gaps when decomposition rules applied indirectly. Specifically:

- A bundle's components weren't fully visible in the Decomposition Workspace if the root or a child component had been decomposed from a commercial bundle.
- A product inheriting decomposition rules from its product classification didn't show that inheritance — making it hard to know why specific rules were active.

Spring '26 enhances the Decomposition Workspace to surface both:

- **All components of technical bundles** even after decomposition has occurred at root or child level
- **Distinction between rules configured directly on the product vs. rules inherited from product classification**

### Use Cases

**DRO Designer persona:**

- **Audit a bundled tech product's decomposition** — open a complex bundled product (e.g., QB Complete) in the Decomposition Workspace; see all components and their associated rules, even when sub-bundles have decomposed.
- **Trace inherited classification rules** — confirm whether a specific decomposition rule comes from the product directly or was inherited from `PC-QB-COMPLETE` or another product classification.

### Design Time Configuration

> **No configuration required.** This is automatic behavior in 260.

The Decomposition Workspace UI now surfaces:

1. All components of a technical bundle, regardless of decomposition state of the root or child products.
2. Visual differentiation between product-level decomposition rules and product-classification-level decomposition rules.

### QuantumBit walkthrough scenario

1. Open a QB bundle that has Product Classification rules — e.g., a server bundle whose components map via `PC-QB-CPU`, `PC-QB-MEMORY`, `PC-QB-STORAGE` classifications.
2. Open the Decomposition Workspace for the bundle.
3. Verify all bundled components are visible, including any sub-bundles.
4. For each rule shown, verify the UI distinguishes between rules configured on the product directly vs. inherited from product classifications.

### Configuration and Runtime Video

📹 **"Decomposition Workspace Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 2: Pause External Callouts During Downtime

> **Source:** Solution Overview "Pause external callouts during downtime" page.

### Business Objective

When an external system that DRO calls out to is offline, callouts retry until they fatally fail — generating noise, consuming API quota, and requiring manual intervention to recover after the external system comes back online. Spring '26 introduces an explicit **'On Hold'** status for callout steps so admins can pause execution proactively when an external system is known to be offline.

### Use Cases

**Operations / Integration Admin persona:**

- **Pause during scheduled maintenance** — when an external system has known maintenance, set its Integration Definition to 'offline'; callouts stop attempting and stay in 'On Hold' status.
- **Avoid retry storms during incidents** — when an external system has unexpected downtime, an admin can pause callouts immediately to prevent wasted retries; resume by setting status back to 'online' once the system recovers.

### Design Time Configuration

> **Permission required:** DRO Admin / Integration Admin.

**Setup:**

1. From DRO Settings, **turn on Future Dated Step**.
2. When an external system is down or in maintenance, an admin **updates the status of the corresponding Integration Definition to `offline`**.

**Runtime behavior:**

- Callout steps targeting that Integration Definition move to 'On Hold' status (instead of attempting + failing + retrying).
- When the admin sets the Integration Definition back to `online`, callout steps resume from their 'On Hold' state.

### QuantumBit walkthrough scenario

1. Set up an Integration Definition for a QB external system (e.g., a fulfillment provisioning service for QB Server hardware).
2. Configure a callout step in a fulfillment plan definition that targets this Integration Definition.
3. Set the Integration Definition status to `offline`.
4. Trigger an order that would invoke the callout.
5. Verify the callout step lands in 'On Hold' status (not retrying).
6. Set the Integration Definition status to `online`.
7. Verify the callout step resumes execution.

### Configuration and Runtime Video

📹 **"Pause External Callouts Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 3: Hook Custom Logic Before Generating a Plan

> **Source:** Solution Overview "Hook custom logic before generating a plan" page.

### Business Objective

Some data critical to fulfillment can't be determined during order decomposition itself but is required before plan generation. Examples: dynamic start/end dates on Fulfillment Assets (FA), sales commission calculations, inventory availability checks. Customers previously had to monkey-patch the decomposition step or run post-hoc updates after plan generation. Spring '26 introduces a clean integration point with **two new Invocable Actions** that let designers split decomposition from plan generation cleanly.

### Use Cases

**Fulfillment Designer persona:**

- **Run inventory-availability checks before plan generation** — after decomposition, run a custom Apex/Flow check against external inventory; if certain components aren't available, modify the fulfillment line items before plan generation creates the orchestration plan.
- **Calculate sales commission per fulfillment line** — after decomposition, persist computed commission values on fulfillment line items so the generated plan reflects them.
- **Determine context-specific dates** — apply business rules to compute FA start/end dates based on customer requirements before the plan is generated.

### Design Time Configuration

> **Permission required:** DRO Designer + Flow Builder access.

Two new Invocable Actions are shipped:

| Invocable Action | Purpose |
|---|---|
| **Decompose Sales Transaction** | Runs decomposition only (does not generate the plan) |
| **Orchestrate Sales Transaction** | Triggers plan generation (called separately, after custom logic completes) |

**Pattern:**

1. Configure your transaction processing entry point to call **Decompose Sales Transaction** instead of the all-in-one decomposition + plan generation.
2. After decomposition, run your custom logic (Apex, Flow, etc.) on the resulting fulfillment line items / fulfillment assets.
3. **Trigger a platform event** after custom logic completes; the platform event invokes **Orchestrate Sales Transaction** to generate the plan.

[NEEDS REVIEW] — confirm exact platform event name and request body. Pull from master PDF and 260 org.

### QuantumBit walkthrough scenario

1. Configure a transaction processing flow that uses Decompose Sales Transaction for QB orders containing usage-rated products.
2. After decomposition, run custom Flow logic that determines the start date for each FA based on the customer's requested deployment date (custom field on the Quote).
3. Persist the computed start dates on the relevant FOLI records.
4. Fire a platform event to trigger Orchestrate Sales Transaction.
5. Verify the generated FulfillmentPlan and FulfillmentSteps respect the dynamic start dates.

### Configuration and Runtime Video

📹 **"Custom Logic Hook Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 4: Orchestrate a Business Process in DRO

> **Source:** Solution Overview "Orchestrate a Business Process" page.

### Business Objective

DRO previously had two design constraints that limited its applicability to non-product-centric workflows:

1. DRO was **tightly coupled with Product2** — orchestration plans had to be associated with products or product classifications.
2. The **transaction format was tightly coupled** with the Sales Transaction Context Definition format.

This meant customers couldn't use DRO for entities like Collection Plans, Obligations, Service Requests without lines, or other non-product business processes — they were forced to either tag everything as a product (catalog proliferation) or build orchestration outside DRO.

Spring '26 lifts both constraints. Customers can now orchestrate **any business entity** by adding context mappings, configuring the Setup entity, and submitting requests to DRO via a new Invocable Action.

### Use Cases

- **Billing dunning orchestration** — Billing teams use DRO to orchestrate dunning processes based on customer segments (no Product2 association required).
- **Service request orchestration** — Service Automation orchestrates SRs without line items.
- **Order-level orchestration** — Fulfillment designers associate orchestration plans **directly with orders** instead of tagging every product/classification with scenario rules. Reduces scenario-rule sprawl and stays under platform guardrails.

### Design Time Configuration

> **Permission required:** DRO Designer.

**Setup:**

1. Add the appropriate **context mappings** for your business entity (Collection Plan, Obligation, custom object, etc.).
2. Enter the necessary details in the **Setup entity** for DRO orchestration.
3. Submit a request to DRO using the new Invocable Action to orchestrate the designed business process.

[NEEDS REVIEW] — confirm exact context mapping setup steps + the new Invocable Action's input shape. Pull from master PDF.

### QuantumBit walkthrough scenario

QB doesn't natively model collection plans or obligations as part of its catalog data. For demonstration:

1. Set up a custom Collection Plan object scenario — define context mappings that link the Collection Plan to an account (and not to a Product2).
2. Configure DRO to orchestrate Collection Plans using the appropriate Fulfillment Step Definition Group.
3. Submit a Collection Plan via the new IA.
4. Verify a FulfillmentPlan is generated and orchestration proceeds without requiring any product association.

### Configuration and Runtime Video

📹 **"Orchestrate Business Process Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 5: CME Managed Package and DRO Interop (GA)

> **Source:** Solution Overview "Integrate DRO with Industries CPQ (GA)" page. **Note:** GA in 260 (was Pilot in earlier preview).

### Business Objective

DRO is the **in-core alternative** to Industries Order Management (IOM, formerly OM Std and OMPL) — with higher scale, better performance, and advanced features. Customers running Industries CPQ (CME managed package) want to leverage DRO for order orchestration without abandoning their existing CME setup.

### Use Cases

- **Industries CPQ + DRO** — capture orders in Industries CPQ, submit them to DRO for orchestration, get DRO's advanced fulfillment capabilities (decomposition, custom scopes, jeopardy, fallout) while keeping CME quote-to-order.

### Design Time Configuration

> **Permission required:** DRO Admin + CME Admin.

**Setup:**

1. **Enable DRO** in your org.
2. **Create and activate** the `CMESalesTransaction` context definition.
3. Configure **Sales Transaction Context for DRO** with respect to the `CMESalesTransaction` context definition.
4. **Set up Order Routing Rules** to direct CME orders to DRO for orchestration.

### Use Case detail

Capture order in Industries CPQ → submit to DRO for orchestration. The order benefits from:
- DRO's higher scale + better performance vs IOM
- DRO's in-core benefits — common components, native reports/dashboards
- DRO's advanced features — custom scopes, jeopardy/fallout, expression-based enrichment

### Configuration and Runtime Video

📹 **"CME Interop Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 6: Orchestrate Asset Move and Change of Plan (Pilot)

> **Source:** Solution Overview "Orchestrate Asset Move and Change of Plan" page. **Pilot** in 260.

### Business Objective

Telecom and similar service businesses want to retain end customers by allowing them to:
- **Move** services to different locations (e.g., relocating broadband)
- **Change Plan** to better/different offers with more competitive pricing (e.g., upgrading from broadband to triple-play Broadband + Telephony + TV)

The MACD (Move/Add/Change/Disconnect) order pattern is industry-standard but previously couldn't be orchestrated via DRO from Industries CPQ. Spring '26 adds Pilot support for orchestrating these flows.

### Use Cases

1. **Customer service location move** — telecom customer requests broadband or triple-play service to be available at a new residential location; DRO orchestrates the move with location-specific provisioning steps.
2. **Plan upgrade / change** — telecom customer upgrades from broadband to triple-play; DRO orchestrates the deactivation of the old service + activation of the new with minimal downtime.

### Design Time Configuration

> **Pilot — Customers must contact Salesforce to enable.**

> **Pre-requisite:** CME-DRO Interop must be configured in the org (Feature 5).

[NEEDS REVIEW] — full pilot enablement and configuration steps. Pull from master PDF and PM contact.

### Configuration and Runtime Video

📹 **"Demo of Move and Change Plan"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## QuantumBit data reference for DRO

`datasets/sfdmu/qb/en-US/qb-dro/` provisions design-time DRO configuration for the QB catalog: 17 objects in 1 pass.

### Provisioned Design-Time Records

| Object | Description |
|---|---|
| `FulfillmentStepDefinitionGroup` | Step groups for QB fulfillment scenarios |
| `FulfillmentStepDefinition` | Step definitions (e.g., "Provision QB Server", "Send Welcome Email") |
| `FulfillmentStepDependencyDef` | Dependencies between steps |
| `ProductFulfillmentDecompRule` | Decomposition rules (commercial → technical product mapping for QB bundles) |
| `ProductDecompEnrichmentRule` | Enrichment during decomposition |
| `ProductFulfillmentScenario` | Scenario rules linking QB products/classifications to fulfillment step groups |
| `FulfillmentFalloutRule` | Fallout queue and integration handlers |
| `FulfillmentStepJeopardyRule` | Time-based escalation rules |
| `FulfillmentTaskAssignmentRule` | Task assignment routing |
| `FulfillmentWorkspace` + `FulfillmentWorkspaceItem` | Workspace UI grouping |
| `ValTfrmGrp` + `ValTfrm` | Value transformation groups |
| `User` + `Group` | ReadOnly references for assignee resolution |

### Sample QB Fulfillment Scenarios

The QB DRO data plan provisions decomposition + orchestration flows for these scenarios:

[Author: list specific scenario names from `ProductFulfillmentScenario.csv` — e.g., "QB Complete Bundle Provisioning", "QB Database Token Provisioning", etc.]

### Notes on DRO + Usage products

QB's usage-rated products (e.g., `QB-DB`, `QB-TOKENS-PACK`) participate in DRO orchestration like any other product. **Cross-area constraint to remember:** DRO is incompatible with Swap/Upgrade/Downgrade for usage assets — those operations are blocked at the TM layer regardless of DRO setup (see Cross-Area Compatibility Constraints above).

---

## Cross-Area: TM Compatibility Constraint

**Primary home:** `260-transaction-management-hands-on.md` § Feature 7 (Swaps/Upgrades/Downgrades).

DRO is **not compatible with Swaps/Upgrades/Downgrades**. From the DRO perspective, customers using DRO for orchestration cannot use the swap/upgrade/downgrade amendment flow — they must model these as cancel + new transaction.

→ **Full constraint:** `260-transaction-management-hands-on.md` § Feature 7 (Swaps).

---

## Open questions for author / PM

1. **Demo URLs** — Solution Overview confirms recorded demos for: Decomposition Workspace, Pause External Callouts, Custom Logic Hook, Orchestrate Business Process, CME Interop, Move and Change Plan. Need actual URLs.
2. **Custom Logic Hook platform event** — confirm exact platform event name + request body for the Decompose Sales Transaction → custom logic → Orchestrate Sales Transaction flow.
3. **Orchestrate Business Process configuration** — exact context mapping setup steps + new IA input shape. Pull from master PDF.
4. **Move and Change Plan Pilot enablement** — what's the Pilot gating (BT org perm, Support case, etc.)? Need from PM.
5. **`update_product_fulfillment_decomp_rules` Apex bug** — `rlm-base-dev` runs this Apex script as a workaround for a 260 bug where `ExecuteOnRuleId` is not generated on `INSERT` and must be triggered by `UPDATE`. Should this be flagged in the customer-facing exercise as a known issue, or kept as repo-internal build remediation only?
6. **CME Interop transition path** — for customers currently on IOM (OM Std / OMPL), is there a documented migration path to DRO? Should the exercise include a comparison/migration callout?
7. **DRO + Usage product orchestration** — are there special considerations for orchestrating usage-rated products beyond the swap/upgrade/downgrade incompatibility? Any provisioning differences for token-rated vs. native-UoM-rated resources?
8. **End-to-end scenario** — should 260 add a stitched scenario combining Decomposition Workspace observation + Custom Logic Hook insertion + Pause Callouts during a simulated downtime window? Composed walkthrough would test all three new features together.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
