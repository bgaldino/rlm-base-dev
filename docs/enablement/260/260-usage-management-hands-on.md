---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Usage Management"
document_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag)"
  - "Rate Management + Usage Selling enabled (Salesforce Go automation in 260 — see Feature 1)"
  - "qb-rating data plan loaded (`prepare_rating` flow with `rating=true`) — provides 9 usage-rated products + 4 usage resources"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Usage Management (pp 996+) + § Manage Quotes and Orders → Usage selling (pp 825+)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — Usage Management Design & Selling section"
  - "docs/salesforce/260/feature-index.md — per-area feature inventory"
  - "datasets/sfdmu/qb/en-US/qb-rating/ — QuantumBit usage rating data plan"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
  - ".cursor/skills/revenue-cloud-data-model/domains/usage.md"
---

# Revenue Cloud — Usage Management

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog loaded. Usage Management exercises additionally require the `prepare_rating` flow run with `rating=true` and `qb=true` — this loads 9 QB usage-rated products, 4 usage resources, and supporting policies.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 Solution Overview deck and master Help PDF.** Configuration steps for Usage Product Validator and Consumption Agent are complete (verified against master PDF). Save Quote/Order Rates and Usage Assets From Order Item Action have Solution Overview content but minimal master-PDF coverage — flagged `[NEEDS REVIEW]` for org walkthrough validation.

> **Cross-area dependency:** Several Transaction Management features (Multiple Ramp Schedules, Multiple Ramped Asset Amendments, Swaps/Upgrades/Downgrades, Future-Dated Amendments) interact with usage products in specific ways. See the **Critical Compatibility Constraints** section below before authoring any walkthrough that mixes Usage Management + Transaction Management.

---

## Critical Compatibility Constraints (Usage + Transaction Management)

> ⚠️ **Read before constructing any walkthrough that involves usage assets going through quote-to-cash + amendment lifecycle.** Sourced from master PDF Asset Management section research.

| Workflow | Allowed for Usage Assets? | Notes |
|---|---|---|
| Standard Amend / Renew / Cancel (last ASP only) | ✅ Yes | Works as expected |
| Future-dated Amend / Renew / Cancel | 🚫 **Not allowed** | "You can't amend a usage-based product with a future-date change" (master PDF p 885+) |
| Swap / Upgrade / Downgrade | 🚫 **Not allowed** | "You can't swap, upgrade, or downgrade … usage-based assets" (master PDF p 882) |
| Transfer between accounts | ✅ Yes | Acts as amend with copy of ASP |
| In-Flight Order Changes | ✅ Yes | Carry-forward from 256 |
| Group Ramp + Usage + Amendment | ⚠️ **Known issue** | Net Unit Price Disappears (master PDF p 127) — see Known Issues |

**Implication for design-time walkthroughs:** when introducing usage products into deal scenarios, use selling models that don't require swap/upgrade/downgrade flows for amendment. If the demo needs swap-like behavior, model it as a cancel + new transaction instead.

---

## Carry-forward inventory (from prior releases)

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Token Based Selling | 256 | `docs/enablement/256/Summer '25 - Usage Management.pdf` | ✅ no change |
| Grant Binding | 256 | same | ✅ no change |
| Token Commitment Design & Selling | 256 | same | 🔄 **enhanced** in 258 (Quantity + Monetary Commitments) and 260 (Usage Product Validator coverage) |
| Quantity Commitments — Design & Selling Experience | 258 | `docs/enablement/258/Usage Management - Winter '26 Rev Cloud - External.pdf` | ✅ no change |
| Monetary Commitments — Design & Selling Experience | 258 | same | ✅ no change |

> The 258 Usage Management exercise was titled "Salesforce Feature Name" in its placeholder template (a draft artifact) — content is correct.

---

## Upgrade Guidance from Winter '26

> Customers upgrading from 258 (Winter '26) to 260 (Spring '26) — Rate and Usage Management require synchronization of any custom context definitions used for rating.

### Synchronize Custom Context Definitions for Rate Discovery and Rating Procedures

If you've extended the predefined `RateManagementContext` and `RatingDiscoveryContext` context definitions, you must synchronize them after upgrading to Spring '26.

**Affected:** customers with custom context definitions extending the standard rate management or rating discovery contexts.

**Steps:**

> **Permission required:** Customize Application + Modify All Data.

1. From Setup, in the Quick Find box, find and select **Context Definitions**.
2. In the **Custom Definitions** tab, select a custom definition that extends `RateManagementContext` or `RatingDiscoveryContext`.
3. In the **Sync Status** column, click **Sync Now**.
4. Save your changes.
5. Repeat for each extended context definition.

(Source: master PDF p 119, "Synchronize Custom Context Definitions for Rate Discovery and Rating Procedures")

---

## Known Issues for Spring '26

### Net Unit Price Disappears During Amendment of Usage Assets Created with Group Ramp

When editing the quantity or another field during amendment of usage assets created with group ramp, the **net unit rates** for usage quote line items / order line items can **disappear**. (master PDF p 127)

**Workaround:** Re-enter quantities after the disappearance. Alternatively, structure deals to avoid combining group-ramped + usage + amendment until the issue is resolved.

**Affected exercises:** any walkthrough that places a usage product in a group ramp and then amends the resulting asset.

---

## Release Overview

Salesforce Revenue Cloud Usage Management Design & Selling includes the following net-new features in Spring '26:

1. **Salesforce Go: Automation of Usage Selling & Rate Management Setup** — one-click enablement
2. **Usage Product Validator** — design-time validation of usage product setup with cross-entity checks
3. **Usage Selling: Save Quote/Order Rates** — preserve negotiated rates against subsequent catalog rate changes
4. **Usage Assets From Order Item Action** — automatically generate usage assets from order item actions
5. **Consumption Agent (Agentforce)** — agent-managed token resources for identifying overages and creating quotes

---

## Feature 1: Salesforce Go — Automation of Usage Selling & Rate Management Setup

> **Source:** Solution Overview "Salesforce GO: Automation of Usage selling & Rate Management setup" page.

### Business Objective

Customer admins previously spent significant time enabling Rate Management and Usage Selling features, walking through rate discovery procedure setups across multiple screens. Spring '26 brings this into the Salesforce Go automated setup framework: one-click enablement that triggers the full series of feature toggles + procedure setup behind the scenes.

### Use Cases

**Salesforce Admin / Implementation persona:**

- **Initial implementation** — when enabling Revenue Cloud from Salesforce Go, the framework also enables Rate Management + Usage Selling and sets up required procedures automatically.
- **Re-bootstrap after sandbox refresh** — re-running Salesforce Go reapplies the Rate Management + Usage Selling setup to the freshly refreshed org.

### Design Time Configuration

> **Permission required:** Salesforce Admin.

1. From Setup, find and open **Salesforce Go**.
2. From the Salesforce Go interface, locate **Revenue Cloud** in the available solutions.
3. Enable the Revenue Cloud setup; the framework triggers Rate Management + Usage Selling enablement as part of the setup sequence.

The Salesforce Go automation includes:

- Enabling Rate Management feature flag
- Enabling Usage Selling feature flag
- Setting up the required rate discovery procedure
- Activating supporting decision tables

> **Available in all editions** of Salesforce.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview lists this under the broader Salesforce Go demo (likely "Salesforce Go" as the parent demo).

---

## Feature 2: Usage Product Validator

> **Source:** Solution Overview "Usage Product Validator" page + master PDF "Validate Your Setup" / "Run the Usage Product Validator" / "Considerations for Usage Product Validator" (pp 1049–1051). Verified content.

### Business Objective

Customers setting up usage-based products often misconfigure the multi-entity design — products, usage resources, rate cards, grants, and policies all need to align, and a missing or misconfigured record at any layer breaks the runtime usage experience. Spring '26 introduces a **design-time validator** on the Product details page that checks the product's Usage and Rating objects and surfaces errors before the product enters quote-to-cash.

The validator is also exposed as an API supporting up to **10 products per query** for bulk validation in CI / org-prep workflows.

### Use Cases

**Catalog / Usage Designer persona:**

- **Verify a new usage product before activation** — after creating `QB-DB-TOKEN` (a token-rated database product) and its supporting records, run the validator to confirm all required design-time entities are aligned.
- **Catch missing rate card entries** — when the validator detects a rate card entry gap (e.g., 12-hour-or-greater gap between consecutive rate card entries for the same product usage resource), it surfaces a warning with a navigation link.
- **Bulk validate after a data migration** — after running the `qb-rating` data plan against a fresh org, use the API to validate up to 10 products at once.

### Validation Rules and Warning Thresholds

The validator enforces effectivity validation between the product usage resource and the rate card entry, **starting from the product usage resource's start date**. It surfaces warnings when the time difference between any of these record pairs exceeds **12 hours**:

- **Product usage resource gaps**: gap between two consecutive PUR records for the same usage resource
- **Rate card entry gaps**: gap between two consecutive rate card entries associated with a single PUR
- **Initial gap**: difference between PUR start date and the start date of the first associated rate card entry
- **Terminal gap**: difference between PUR end date and the end date of the last associated rate card entry (only checked if PUR has a defined end date)

> **Note:** if the usage model type of a product is changed *after* all associated objects are created, manually verify the associated objects before running the validator. Otherwise the validator can produce incorrect results.

### Design Time Configuration

> **Permissions required:** `Usage Management Design Time User` + `Rate Management Design Time User`.

**Pre-step — Add the validator to the product record page:**

The Usage Product Validator is a component that admins must add to the relevant Product record page layout. The product must have a usage model type for the validator to be relevant.

**Run the validator (UI):**

1. From the App Launcher, find and select **Products**.
2. Select a usage-rated product (e.g., `QB-DB`, `QB-DAT-THPT`, `QB-TOKENS-PACK` from the QB catalog).
3. On the product record page, under the **Usage Product Validator** component, click **Validate**.
4. Review the validation results — errors require remediation; warnings can be addressed at the user's discretion.

**Run the validator (API):**

The validator API supports up to 10 products in a single call. Useful for CI / org-prep validation.

[NEEDS REVIEW] — confirm exact API endpoint and request shape.

### QuantumBit walkthrough scenario

After loading the QB rating data plan:

1. Navigate to **QB-DB** (QuantumBit Database) — a usage-rated product with multi-resource rating (CPU time + Data Storage).
2. Add the Usage Product Validator component to the Product record page (one-time setup).
3. On QB-DB's record page, click **Validate**.
4. Verify a clean validation result.
5. (To demonstrate error handling) — temporarily deactivate one of the rate card entries for QB-DB → re-run validation → confirm the validator surfaces the rate card entry gap as a warning with a navigation link to the affected record.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview doesn't explicitly list a Usage Product Validator demo.

---

## Feature 3: Usage Selling — Save Quote/Order Rates

> **Source:** Solution Overview "Usage Selling: Save Quote/Order Rates" page. Master PDF coverage limited; the new feature appears to be primarily a `TransactionProcessingType` setting.

### Business Objective

Customers selling usage-based products want to **save the negotiated usage rates upon saving quotes and orders**, so subsequent changes to catalog rates don't impact the rate card associated with an existing quote/order. Without this feature, rates would always be re-read from the catalog at query time — meaning a catalog rate change retroactively affects any quote that references the same usage resource.

Spring '26 introduces a new `TransactionProcessingType` setting — `catalogRatePerf` — that controls this behavior:

- **Enabled (`catalogRatePerf = true`)** — every time a new quote or order is saved, the associated rate card entries are automatically saved with the quote/order. Subsequent catalog rate changes do not affect saved quotes/orders.
- **Disabled (`catalogRatePerf = false`)** — rates are always read from the catalog at runtime. Default behavior (legacy).

### Use Cases

**Sales Operations persona:**

- **Lock in negotiated rates** — when a sales rep negotiates favorable rates for a customer's QB-DB consumption (token rate card override), saving the quote captures those rates so a later catalog rate adjustment doesn't change the customer's contracted experience.

**Pricing Admin persona:**

- **Adjust catalog rates safely** — admins can update catalog rates for new business without worrying about retroactively changing existing quote/order pricing.

### Design Time Configuration

> **Permission required:** `Usage Management Design Time User` or equivalent admin permission with access to TransactionProcessingType records.

1. Navigate to the **TransactionProcessingType** records (Setup → Transaction Processing Types, or via Object Manager).
2. Locate the relevant transaction processing type.
3. Edit the record and enable the **`catalogRatePerf`** setting.
4. Save.

After enabling, every new quote or order save triggers automatic rate card entry capture.

[NEEDS REVIEW] — confirm exact navigation path in 260; the master PDF didn't surface detailed steps in initial extraction.

### QuantumBit walkthrough scenario

1. Confirm `catalogRatePerf` is enabled on the relevant TransactionProcessingType.
2. Create a quote with QB-TOKENS-PACK (token-rated) and save.
3. Verify rate card entries are captured with the quote (look for new rate card records or the saved-rate field on the quote line items).
4. Modify the catalog rate for the QB-TOKEN usage resource.
5. Re-open the saved quote — verify the rates from step 2 persist (don't change to reflect the modified catalog rates).

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 4: Usage Assets From Order Item Action

> **Source:** 260 highlights "Usage assets from order item action". Solution Overview Usage Management section.

### Business Objective

When usage products are sold and orders fulfill, **usage assets** must be created to track ongoing consumption against the contracted commitment. Spring '26 streamlines this — usage assets are generated automatically as part of the order item action workflow, eliminating a manual step in the assetization process.

### Use Cases

**Order Fulfillment persona:**

- **Automatic usage asset creation** — when an order containing usage products (e.g., QB-TOKENS-PACK + QB-DB) is activated, the corresponding usage assets and underlying tracking records (UsageEntitlementBucket, UsageEntitlementEntry, ProductUsageGrant linkage) are created automatically.

### Design Time Configuration

[NEEDS REVIEW] — the Solution Overview lists this as a feature but detailed configuration steps weren't extracted on initial scan. Likely automatic behavior triggered by order item action; may have a feature-flag toggle. Pull from a 260 org walkthrough.

### QuantumBit walkthrough scenario

1. Create a quote with QB-TOKENS-PACK (1 token pack) and QB-DB (database).
2. Convert the quote to an order.
3. Activate the order.
4. Verify that on activation:
    - A usage asset is created for QB-TOKENS-PACK
    - A usage asset is created for QB-DB
    - Underlying entitlement and grant records are populated correctly
5. Confirm the customer's account now shows the new usage assets in the Managed Assets viewer.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 5: Consumption Agent (Agentforce)

> **Source:** master PDF "Manage Token Overages for Quoting with Agentforce" (p 1329+). Verified content.

### Business Objective

Token-based usage models often have customers running into overage situations — they consume more tokens than their commitment covers. Identifying these overages and generating timely upsell quotes for additional token packs has historically been manual. The **Agentforce Consumption Agent** automates this: it monitors token resources, identifies overages at the account level, and assists in creating targeted quotes with token packs.

### Key Capabilities

- **Identifies token overages** at the account level
- **Assists in creating targeted quotes** with token packs, eliminating manual effort
- **Enables sales teams to easily upsell** token packs

### Use Cases

**Sales Rep persona:**

- **Proactive overage detection** — agent flags accounts where token consumption is approaching or has exceeded the committed allocation.
- **Quick upsell quote** — agent generates a targeted quote with a recommended token pack (e.g., QB-TOKENS-PACK) and pre-populates account/contract context.

### Example Utterances That Trigger This Topic

- *"I would like to get account usage details for Acme and Cloud Kicks."*
- *"What is the current consumption on my account?"*
- *"How many assets from Acme are with Overages?"*

### Design Time Configuration

> **Prerequisites:**
> - Einstein generative AI enabled
> - Agentforce enabled and configured
> - Rate Management enabled
> - Usage Management enabled
> - Token-based products configured (QB has `QB-TOKENS-PACK`, `QB-DB-TOKEN`, `QB-CMT-TKN-EACH`, `QB-CMT-TKN-FLAT`, `QB-CMT-TKN-TIER` for testing)

> **Permissions:** Wallet Management User + Usage Runtime user personas need same object permissions as Traceability.

> **Limitation:** the agent is available to **authenticated users in Lightning Experience** only. Customers and partners using Experience Cloud do not yet have access to external digital agents.

**Setup:**

1. Verify all four prerequisites are enabled in your org.
2. From Setup, find and configure the Consumption Agent topic in your Agentforce setup.
3. Assign the Wallet Management User and Usage Runtime user personas to the appropriate users with object permissions matching Traceability access.

[NEEDS REVIEW] — confirm exact agent topic configuration details from a 260 org. Master PDF gave overall capabilities and prerequisites, but detailed setup-screen walk-through wasn't fully extracted.

### QuantumBit walkthrough scenario

1. Confirm prerequisites: Einstein gen AI + Agentforce + Rate Management + Usage Management.
2. Create a customer Account with QB-TOKENS-PACK assetized (e.g., 1000 tokens committed).
3. Simulate token overage by modifying the underlying UsageEntitlementBucket balance to indicate the account has consumed >1000 tokens.
4. As a sales rep with the Consumption Agent permissions, ask the agent: *"What is the current consumption on my account?"*
5. Verify agent identifies the overage and offers to create an upsell quote.
6. Accept the quote suggestion; verify a new quote is generated with QB-TOKENS-PACK at the configured upsell quantity.

### Configuration and Runtime Video

[NEEDS REVIEW] — Agentforce demos may live in a separate Agentforce-specific solution overview deck.

---

## QuantumBit data reference for Usage Management

The QB rating data plan (`datasets/sfdmu/qb/en-US/qb-rating/`) provides 9 usage-rated products and 4 usage resources. This is the canonical setup for Usage Management exercises.

### Usage Resources

| Code | Name | Notes |
|---|---|---|
| `QB-TOKEN` | Quantum Tokens | Token-class resource, billed monthly total |
| `UR-CPUTIME` | Compute Time | Time-class resource, billed monthly total |
| `UR-DATASTORAGE` | Data Storage | Data-volume class resource, billed monthly peak |
| `UR-DATAXFR` | Data Throughput | Data-volume class resource, billed monthly total |

### Usage-Rated Products

| SKU | Product / Rating Model | Use for walkthroughs of |
|---|---|---|
| `QB-DB` | QuantumBit Database — multi-resource (CPU + Data Storage) | Multi-resource validation; complex amendment scenarios |
| `QB-DB-TOKEN` | QuantumBit Database (token rating) | Token-rated database; Consumption Agent tests |
| `QB-DAT-THPT` | Data Throughput product | Throughput-only billing; rate card validation |
| `QB-TOKENS-PACK` | Token Pack | Token allocation purchase; Consumption Agent upsell |
| `QB-CMT-TKN-EACH` | Commitment Tokens (per-token) | Quantity Commitments (carry-forward 258) |
| `QB-CMT-TKN-FLAT` | Commitment Tokens (flat) | Flat-fee commitment scenarios |
| `QB-CMT-TKN-TIER` | Commitment Tokens (tiered) | Tiered commitment scenarios |
| `QB-MTY-CMT` | Monetary Commitment | Monetary Commitments (carry-forward 258) |
| `QB-QTY-CMT` | Quantity Commitment | Quantity Commitments (carry-forward 258) |

### Supporting design-time records

The `qb-rating` data plan also loads:

- **Usage Resource Billing Policies** (`monthlytotal`, `monthlypeak`)
- **Usage Commitment Policies**
- **Usage Overage Policies**
- **Usage Grant Renewal Policies**
- **Usage Grant Rollover Policies**
- **Usage Product Grant Binding Policies**
- **Rating Frequency Policies**
- **Unit Of Measure Classes** (Token UoM Class, TIME, DATAVOL)
- **Units Of Measure** (TOKEN-UOM, m, TB, GB, etc.)

These are required for any usage product walkthrough; they're loaded automatically by `prepare_rating` flow.

---

## Cross-Area: Multiple Ramped Asset Amendments + Usage

**Primary home:** `260-transaction-management-hands-on.md` § Multiple Ramped Asset Amendments.

When ramped assets include usage-rated products (e.g., QB-DB in a multi-quarter ramp), amending those assets in 260 enables **multiple ramped asset amendments in a single transaction**. From the Usage Management perspective:

- Usage assets in ramp groups participate in the multi-asset amendment workflow.
- ⚠️ **Known issue alert:** when editing the quantity or another field during amendment of usage assets created with group ramp, **Net Unit Price disappears** — see Known Issues above. Plan walkthroughs to either avoid this combination or pre-warn users.

→ **Full configuration:** `docs/enablement/260/260-transaction-management-hands-on.md` § Feature 4.

---

## Cross-Area: Asset Lifecycle for Usage Assets

**Primary home:** `260-transaction-management-hands-on.md` § Features 7 + 8.

Usage assets have specific lifecycle constraints in 260:

- ✅ Standard amend / renew / cancel **on the last ASP** works as expected.
- 🚫 **Cannot use Swap / Upgrade / Downgrade** on usage-based assets.
- 🚫 **Cannot use future-dated amendments** on usage products.

For usage workflows that need swap-like behavior (e.g., changing rating model), model as **cancel + new transaction** rather than swap.

→ **Full constraints:** `docs/enablement/260/260-transaction-management-hands-on.md` § Feature 7 (Swaps/Upgrades/Downgrades) + § Feature 8 (Future-Dated Amendments).

---

## Open questions for author / PM

1. **Demo URLs** — Solution Overview Usage Management section doesn't explicitly call out per-feature recordings for: Usage Product Validator, Save Quote/Order Rates, Usage Assets From Order Item Action. Confirm with PM.
2. **Save Quote/Order Rates configuration** — exact navigation to `catalogRatePerf` TransactionProcessingType setting, and whether it's a true/false flag or has additional configuration. Master PDF didn't surface detailed steps; pull from 260 org.
3. **Usage Assets From Order Item Action** — automatic vs. opt-in? Solution Overview describes the behavior but not the toggle. Pull from 260 org.
4. **Consumption Agent topic configuration** — Agentforce topic API name + included agent actions. Pull from master PDF deeper extraction or Agentforce-specific solution overview deck.
5. **Usage Product Validator API** — exact API endpoint and request shape. Pull from master PDF or developer guide.
6. **End-to-end scenario** — should 260 add a stitched scenario combining Salesforce Go (Feature 1) + Validator (Feature 2) + Save Rates (Feature 3) + Auto-Asset (Feature 4) + Consumption Agent (Feature 5) into a single end-to-end usage selling demo? Solution Overview groups them sequentially under one umbrella; that suggests they compose well.
7. **Cross-area validation** — should a callout be added to TM Feature 7 (Swaps) explicitly listing what to do when a customer wants to swap a usage product (i.e., cancel + new transaction)? Adding it bidirectionally clarifies intent.
8. **262 forward-look** — Summer '26 (262) brings Usage Product Guided Setup + Usage Product Activation API + Consumption Agent enhancements. Should 260 mention these as upcoming, or stay 260-focused? Currently silent.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
