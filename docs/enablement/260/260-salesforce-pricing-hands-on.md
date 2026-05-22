---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Salesforce Pricing"
document_version: 0.5
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag)"
  - "Default pricing procedure deployed and active"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium (1,460 pages)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — internal Solution Overview deck (127 pp, CONFIDENTIAL)"
  - "docs/salesforce/260/release-notes-pricing.md — captured release notes"
  - "https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_pricing.htm&release=260&type=5"
---

# Revenue Cloud — Salesforce Pricing

**Enablement Exercises** · Version 0.5 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in the Spring '26 release. The Help portal uses both names interchangeably during the transition. This exercise series will continue to say "Revenue Cloud" for the 260 cycle to match what users see in the product UI; we'll re-evaluate per-release.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog loaded — 162 products across 28 PCM objects with structured attributes, classifications, and bundles.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 release notes and master Help PDF.** Configuration steps for each feature are sourced from the master PDF (page references included). Areas still needing user input are flagged inline with `[NEEDS REVIEW]`. Author should walk through each feature in a 260 org to confirm the steps and capture screenshots before flipping `status: draft` → `status: review`.

---

## Carry-forward inventory (from prior releases)

These features were introduced in 256 (Su'25) or 258 (W'26). They remain valid for 260 unless flagged otherwise. Readers should reference the prior-release exercise PDFs for full walkthroughs.

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Pre/Post Apex Hook for Procedure Plan | 256 | `docs/enablement/256/Summer '25 - Salesforce Pricing.pdf` | ✅ no change |
| Price Tracking — Maximum Price | 256 | same | ✅ no change |
| Multiple Output Resolution — Stacking & Sequencing | 256 | same | ✅ no change |
| Dynamic Output Mapping | 256 | same | ✅ no change |
| Pricing Simulation Screen Enhancement | 256 | same | ✅ no change |
| Cumulative Quantity Usage in Pricing Procedure | 256 | same | ✅ no change |
| Pricing Analytics | 256 | same | ✅ no change |
| Header Adjustments / Discount Distribution Service | 258 | `docs/enablement/258/Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf` | ✅ available — note: the Winter '26 doc called this "Header Adjustments"; Spring '26 docs use "Discount Distribution Service" |
| Price Revision Policy & Element for CPI Uplifts | 258 | same | ✅ no change |
| Enhanced Formula Element (multiple formulae) | 258 | same | 🔄 **enhanced** in 260 — see Feature 4 (Conditional IF Statements) below |
| Enhanced Pricing Performance for Large Transactions | 258 | same | 🔄 **enhanced** in 260 — same lineage as the 260 **15K Line Scale (Beta)** feature, whose primary home is `260-transaction-management-hands-on.md`. The 258 description was the early framing; 260 brings explicit 15K Beta capability for both pricing and configuration on large quotes/orders. See cross-area note below. |

---

## Upgrade Guidance from Winter '26

> Customers upgrading from 258 (Winter '26) to 260 (Spring '26) — review these transitional actions before assuming the carry-forward features in this area work as expected. Source: master PDF "Upgrade Guidance for Spring '26" section.

### Procedure Plan migration is now supported

Prior to 260, the Salesforce Help docs explicitly stated *"You can't migrate Procedure Plans from one org to another"* (Considerations for Importing and Exporting Pricing Data, master PDF p 342). **Spring '26 lifts that restriction** — see Feature 2 below for the new packaging capability. Customers who built procedure plans in sandbox and were blocked from promoting them to production can now do so via standard packaging flows.

> *Note: master PDF dated 2026-01-15 still contains the outdated "can't migrate" note. Public release notes confirm 260 GA removes the limitation.*

---

## Known Issues for Spring '26

These ship with 260 GA. Call them out in any walkthrough that exercises the affected areas so customers don't escalate them as bugs.

### Limitation with Price Propagation Element

Intermittent Pricing API failures occur when using **Price Propagation + Pricing Setting elements together**, when the procedure is configured *without a change set* and *context reuse is disabled*. Throws `ClassCastException: CacheableDataColumn cannot be cast to CacheableMetaColumn` at the Context Layer. **Workaround:** retry the pricing request. (master PDF p 117)

### Instant Pricing API returns additional records for ARC use cases

When invoked headlessly with **API v66.0**, the Instant Pricing API response can include cancellation lines, ARC breakdown lines, ARC detail lines, and quote summary fields that earlier API versions didn't return. **Action:** integrations dependent on prior response shape should not upgrade their API version. (master PDF p 118)

### Canceling derived pricing products results in incorrect net total price

After upgrading to Spring '26, canceling or amending a derived pricing product can produce an incorrect net total. **No workaround currently available.** (master PDF p 118)

---

## Release Overview

Per the 260 Solution Overview deck, the Spring '26 Price Management release enhancements are:

1. **Promotions — Define and Apply** *(Beta)*
2. **Promotions Visibility at Runtime** *(Beta)*
3. **Price Propagation** *(GA)* — nested groups + horizontal calculations
4. **Pricing Propagation Preview — Nested Groups** *(GA)* — design-time preview/setup tooling for the propagation table
5. **Easier debugging for multiple occurrences of same element** *(GA)* — auto-numbered element names in pricing procedures
6. **If-Else Formula** *(GA)* — IF() formula support in Formula-Based Pricing
7. **Advanced Logging** *(GA)* — detailed logs for attribute pricing, promotions, propagation, derived pricing

Plus the rename: **Pricing Operations Console is now Revenue Cloud Operations Console**.

> **Recorded demos exist for 260 Pricing** — confirmed in the Solution Overview licensing matrix:
> - "Price Propagation Demo"
> - "Promotions Demo"
> - "If Else Formula, Auto-numbering demo"
>
> [NEEDS REVIEW] — get the actual demo URLs from the PM team for embedding/linking.

---

## Feature 1: Streamline Complex Quote Calculations with Smarter Price Propagation

> **Source:** master PDF, "Price Propagation" section (~p 416–419 of the source PDF / extracted lines 21850–22100). Verified content.

### Business Objective

Complex deals — building automation, multi-floor leasing, telecom installations — model their pricing as nested hierarchies (Building → Floor → Room → line items). Pricing reps need totals, discounts, and margins to roll up automatically through every level, and within each line they need calculations that flow horizontally across fields (e.g., Net Price = List Price − Discount − Margin).

The Spring '26 Price Propagation enhancements deliver:

- **Ascending Propagation (Rollup)** — aggregate values from child lines to parent groups (sum, possibly filtered by conditions like `SellingModelType = 'One Time'`).
- **Horizontal Propagation** — calculate fields sequentially within a single line or group, so dependent fields (e.g., Net Price) compute only after their inputs (Unit Cost, Margin) resolve.
- **Up to 5 levels of nesting** in a single quote hierarchy.

### Use Cases

**Pricing Designer persona:**

- **Roll up panel net prices into building totals** — for a Building (Group) → Floor (Subgroup) → Room (Subgroup) → Panel (Line Item) hierarchy, calculate each panel's Net Price = List Price − Discount, then sum panel net prices into a Room Total, Room Totals into a Floor Total, and Floor Totals into a Building Total.
- **Filter rollups by selling model** — when summing child costs, exclude line items whose `SellingModelType ≠ 'One Time'` (configurable via up to 3 filter conditions per merged attribute).

### Design Time Configuration

> **Important constraints (from Help):**
> - One Price Propagation element per pricing procedure max.
> - Not compatible with Derived Pricing or Promotions elements in the same procedure.
> - Not supported inside a List Group.
> - If Delta Pricing is enabled, copy the Net Unit Price into a tag *before* the propagation element runs.

1. Open an existing pricing procedure or create a new one. Confirm it does not already contain a Price Propagation, Derived Price, or Promotion element.
2. Click **+** to add the Pricing Setting element. Select **Enable Propagation** and map your common variables.
3. In the Pricing Setting element, under **Propagation Setting**, select **Configure Propagation Rules**.
4. In the Configure Propagation Table window, choose:
   - **Configure a new table** — define nodes, joins, and formulas from scratch, OR
   - **Select a template** — *Map SalesTransactionItem to SalesTransactionGroup*, which pre-maps SalesTransactionItem records to SalesTransactionGroup using the predefined Sales Transaction Context.
5. **Add Nodes** — add `SalesTransactionItem` and `SalesTransactionGroup` with their attributes (e.g., `ItemDiscountPercentage`, `ListPrice`, `ItemUnitCost__std`, `ItemNetTotalPrice`, `ItemTotalMarginAmount__std`, `SalesTransactionItemGroup` from items; `GroupDiscount__std`, `SummarySubtotal`, `GroupTotalMarginAmount__std`, `GroupSource` from groups).
6. **Join Nodes** — define parent-child relationships:
   - Mapping Type: `Parent-Child`
   - Parent Key: `GroupSource`
   - Child Key: `SalesTransactionItemGroup`
   - Node Identifier: a unique tracking value
7. **Merge Attributes** — create merged columns for shared parent/child data, e.g., `Merged_header_1` with merge condition *Not Null*, attributes `GroupTotalMargin_std` and `ItemTotalMargin_std`.
8. **Edit Attributes** — define horizontal formulas:
   - Pick the column to calculate (e.g., Net Unit Price)
   - Enter the formula (e.g., `UnitCost + MarginAmount`)
   - Set a sequence number (1, 2, …) — sequence is mandatory, must be unique per formula, must be manually adjusted if you reorder.
   - Set **Use Zero for Null Values** if you want null inputs treated as 0.
9. Define **Ascending Propagation** to roll up values:
   - Create a merged attribute (e.g., `Merge Total Cost`)
   - Aggregation function: `Sum`
   - Specify the child field: `Sum(!Child.ItemTotalCost)`
   - (Optional) Filter children by up to 3 conditions (e.g., `SellingModelType = 'One Time'`).
10. Save the Propagation Rules.
11. Add the **Price Propagation** element to the procedure.
12. Save and Activate the procedure.

### Configuration and Runtime Video

[NEEDS REVIEW] — confirm whether a 260 recording is being produced or if the Help embed is sufficient.

### QuantumBit walkthrough scenario suggestion

[NEEDS REVIEW] — author/PM input needed: the QB catalog has 162 products including bundles, but doesn't natively model a Building/Floor/Room hierarchy. Either (a) pick a different QB scenario that genuinely needs nested groups, or (b) introduce a temporary demo data overlay specifically for this exercise.

---

## Feature 2: Package Your Pricing Workflow Seamlessly

> **Source:** Spring '26 release notes (https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_pricing.htm&release=260&type=5). Master PDF dated 2026-01-15 still contains an outdated note saying procedure plans can't be migrated — release notes confirm 260 GA lifts that restriction.

### Business Objective

Migrating pricing logic between orgs (sandbox → UAT → production) historically required some manual recreation. Pricing recipes, decision tables, and context definitions could already be packaged. **What's new in 260:** procedure plans can now be packaged too — the missing piece. The entire execution flow of pricing and discovery procedures transfers atomically.

### Use Cases

**Salesforce Admin / Release Manager persona:**

- **Promote a validated pricing solution from sandbox to production** — after configuring a procedure plan in sandbox, add it to a change set or unmanaged package, deploy, and the target org has the same pricing flow available immediately.

### Design Time Configuration

> **Important historical note:** Prior to 260, the Salesforce Help docs explicitly stated "You can't migrate Procedure Plans from one org to another" (Considerations for Importing and Exporting Pricing Data, master PDF p 342). Customers who hit that limitation should note the 260 release lifts it.

The pre-260 packaging flow already supported recipes, decision tables, context definitions, and procedures (using Package Manager → Components tab → Add → select component types). 260 simply extends the supported component list to include Procedure Plans.

[NEEDS REVIEW — confirm the specific component-type label that exposes Procedure Plans in Package Manager. Pull from a 260 org or wait for an updated Help doc.]

### Configuration and Runtime Video

[NEEDS REVIEW — likely no dedicated demo for this incremental enhancement; release-notes-style callout may suffice.]

---

## Feature 3: Troubleshoot Pricing Elements with Advanced Price Log Settings

> **Source:** master PDF, "Set Up Advanced Price Logs" (lines 75300+ in extracted text, around p 1448 of source PDF). Verified.

### Business Objective

When a pricing procedure produces an unexpected result, admins need to see *what each element did with its inputs*. Standard logs show the sequence of executions; **Advanced Price Log Settings** capture input values and exception details for the most logic-heavy elements (Attribute-Based Price, Derived Price, etc.) — turning opaque "wrong number" reports into actionable root-cause data.

### Use Cases

**Pricing Admin persona:**

- **Diagnose an Attribute-Based Price misfire** — when a discount tier returns the wrong percentage for a specific product attribute combination, enable advanced logs for that element and re-run the API call to see the full input context evaluated against the rule.
- **Identify performance bottlenecks** — exception details and timing data help isolate which element in a long procedure is consuming disproportionate runtime.

### Design Time Configuration

> **Permission required:** Salesforce Pricing Admin

1. From Setup, in the Quick Find box, find and select **Salesforce Pricing**.
2. Under Salesforce Pricing, select **Advanced Price Log Settings**.
3. [NEEDS REVIEW — confirm exact sub-step list from master PDF; the text I have ends at the navigation step. Pull the rest from `revenue-cloud-spring-26-2026-01-15.pdf` page 1448–1450.]

### Configuration and Runtime Video

[NEEDS REVIEW]

### Where to view the resulting logs

After Advanced Price Logs are on:

1. From the App Launcher, find and select **Revenue Cloud Operations Console** (renamed from Pricing Operations Console — see Feature 6).
2. Select a pricing log from the list of API executions.
3. Open the **Debug Details** tab to see element-level execution detail including the new advanced data.

---

## Feature 4: Build Pricing Logic with Conditional IF Statements

> **Source:** Solution Overview deck "If-else formula" section. Concrete example provided.

### Business Objective

Pricing calculations often leverage complex conditional logic. Lack of IF support in the formula element historically forced workarounds (chained elements, custom Apex). Spring '26 adds native `IF()` formula support inside Formula-Based Pricing, letting designers express conditional logic in a single readable formula.

### Use Cases

**Pricing Designer persona:**

- **Apply premium pricing based on Sale Type** — if `SaleType = "Premium"`, multiply list price by a premium factor; otherwise apply regular price.

### Design Time Configuration

1. Open or create a pricing procedure that includes a Formula-Based Pricing element.
2. In the formula expression, search for the **`IF()`** function.
3. Provide three parameters:
   - **Logical condition** — the test expression
   - **Value if true** — output when the condition evaluates true
   - **Value if false** — output when the condition evaluates false

**Concrete example from the Solution Overview:**

```
IF(SaleType = "Premium", ItemListPrice__c * ItemPremium__c / 10000, ItemListPrice__c)
```

This formula multiplies `ItemListPrice__c` by `ItemPremium__c / 10000` (basis-point math) when `SaleType` is "Premium", and falls back to `ItemListPrice__c` for any other Sale Type.

> Nested IFs are supported, so multi-tier conditional logic like discount tiers or financial product fee bands can be expressed without custom code.

### Configuration and Runtime Video

📹 **"If Else Formula, Auto-numbering demo"** — recorded demo confirmed in the Solution Overview licensing matrix. [NEEDS REVIEW — get URL.]

---

## Feature 5: Accelerate Debugging of Pricing Flows (Auto-Numbered Element Names)

> **Source:** Solution Overview deck "Easier debugging for multiple occurrences of same elements".

### Business Objective

Pricing procedures often contain multiple occurrences of the *same element type* (e.g., several Formula-Based Pricing elements) that previously shared the same name — making them hard to distinguish in the Revenue Cloud Operations Console during debugging. Spring '26 auto-generates a unique occurrence-count suffix on each element's name, and that name flows through to the Operations Console for easy identification.

### Use Cases

**Pricing Admin persona:**

- **Identify the right Formula-Based Pricing element when debugging** — when a procedure has 3 Formula-Based Pricing elements and one is failing, the auto-generated unique name lets you pinpoint which one in the Operations Console without manual inspection.

### Design Time Configuration

> **No configuration required.** This is automatic behavior in Spring '26.

When a new element is added to a pricing procedure, Salesforce automatically appends an occurrence-count suffix to the element's name. This name is shown in:

- The pricing procedure designer
- The **Revenue Cloud Operations Console** (renamed from Pricing Operations Console — see Feature 6)
- Pricing API execution logs

### Configuration and Runtime Video

📹 **"If Else Formula, Auto-numbering demo"** — single combined demo for both features. [NEEDS REVIEW — get URL.]

---

## Feature 6: Pricing Operations Console Is Now Revenue Cloud Operations Console

> **Rename only — no functional change.** Source: release notes + master PDF lines 75271+ (entire Operations Console section now uses the new name).

### What changed

Every reference in product UI, Help docs, and App Launcher entries:

- Old: **Pricing Operations Console**
- New: **Revenue Cloud Operations Console**

### Action required

For prior-release exercises that referenced "Pricing Operations Console", the carry-forward note (top of doc) should remind readers the app is now called Revenue Cloud Operations Console. No procedure logic changes; the same four sections remain (Price Waterfall Storage, Decision Tables, API Calls, Pricing API Executions).

---

## Promotions (Beta) — Define and Apply

> **Source:** Solution Overview deck "Promotions (Beta) — Define and apply promotion discounts" + "Promotion visibility at runtime (Beta)" + master PDF "Set Up Promotions in Revenue Cloud (Beta)" (line 69061+).

### Business Objective

Businesses want to offer promotional discounts as special prices applicable for a limited time, to incentivize sales of newly launched products. They need flexibility to either carry over special pricing across the asset lifecycle or revert to regular pricing during amendments and renewals.

### Use Case

Configure limited-time offers that give special discounts to attract customers and enable upsells.

### Solution / How To Configure

1. **Define product- and category-based promotions** using the definition template.
2. Sellers see eligible and applicable promotions during product browse and in the Quote line item product details panel.
3. Pricing applies relevant promotions at run time on the transaction line via the **Promotion Execution Element** in the pricing procedure.
4. Carry-forward behavior:
   - **Last Transaction Price** as the pricing source — promotions carry over across asset lifecycle.
   - **List Price** as the pricing source — promotions reset; current eligible promotions evaluate fresh during Amendments / Renewals.

### Promotion Visibility at Runtime (Beta)

Companion feature with these runtime characteristics:

1. Active product and category promotions are **visible during product browse**.
2. Quote/Order pricing applies **automatic** promotions; **manual / coupon code** promotions must be selected by the seller. Once applied, they appear on the side panel of product details.
3. Assets carry applied-promotion information via the **AssetActionSource → PriceAdjustment** object.
4. **Amending an asset against Last Transaction Price** carries forward previously applied promotions and does not apply currently eligible ones.
5. **Amending an asset against List Price** evaluates current eligible promotions and applies them.

### Notes for the exercise

- Beta in 260 — clearly label as such.
- `rlm-base-dev` commit `f2b8aa59 enhanced pricing procedure with promotions` suggests demo content may already exist in the repo. [NEEDS REVIEW — confirm with author.]
- Detailed activation/configuration steps are in master PDF p 1336+ — pull when authoring full content.

📹 **"Promotions Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Cross-Area: 15K Line Scale (Beta)

**Primary home:** `260-transaction-management-hands-on.md` § 15K Transactions (Beta).

Spring '26 introduces a Beta capability supporting 15,000-line quotes and orders, with Pricing and Configurator both validated against the new scale. This is the formalization of what 258 framed as "Enhanced Pricing Performance for Large Transactions". For Pricing specifically: pricing procedures continue to execute consistently at 15K-line scale; the same procedures, recipes, and propagation rules apply.

**For Pricing readers:** if your pricing procedures use multi-element compositions (Header Adjustment + Price Propagation + IF formula + Promotions), validate them against representative 15K-line transactions. Pricing performance should hold; if it doesn't, file a case referencing the 15K Beta scope.

→ **Full configuration:** `docs/enablement/260/260-transaction-management-hands-on.md` § 15K Transactions (Beta).

---

## QuantumBit data reference (for use in step-by-step instructions)

When authoring Design Time Configuration steps, reference QuantumBit records by name. These canonical entries come from the QB pricing data plan.

### Price Books

> Source: `datasets/sfdmu/qb/en-US/qb-pricing/Pricebook2.csv` — 1 custom price book, plus Standard.

[Author: open the CSV and list the specific name + currency code here when drafting full content.]

### Price Adjustment Schedules

> Source: `datasets/sfdmu/qb/en-US/qb-pricing/PriceAdjustmentSchedule.csv` — 3 schedules.

[Author: list names here.]

### Product Selling Models

> Source: 9 selling models loaded read-only from `qb-pcm`.

[Author: list names — common ones: One-Time, Term-Defined, Evergreen.]

### Sample Products

> 162 products in QB catalog. For exercises, pick representative products that are bundles (for bundle adjustments), single SKUs (for tier examples), and term-defined products (for selling-model examples).

[Author: select 3–5 canonical products and document SKUs here. These become the "use product X" reference for any feature walkthrough.]

---

## Open questions for author / PM

> Updated after reading the Solution Overview deck — several prior questions resolved or reframed.

1. **Demo URLs** — the Solution Overview confirms three recorded demos exist for 260 Pricing: *Price Propagation Demo*, *Promotions Demo*, *If Else Formula, Auto-numbering demo*. **Need the actual URLs** (Highspot / internal Vidyard / Slack-hosted?) to embed or link from the exercise.
2. **Demo data for Price Propagation** — still open. QB doesn't natively model nested Building/Floor/Room hierarchies. Options: layer a temporary overlay catalog, pick a different scenario that fits QB, or document the limitation. The Solution Overview's "Pricing Propagation Preview" feature focuses on design-time configuration of the propagation table — that part *can* be demonstrated against any QB pricing procedure even without nested groups.
3. **Procedure Plan packaging** (Feature 2 in earlier draft) — the Solution Overview Price Management section does **not** include this feature. Either it was reclassified into a different section (Packaging Updates, p 3052 in the deck) or the release notes summary covered something separate. Worth a focused look at the deck's Packaging section before promoting this feature.
4. **Promotions activation prerequisites** — the Beta requires explicit enablement. The Solution Overview describes the user flows but not the activation steps. Will need to either pull from the master PDF or get from PM.
5. **End-to-end scenario** — should 260 add a stitched-together scenario showing Promotions + Price Propagation + IF formula working together against a single QB quote? Solution Overview suggests these are designed to compose well; this would be a strong pedagogical add for 260.
6. **Branding** — keep "Revenue Cloud" labels, switch to "Agentforce Revenue Management", or use both? The Solution Overview deck still uses "Revenue Cloud Advanced" throughout (the rebrand hasn't propagated to internal materials yet). Recommendation: stay with "Revenue Cloud" for 260 enablement until the product UI updates.
7. **`rlm-base-dev` Promotions content** — confirm whether commit `f2b8aa59 enhanced pricing procedure with promotions` already provisions a promotions demo in QB. If yes, the exercise can leverage it directly; if not, we'll need to either author one or wait for it.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
