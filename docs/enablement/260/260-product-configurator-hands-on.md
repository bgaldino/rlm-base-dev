---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Product Configurator"
document_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag) — bundles configured (e.g., QB Complete, QB Starter)"
  - "Product Configurator enabled (Setup → Product Configurator → confirm enablement)"
  - "Product Discovery flow available (or custom Configurator flow in place if customized)"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Product Configurator (pp 562–646)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — Product Configurator section (pp ~25–37)"
  - "docs/salesforce/260/feature-index.md — per-area feature inventory"
  - "datasets/sfdmu/qb/en-US/qb-pcm/ — QuantumBit catalog with bundles and attributes"
  - ".cursor/skills/release-enablement/authoring-patterns.md — sub-feature handling pattern"
---

# Revenue Cloud — Product Configurator

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog loaded — including bundles (QB Complete, QB Starter, Professional Services Bundle) and 39 attribute definitions across 18 product classifications.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 release notes, Solution Overview deck, and master Help PDF.** Configuration Logs detailed setup is complete. UI Enhancement and Flexible Configuration features capture business intent and use cases; many configuration steps are flagged `[NEEDS REVIEW]` pending walkthrough in a 260 org with screenshots. Author should validate UI changes by configuring a QB bundle (e.g., QB Complete) and capturing screenshots before flipping `status: draft` → `status: review`.

> **Configurator-specific authoring note:** This area is screenshot-heavy. Several UI features (Compact Layout, Sticky Errors, Inline Attribute Configuration) are best demonstrated visually rather than narratively. The exercise structure below preserves the standard four-part sections, but readers should expect screenshot-driven walkthroughs once the doc reaches `status: review`.

---

## Carry-forward inventory (from prior releases)

The following Configurator features were introduced in 256 (Su'25) or 258 (W'26). They remain valid for 260 unless flagged otherwise. Readers should reference the prior-release exercise PDFs for full walkthroughs.

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Add Product from Catalog into Constraint Builder | 256 | `docs/enablement/256/Summer '25 - Configuration.pdf` | ✅ no change |
| Basic Logic Constraint | 256 | same | ✅ no change |
| Conditional Logic Constraints | 256 | same | ✅ no change |
| Message Rule | 256 | same | ✅ no change |
| Require Rule | 256 | same | ✅ no change |
| Preference Rule | 256 | same | 🔄 **enhanced** in 258 — see Preference Rule with Expression Grouping in `258/Product Configurator - Winter'26 Revenue Cloud - External.pdf` |
| Admin UI — Constraint Template Enhancements (flexible expression-building) | 258 | `docs/enablement/258/Product Configurator - Winter'26 Revenue Cloud - External.pdf` | ✅ no change |
| Support Product Component Groups in CML | 258 | same | ✅ no change |
| Visual Builder — new rule templates | 258 | same | ✅ no change |
| Dynamic Loader/Table Constraints | 258 | same | ✅ no change |
| Non-Blocking UI in the Configurator | 258 | same | ✅ no change |
| Rule-Based Product Recommendation (during Quote/Order) | 258 | same | ✅ no change |
| Product Centric Modelling (CML sync with product definitions) | 258 | same | ✅ no change |
| Preference Rule with Expression Grouping | 258 | same | ✅ no change |
| Exclude Rule | 258 | same | ✅ no change |
| Hide Attribute Values Rule | 258 | same | ✅ no change |
| Disable Components Rule | 258 | same | ✅ no change |

> The 258 Configurator exercise was titled "Salesforce Feature Name" in its placeholder template — that's a draft artifact, not the actual feature name. Use the document content (CML rules, constraint modeling, runtime UX) to identify what's covered.

---

## Upgrade Guidance from Winter '26

The master PDF "Upgrade Guidance for Spring '26" section (pp 115–117) does **not list a dedicated Product Configurator subsection**. PCM-area upgrade items (Discover Products flow update, Permission Set Group recalculation) affect the Configurator indirectly because Configurator runs inside the Product Discovery flow.

**Affected Configurator users:** customers with a custom Discover Products flow that wasn't updated during Winter '26.

→ **For details, see:** `docs/enablement/260/260-product-catalog-management-hands-on.md` § Upgrade Guidance from Winter '26 → Discover Products Flow Update.

If you've already completed the PCM upgrade guidance during the 260 PCM rollout, no additional Configurator-specific upgrade work is required.

---

## Release Overview

Salesforce Revenue Cloud Product Configurator includes the following net-new features in Spring '26:

1. **Configurator UI Enhancements**
    - **New Streamlined Compact Layout** — compact mode toggle for large bundles, with key fields fixed in position
    - **Fixed Position "Sticky" Error Messages** — persistently displayed at the top of the configurator modal, severity-tiered
2. **Flexible Configuration Experience**
    - **Edit Transaction Line Context Fields** — set/modify context fields directly within the configurator option card
    - **Inline Attribute Configuration for Bundle Components** — configure component attributes directly inside the option card, no separate-screen navigation
    - **Enhanced Instance Selection and Cloning** — create multiple instances with a single click + clone configured instances
3. **Translation Support for Error Messages** — localized configurator error messages
4. **Configuration Logs** — opt-in detailed logs for monitoring and troubleshooting product configuration performance, viewable in the Revenue Cloud Operations Console

---

## Feature 1: New Streamlined Compact Layout

> **Source:** Solution Overview "New Streamlined Compact layout" page. Sub-feature of *Configurator UI Enhancements* per the Solution Overview's grouping.

### Business Objective

The default configuration layout for large bundles displays a limited number of options without scrolling. This hinders users' ability to compare options effectively — they must scroll to view the complete set of components, losing visual context.

The compact mode toggle introduces a denser, more efficient layout for large bundles. Key fields (Product Name, Quantity, Selling Model, Price) stay fixed in position so the user always has a consistent reference point; additional custom fields are accessed by expanding individual option cards on demand.

### Use Cases

**Sales Rep persona:**

- **Compare options across a 10+ component bundle** — open the QB Complete bundle in compact mode and quickly scan all components without losing track of which products are selected vs. which are still pending review.
- **Configure a multi-tier server bundle** — toggle compact mode on the QB Server bundle (with 5+ component categories: CPU, Memory, Storage, Network Adapter, Cables) and assess each option's quantity and price side-by-side.

### Design Time Configuration

[NEEDS REVIEW] — confirm in 260 org. Approximate flow based on Solution Overview text:

1. From Setup → Product Configurator settings (or the Configurator flow setup), locate the **Compact Mode Toggle** setting.
2. Enable compact mode for the relevant configurator deployment (org-wide, per-flow, or per-record-type — confirm scoping in 260).

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview licensing matrix doesn't list a dedicated demo for this feature; likely covered in a combined Configurator UI Enhancements walkthrough. Confirm with PM.

---

## Feature 2: Fixed Position "Sticky" Error Messages

> **Source:** Solution Overview "Fixed Position 'Sticky' Error messages" page. Sub-feature of *Configurator UI Enhancements*.

### Business Objective

Sales users configuring large bundles with many components had to scroll down constantly to view all available options — and as they did, error messages disappeared off-screen. They lost visibility of important configuration errors during the very task that produced them.

Spring '26 introduces a persistent Error Message component, displayed at the top of the configurator modal as a fixed-position panel. Error messages remain visible regardless of scroll position. Messages are tiered by severity (Error / Warning / Info), and users can expand the message pane for detail or collapse it to maximize configuration space.

### Use Cases

**Sales Rep persona:**

- **Configure a constrained bundle** — when configuring the QB Complete bundle with active constraint rules (Require Rules, Preference Rules), see all triggered errors without scrolling back to the top.
- **Understand multi-message resolutions** — when several rules fire simultaneously (e.g., a Require Rule firing alongside a Hide Attribute Values Rule), see severity-grouped messages so the most important issues are addressed first.

### Design Time Configuration

The new Error Message component is **available by default** — no configuration required to enable. Optional admin behaviors:

1. The default position is fixed/sticky at the top of the configurator modal.
2. Users can expand the message pane to see detail or collapse it.
3. Severity grouping (Error / Warning / Info) is automatic based on rule definitions in CML.

[NEEDS REVIEW] — confirm whether admins can customize the component's position or default-collapsed state.

### Configuration and Runtime Video

[NEEDS REVIEW] — likely covered in combined Configurator UI Enhancements walkthrough.

---

## Feature 3: Edit Transaction Line Context Fields

> **Source:** Solution Overview "Edit transaction line context fields" page. Sub-feature of *Flexible Configuration Experience*. Builds on the existing capability to add Sales Transaction Item context fields to the option card via flow settings.

### Business Objective

Sales reps previously experienced a disjointed configuration process — they had to navigate across multiple screens to input supplementary product-specific context fields (e.g., service location, start date, custom attributes that aren't in CML). Spring '26 enables sales users to set or modify Sales Transaction Item context field values **directly within the configurator option card during product configuration**.

Custom fields added to the configurator flow setup become editable based on their data type — text fields edit inline, picklists open dropdowns, dates pick via date picker.

### Use Cases

**Sales Rep persona:**

- **Set the deployment location for a product during configuration** — when configuring a QuantumBit Server, set the data center location directly in the option card without exiting to the Quote line item.
- **Set the start date for a subscription product** — when configuring a QB Automation subscription, pick the activation date directly in the configurator.

### Design Time Configuration

> **Permission required:** Flow Builder access; Product Configuration Designer.

Pre-requisite — Sales Transaction Item context fields must already be added to the option card via flow settings (existing capability, not new in 260).

In 260:

1. Open the Product Configurator flow in Flow Builder.
2. Locate the option card configuration (within the configurator flow setup).
3. Custom fields added to the option card become editable by default in 260.
4. Field type determines the editor: text → inline text input, picklist → dropdown, date → picker, checkbox → toggle.

### QuantumBit walkthrough scenario

1. From the QB catalog, select a **QuantumBit Server** product.
2. Open the configurator.
3. In the option card for a Memory component, set a custom Sales Transaction Item context field (e.g., `RackPosition__c` if added to the flow setup).
4. Save the configuration; verify the field value persists on the resulting Quote Line Item.

### Configuration and Runtime Video

[NEEDS REVIEW] — likely covered in combined Flexible Configuration Experience demo.

---

## Feature 4: Inline Attribute Configuration for Bundle Components

> **Source:** Solution Overview "Inline Attribute Configuration for bundle components" page. Sub-feature of *Flexible Configuration Experience*.

### Business Objective

Sales Reps configuring bundles with multiple components had to navigate to a separate screen for each component to configure its attributes — leading to many clicks and a fragmented view of selections across components. Spring '26 enables inline attribute configuration directly within the option card, so admins can let sales users configure component attributes without leaving the options screen.

Best for bundles with several components and a small number of attributes per component (≤5).

### Use Cases

**Sales Rep persona:**

- **Configure a bundle with attribute-rich components** — when configuring QB Server bundle, set processor speed, memory size, and storage type for each component without navigating to separate attribute screens.

### Design Time Configuration

> **Permission required:** Admin (Flow Builder access). Inline attribute configuration is opt-in per option card.

1. Open the Product Configurator flow in Flow Builder.
2. Locate the **option card flow setting** for the bundle.
3. Enable **Inline Attribute Configuration** for the option groups where it should apply.
4. Save and activate.

### Performance recommendation

Use inline attribute configuration when components have **fewer than 5 attributes**. With more attributes, the option card becomes cluttered and the separate-screen approach is preferable.

### QuantumBit walkthrough scenario

1. From the QB catalog, select **QB Complete** bundle (or another QB bundle with attribute-rich components).
2. Enable inline attribute configuration in the configurator flow for this bundle's option groups.
3. Open the configurator at runtime — verify that selected components display their attribute editors directly in the option card.
4. Configure a component's attributes inline; save; verify attribute values persist on the resulting Quote Line Item.

### Configuration and Runtime Video

[NEEDS REVIEW] — combined Flexible Configuration Experience demo.

---

## Feature 5: Enhanced Instance Selection and Cloning

> **Source:** Solution Overview "Enhanced instance selection and cloning configured instances" page. Sub-feature of *Flexible Configuration Experience*.

### Business Objective

Sales Reps previously needed to add and configure each product instance individually — repetitive, time-consuming, and error-prone for deals requiring the same product at multiple sites or in multiple configurations. Spring '26 introduces:

- **Multi-instance creation**: specify a desired quantity and create multiple instances of a product with a single click
- **Clone configured instance**: take an already-configured instance and clone its selections to a new instance, then optionally tweak

### Use Cases

**Sales Rep persona:**

- **Deploy QB Server to 5 office locations** — create 5 instances at once, then customize per-location attributes (location name, network configuration).
- **Clone a complex bundle configuration** — configure a QB Complete bundle for the first office, clone it to apply to the next 4 offices, and adjust per-office details.

### Design Time Configuration

> **Permission required:** Admin (Product Configurator flow setup).

Enabled in the **option groups section** of the product configurator flow setup:

1. Open the Product Configurator flow.
2. Locate the option groups section.
3. Enable **Instance Selection** and **Cloning of Instances** for the option groups where this should apply.
4. Save and activate.

### Runtime behavior

- Sales users get a quantity selector: enter a number (e.g., 5) → click → 5 instances are created.
- After configuring one instance, the **Clone** action duplicates all selections to a new instance for further editing.

### QuantumBit walkthrough scenario

1. From the QB catalog, navigate to a multi-instance-suitable product (e.g., QuantumShell rack accessories or QB Servers for a multi-site deployment scenario).
2. Enable Instance Selection + Cloning for the relevant option group.
3. At runtime, create 5 instances at once.
4. Configure the first instance; clone to instance 2; adjust one attribute.
5. Save the configuration; verify all 5 instances appear as separate Quote Line Items with the expected per-instance attributes.

### Configuration and Runtime Video

[NEEDS REVIEW] — combined Flexible Configuration Experience demo.

---

## Feature 6: Translation Support for Error Messages

> **Source:** Solution Overview "Translation Support for Error Messages" header (full content not extracted on initial scan; the section title appears in the deck without a detailed Customer Need / Solution paragraph in my extraction).

### Business Objective

Configurator error messages (raised by Constraint Rules, Require Rules, Hide Attribute Values Rules, etc.) were previously surfaced in the configurator's default language. Spring '26 adds support for **localized error messages**, so sales users in different locales see error messages translated into their language.

This pairs with the broader Translation Workbench / multilingual support already in PCM (data translation for catalog, category, attribute, and picklist values introduced in 258).

### Use Cases

**Catalog / Configurator Designer persona:**

- **Localize constraint rule messages for a multi-region rollout** — translate the error/warning messages associated with constraint rules so sales reps in France, Germany, and Japan see them in their language.

### Design Time Configuration

[NEEDS REVIEW] — likely uses the existing Translation Workbench mechanism applied to constraint rule messages. Pull from master PDF or 260 org walkthrough.

Approximate flow (based on the existing Translation Workbench pattern from 258):

1. From Setup → Translation Workbench → Translation Language Settings, enable the target languages.
2. From Translation Workbench → Translate, select the target object/field (constraint rule messages — confirm exact label in 260).
3. Provide translations for each rule's message text.
4. Save; verify users in the target locale see translated messages at runtime.

### QuantumBit walkthrough scenario

1. Configure a Constraint Rule with a Message Rule (existing 256 capability) that fires when invalid component combinations are selected on QB Complete bundle.
2. Add a French translation for the rule's message text via Translation Workbench.
3. Switch user locale to French.
4. Reproduce the constraint violation; verify the French translation displays.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview doesn't explicitly name a dedicated demo for translation support; may be covered in a broader localization demo or PCM data translation demo.

---

## Feature 7: Configuration Logs

> **Source:** master PDF "Set Up Product Configuration Logs" + "Turn On Configuration Logs" (pp 1452–1453). Solution Overview header lists this as a 260 enhancement; full setup steps captured below.

### Business Objective

Customers troubleshooting configurator behavior previously had limited visibility into runtime decisions — particularly for complex bundles where multiple constraint rules fire and interact. Spring '26 introduces **Configuration Logs**, opt-in detailed logs that monitor and troubleshoot product configuration performance. Logs surface in the Revenue Cloud Operations Console (renamed in 260 from Pricing Operations Console) for unified diagnostic access.

### Use Cases

**Configurator Designer / Configuration Admin persona:**

- **Diagnose unexpected runtime behavior** — when a constraint rule fires unexpectedly during configuration of QB Complete, enable Configuration Logs to capture the decision path and identify which rule conditions evaluated truthy.
- **Performance analysis on complex bundles** — when a 50+ component bundle takes longer than expected to configure, capture timing data via Configuration Logs to isolate slow rule evaluations.

### Design Time Configuration

> **Permission required:** Product Configuration Constraints Designer (initial setup); the new `Read and write configuration logs` user permission for those who'll view logs.

**Setup is a 6-step process — the first 3 steps create the user permission, and the last 3 set up the Decision Explainer framework that powers the logs.**

#### Step 1 — Create permission set

1. From Setup, in the Quick Find box, enter `Permission Sets` and select it.
2. Create a new permission set.
3. Assign the **Product Configuration User** user license to the permission set.

#### Step 2 — Enable the log permission

In the new permission set, enable the **Read and write configuration logs** user permission. Save.

#### Step 3 — Assign to users

Assign the permission set to the users who will configure or view configuration logs.

#### Step 4 — Configure Decision Explainer setup objects

From Setup, open **Decision Explainer**. Provide values for these setup objects:

- **Application Subtype Definition**: Label = `SolverPath`, Developer Name = `SolverPath`
- **Business Process Type Definition**: Label = `SolverPath`, Developer Name = `SolverPath`
- **Application Usage Type**: select **Explainability Service**

#### Step 5 — Configure Explainability Action Definition

- **Label**: `SolverPath`
- **Developer Name**: `SolverPath`
- **Business Process Type**: `SolverPath`
- **Application Type**: `Industry Service Excellence`
- **Application Subtype**: `SolverPath`
- **Action Log Schema Type**: `Other`

#### Step 6 — Create Explainability Action Version

- **Label**: `SolverPath`
- **Explainability Action Definition**: `SolverPath`
- **Active**: yes

Save all configurations.

### Turn On Configuration Logs

After setup, configuration logs become available in the **Revenue Cloud Operations Console** app. From the App Launcher, find and select **Revenue Cloud Operations Console** → navigate to the configuration log section to view captured data.

### QuantumBit walkthrough scenario

1. Complete the 6-step setup above against your dev/sandbox org.
2. Open the QB Complete bundle in the configurator at runtime.
3. Trigger a complex configuration that exercises Constraint Rules + Hide Attribute Values + Require Rules.
4. Save the configuration.
5. Open Revenue Cloud Operations Console → Configuration Logs section → find the captured log for the just-saved configuration → review the decision path.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview doesn't explicitly name a Configuration Logs demo. May be covered in a broader debugging/observability demo, or may not have a dedicated recording for this cycle.

---

## QuantumBit data reference

Configurator exercises depend on QB bundles. Source: `datasets/sfdmu/qb/en-US/qb-pcm/`.

### QB Bundles available for Configurator walkthroughs

[Author: confirm exact product names from `Product2.csv` filtered to bundle parents.]

Suggested canonical bundles for each feature:

| Feature | Suggested QB bundle |
|---|---|
| Compact Layout | QB Complete (multi-component infrastructure bundle) |
| Sticky Errors | QB Complete with active Constraint Rules |
| Inline Attribute Configuration | QB Server (CPU + Memory + Storage + NIC) |
| Enhanced Instance Selection | QuantumShell rack accessories (multi-instance use case) |
| Configuration Logs | Any complex bundle — QB Complete or QB Server |

### QB Constraint Rules

[Author: list constraint rules currently provisioned by the QB data plan, if any. Reference `qb-pcm` data plan + any apex-deployed constraints.]

### QB Attribute Categories (18)

[Author: list from `AttributeCategory.csv` — relevant for Inline Attribute Configuration walkthroughs.]

---

## Cross-Area: Constraint Rules in Product Discovery (262 preview)

> Not a 260 feature; included here as forward-looking context.

The 262 (Summer '26) preview adds **"Constraint Rules in Product Discovery"** — promoting constraint rules from the Configurator into the Product Discovery flow itself. For 260 readers: the constraint rules you build in the 260 Configurator using CML will become reusable in 262 Product Discovery without re-implementation.

→ **Future detail:** `docs/salesforce/262/feature-index.md` § Product Catalog & Discovery.

---

## Open questions for author / PM

1. **Demo URLs** — Solution Overview licensing matrix doesn't explicitly list per-sub-feature demos for Configurator UI / Flexible Configuration Experience. Are these covered by combined demos, or do individual demos exist that weren't called out in the matrix?
2. **Compact Mode Toggle scoping** — confirm whether compact mode is org-wide, per-flow, per-record-type, or user-preference. Solution Overview describes the toggle without specifying scope.
3. **Translation Support detail** — full translation flow not extracted. Pull from master PDF Translation Workbench section + Configurator-specific translation guidance, or walk through in 260 org.
4. **Configuration Logs `SolverPath` naming** — the master PDF instructs `SolverPath` as the literal value for multiple setup fields. Is this required? Or is it a placeholder name customers can change? Worth confirming, since the literal-value pattern is unusual.
5. **QB Constraint Rule provisioning** — does `rlm-base-dev` deploy any sample CML constraint rules with the QB catalog, or do users need to build them as part of the exercise? Affects walkthrough scenarios across multiple features.
6. **End-to-end Configurator scenario** — should 260 add a stitched scenario that exercises Compact Layout + Sticky Errors + Inline Attributes + Cloning together? Solution Overview features are sub-feature-grouped; demo wise, that grouping suggests the deck pictures them as composing well.
7. **258 carry-forward features** — many are constraint-modeling capabilities (CML, Visual Builder, Dynamic Loader) that don't have analogues in 260. Are they fully stable, or are any deprecating/changing in 262 that we should pre-flag for 260 readers?

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
