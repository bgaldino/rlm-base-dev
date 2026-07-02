---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Transaction Management"
document_version: 0.3
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag) — includes both one-time/term-defined and usage-rated products"
  - "Pricing procedures activated (`prepare_pricing_data` flow completed)"
  - "Rating set up if exercises include usage-rated products (`prepare_rating` flow completed when `rating=true`)"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Transaction Management (pp 647–887) + § Advanced Approvals (pp 887–927)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — Transaction Management section"
  - "docs/salesforce/260/feature-index.md — per-area feature inventory"
  - "datasets/sfdmu/qb/en-US/qb-pcm/ — QuantumBit catalog"
  - "datasets/sfdmu/qb/en-US/qb-rating/ — QuantumBit usage rating data plan"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
  - ".cursor/skills/revenue-cloud-data-model/domains/usage.md — for usage-product context"
---

# Revenue Cloud — Transaction Management

**Enablement Exercises** · Version 0.3 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog loaded.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 release notes, Solution Overview deck, and master Help PDF.** This is the largest area in 260 (12+ features across 5 sub-categories). Configuration steps reflect the Solution Overview for new features and master PDF for Advanced Approvals subsection. UI-driven items flagged `[NEEDS REVIEW]` pending walkthrough in a 260 org with screenshots.

> **Critical context for readers — usage products on QB quotes:** QuantumBit's catalog includes **9 usage-rated products** (in addition to 150+ one-time and term-defined products). When a quote line item references a usage-rated product like `QB-DB` (database with CPU + storage rating), `QB-DAT-THPT` (data throughput), or `QB-TOKENS-PACK` (consumption tokens), the line behaves differently downstream — pricing applies rate cards, billing applies usage-based schedules, and asset creation produces usage assets that track ongoing consumption. Several Transaction Management features in this exercise (Ramp Deals, Multiple Ramped Asset Amendments, 15K Beta) explicitly support usage products as part of complex deal structures.
>
> If your reader hasn't seen Usage Management before, point them to `docs/enablement/260/260-usage-management-hands-on.md` for the design-time setup of usage products before running the TM walkthroughs that involve them.

---

## Carry-forward inventory (from prior releases)

The following features were introduced in 256 (Su'25) or 258 (W'26). They remain valid for 260 unless flagged otherwise.

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Contract Pricing Schedule | 256 | `docs/enablement/256/Summer '25 - Transaction Management.pdf` | ✅ no change |
| Cumulative Quantity Contract Pricing | 256 | same | ✅ no change |
| In-Flight Order Changes | 256 | same | ✅ no change |
| Automatically Renew Termed Subscriptions | 256 | same | ✅ no change |
| Automatically Create and Update Renewal Opportunities | 256 | same | ✅ no change |
| Negotiate Renewal Price Uplifts Upfront | 256 | same | ✅ no change |
| Header Adjustments for Transaction-Level Discount | 258 | `docs/enablement/258/Transaction Management - Winter '26 Revenue Cloud - External.pdf` | ✅ no change — also documented under Pricing 258 (Discount Distribution Service) |
| Ramp Deal for Groups | 258 | same | 🔄 **enhanced** in 260 — see Feature 3 (Multiple Ramp Schedules per Transaction) |
| Deep Clone Quotes and Orders | 258 | same | ✅ no change |
| Transfer Assets to Another Account | 258 | same | ✅ no change |
| Quote Line Import from CSV | 258 | same | 🔄 **enhanced** in 260 — see Feature 11 (Enhanced Import CSV with Auto-Loading of Defaults) |
| Enhanced Pricing Performance for Large Transactions | 258 | same | 🔄 **enhanced** in 260 — formalized as Feature 1 (15K Transactions Beta) |

---

## Upgrade Guidance from Winter '26

> Customers upgrading from 258 (Winter '26) to 260 (Spring '26) — review these transitional actions before assuming the carry-forward features in this area work as expected. Source: master PDF "Upgrade Guidance for Spring '26" → Transaction Management (p 118–119).

### Error When Refreshing Quote Pages on Partner Community Sites

After upgrading to Spring '26, refreshing quote pages on existing partner quoting sites results in errors that prevent the pages from loading. Admins who want to view or modify the Quote Detail page in Experience Builder can't load the page.

**Affected:** customers with partner quoting sites built before Spring '26.

**Workaround:** Sales reps shouldn't refresh quote pages on partner quoting sites. Admins must recreate the Quote Detail page in Experience Builder to apply changes.

### Cloning Quote Line Groups with Bundles and Active Constraints

After upgrading, cloning a quote line group fails when the group contains a bundle with a child product that has an active constraint.

**Workaround:** Disable the constraint engine rule for the initial clone request and perform the clone operation. After the cloned lines are added to the target quote/order, re-enable the constraint engine rule and run configuration using the Place Sales Transaction API.

---

## Known Issues for Spring '26

### Instant Pricing API returns additional records for ARC use cases

When invoked headlessly with **API v66.0**, the Instant Pricing API response can include cancellation lines, ARC breakdown lines, ARC detail lines, and quote summary fields not returned in earlier API versions. Integrations that depend on prior response shape should not upgrade their API version. (master PDF p 118)

### Canceling Derived Pricing Products Results in Incorrect Net Total Price

After upgrading, canceling or amending a derived pricing product can produce an incorrect net total. **No workaround currently available.** (master PDF p 118)

### Net Unit Price Disappears During Amendment of Usage Assets Created with Group Ramp

When editing the quantity or another field during amendment of usage assets created with group ramp, the **net unit rates** for usage quote line items / order line items can **disappear**. Affects exercises that combine usage products + Multiple Ramp Schedules (Feature 3) + amendment workflows. (master PDF p 127)

---

## Release Overview

Spring '26 Transaction Management includes the following net-new features:

1. **15K Transactions** *(Beta)* — built-in support for 15,000-line quotes and orders (cross-listed via Pricing exercise)
2. **Advanced and Pre-Set Filters** — predefined + user-defined filters for navigating large quotes
3. **Ramp Deal Enhancements**
    - **Multiple Ramp Schedules Per Transaction** — independent ramp schedules per office location, distinct product suites with overlapping ramps on a single quote
    - **Multiple Ramped Asset Amendments in Single Transaction** — amend multiple ramped + non-ramped assets together with varied timelines
4. **Advanced Approvals**
    - **Approval Notification with Email Templates** — new email templates for approver assignment and submitter notification
    - **Rule-Based Auto-Approvals (Smart Approvals)** — auto-approve pre-qualified data changes, skip re-review of unchanged data
5. **Advanced Amendments**
    - **Swaps, Upgrades & Downgrades end-to-end** — complete swap/upgrade/downgrade lifecycle
    - **Amend Asset for Future-Dated Transactions** — amend an asset before its future-dated transaction takes effect
6. **UX Enhancements**
    - **Enhanced Price Waterfall UX Hover** — better hover-state UX in Price Waterfall component
    - **Always On Instant Pricing** — Instant Pricing toggle defaults on across sessions
7. **Other Enhancements**
    - **Enhanced Import CSV to Quote with Auto-Loading of Defaults** — bundle imports auto-include default child products and default attributes
    - **Elevated Data Access for Pricing Quotes and Orders** — sales reps can act on pricing without full data access
    - **Automated Predictable Line Sequencing** *(Pilot)* — line sequencing maintained from quote → order
    - **Quoting Agent Enhancements** — Agentforce-powered quoting improvements

---

## Feature 1: 15K Transactions (Beta)

> **Source:** Solution Overview "15K Transactions - Beta" page. Cross-area landing point — referenced from the Pricing exercise.

### Business Objective

Enterprise customers building complex quotes — manufacturers (multi-component bundles), insurance providers (multi-policy/multi-asset), industrial distributors (high-volume SKU replenishment) — need scalable transactions that hold performance at 15,000+ lines. Spring '26 introduces **built-in support for 15K quote and order transactions** that delivers the same UX and performance customers expect at 1K transactions, ready to use from day one.

### Use Cases

- **Manufacturer**: complex multi-component quote with thousands of configurable parts (e.g., 12,000 mechanical components across multiple assemblies on a single industrial equipment quote).
- **Insurance**: large multi-policy/multi-asset quote with extensive rating details (e.g., fleet insurance covering 8,000 vehicles, each with usage-rated mileage components).
- **Industrial distributor**: high-volume multi-SKU replenishment order (e.g., 14,000 SKU restocking purchase order for a regional distributor's quarterly inventory refresh).

### Design Time Configuration

> **Closed Beta** — customers must contact Salesforce to enable.

The 15K capability is enabled at the org level via Black Tab/internal admin perm (Beta gating). Customers requesting Beta access:

1. Open a Salesforce Support case requesting **15K Transactions Beta** access.
2. Salesforce Support enables the org perm.
3. After enablement, no additional admin configuration is required — the Pricing engine, Configurator, and STLE all transparently support 15K-line transactions.

### QuantumBit walkthrough scenario

Building a 15K-line QB transaction from scratch takes substantial time; for demo purposes, scope to a smaller representative subset that exercises the same code paths:

1. Create a quote with QB Complete bundle as the foundation.
2. Add 100+ line items via Quote Line Import from CSV (see Feature 11 — bundles will auto-load defaults).
3. Mix in usage-rated products (`QB-DB` for database, `QB-DAT-THPT` for throughput, `QB-TOKENS-PACK` for token consumption) to exercise rating at scale.
4. Run Instant Pricing — verify pricing engine handles the load.
5. (For full 15K verification) extend via repeated CSV imports until line count approaches 15K — confirm pricing/configuration latency stays within SLA.

### Configuration and Runtime Video

[NEEDS REVIEW] — Beta features may not have public demos. Confirm with PM.

---

## Feature 2: Advanced and Pre-Set Filters

> **Source:** Solution Overview "Advanced and Pre-Set Filters" page.

### Business Objective

Sales reps managing large, high-line-count quotes (especially in tech/SaaS, manufacturing, telecom) need to find specific lines without manually scrolling through thousands of entries. Spring '26 adds **predefined out-of-the-box filters** plus **user-defined filters** with **AND/OR logic** to refine results and isolate the exact subset of quote lines.

### Use Cases

- **Technology / SaaS**: filter quote lines by product family, type, or billing frequency to quickly update pricing/terms on large multi-product deals.
- **Manufacturing**: narrow lines by product or start date to manage complex quotes and phased shipments.
- **Telecommunications**: filter by service type, region, or term to manage large quotes with thousands of bundled services.

### Design Time Configuration

[NEEDS REVIEW] — likely a property on the Sales Transaction Line Editor (STLE) component. Confirm in 260 org.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 3: Multiple Ramp Schedules Per Transaction

> **Source:** Solution Overview "Multiple Ramp Schedules Per Transaction" page.

### Business Objective

Customers with multi-year, multi-location, multi-tenant, or multi-solution deals need to consolidate complex deal structures into a **single quote** rather than splitting into multiple quotes. Spring '26 introduces support for **independent ramp schedules with overlapping segments** on the same transaction.

### Use Cases

- **Independent ramp schedule per office location** — different growth profiles per branch
- **Distinct product suites or solutions** — each with unique, overlapping, or concurrent ramp-up plans on a single quote

### Design Time Configuration

> **Org Pref required:** "Multiple Ramp Schedules Per Transaction" in Revenue Settings.

1. From Setup → Revenue Settings, enable **Multiple Ramp Schedules Per Transaction**.
2. On the quote, create a Quote Line Group with `Quote Line Group Type = RampScheduleGroup`.
3. Add a SubGroup to the RampScheduleGroup with `IsRamped = True` and `SegmentType = Custom` or `Yearly`.
4. Configure multiple SubGroups for distinct ramp schedules (one per location or product line).
5. Add line items to each SubGroup; configure ramp segments per SubGroup independently.

### QuantumBit walkthrough scenario

Build a multi-location deal:

1. Create a quote for a customer wanting QB infrastructure across 3 office locations.
2. For each location, add a RampScheduleGroup → SubGroup with location-specific timeline.
3. Add the QB Complete bundle (or QB Server + Memory + Storage individually) into each SubGroup.
4. Add a usage-rated product like `QB-DB` to the second location's SubGroup; configure its ramp-up to start mid-deal.
5. Verify each location has independent ramp behavior and pricing reflects per-location ramp segments.

> ⚠️ **Caveat for usage products in ramp groups:** Once these assets are created and need to be amended later, see Known Issues — *Net Unit Price Disappears During Amendment of Usage Assets Created with Group Ramp* affects this combination. Calling out the limitation is appropriate; users would otherwise hit it during downstream walkthroughs.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 4: Multiple Ramped Asset Amendments in Single Transaction

> **Source:** Solution Overview "Multiple Ramped Asset Amendments in Single Transaction" page.

### Business Objective

Customers managing multi-asset portfolios need to amend multiple ramped assets together — with varied timelines — instead of one-amendment-per-asset. Spring '26 enables **selecting multiple ramped + non-ramped assets together for amendment**, in a single transaction.

### Design Time Configuration

> **Org Pref required:** "Multiple Ramp Schedules Per Transaction" (same Org Pref as Feature 3).

1. With the org pref enabled (see Feature 3), navigate to Assets.
2. Select multiple Ramped Assets (alongside any Non-Ramped Assets to be amended together).
3. Click **Amend**.
4. The amendment quote is created with all selected assets, preserving each asset's ramp schedule and timeline.

### QuantumBit walkthrough scenario

After completing the multi-location deal in Feature 3 and assetizing it:

1. Navigate to the customer's Account → Assets.
2. Select the QB Complete asset for Office 1, the QB Complete asset for Office 2 (different ramp end dates), and a non-ramped Professional Services asset.
3. Click **Amend**.
4. Verify the amendment quote contains all three assets with their independent ramp segments preserved.

> ⚠️ If any of the ramped assets include usage-rated products, expect the *Net Unit Price Disappears During Amendment of Usage Assets Created with Group Ramp* known issue (see Known Issues for Spring '26 above). Users may need to re-enter quantities. Plan walkthroughs accordingly — either keep ramps non-usage for the demo, or pre-warn users.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 5: Approval Notification with Email Templates

> **Source:** Solution Overview Approvals subsection. Master PDF Advanced Approvals (lines 46694+).

### Business Objective

Approval workflows previously fired without configurable email content — approvers and submitters got system-default messages. Spring '26 adds **dedicated email templates** so admins can craft branded, contextual messages for approval-related notifications.

### Use Cases

- **Brand approver emails** — when a deal needs Discount Approver review, the email template includes deal context, line item summary, and a customer-facing brand voice.
- **Customize submitter status notifications** — when an approval is approved/rejected/recalled, the submitter sees a status email with appropriate context.

### Design Time Configuration

Configurable via org settings:

- **Send Approval Work Item Assignment Emails** — emails sent to approvers when work items are assigned
- **Send Approval Submission Status Email Notifications** — emails sent to submitters when approval status changes

[NEEDS REVIEW] — full email template configuration steps. Templates likely live in the Email Templates section of Setup; specific template tokens for approval context (record, approver, submitter, etc.) need confirmation.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 6: Rule-Based Auto-Approvals (Smart Approvals)

> **Source:** Solution Overview Approvals subsection. Master PDF "Smart Approvals in Approval Flows" + "Define Rules and Conditions for Auto-Approval Resubmissions" (lines 47030–47493).

### Business Objective

Approval bottlenecks were causing slow deal cycles, especially for resubmissions where most fields hadn't changed. **Smart Approvals** routes requests by **auto-approving pre-qualified data changes** and **skipping re-review of unchanged data**. When a record is resubmitted, Smart Approvals compares new conditions against the previous submission — if values stay within the defined range, it skips re-approval.

### Use Cases

- **Resubmissions with minor edits** — sales rep updates a line item quantity by ±5%; Smart Approval auto-approves because the discount level didn't change.
- **Pre-qualified deal types** — deals matching specific patterns (e.g., new business < $50K with standard discount) auto-approve while edge cases route to manual review.

### Design Time Configuration

Smart Approvals work via Autolaunched Flow Approval Process or Record-Triggered Flow:

1. From Flow Builder, **Create a Draft Autolaunched Flow Approval Process**.
2. Define **Rules and Conditions for Auto-Approval Resubmissions**:
    - Specify which fields trigger re-review when changed
    - Specify which fields are within "auto-approval threshold" (e.g., quantity within ±10%)
3. (Optional) Configure **Stage Exit Condition** for serial approval workflows to prevent deadlocks when conditional steps don't trigger.
4. (Optional) Use **Override Approval Work Item** flow action to let approval admins override decisions for any assignee.
5. Save and activate the flow.

### QuantumBit walkthrough scenario

1. Create an approval flow on Quote object that requires manual approval if Discount > 10%.
2. Configure Smart Approvals rule: "Resubmissions auto-approve if Discount has not changed AND Quantity changed within ±10%."
3. Submit a quote with 9% discount → manual approval (under threshold).
4. Submit a quote with 12% discount → manual approval kicks in.
5. Approver requests changes; sales rep adjusts quantity by 8% (no discount change); resubmits.
6. Smart Approval auto-approves the resubmission (within threshold).

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 7: Swaps, Upgrades & Downgrades

> **Source:** master PDF "Swap, Upgrade, or Downgrade Assets in Revenue Cloud" (pp 880–882) + "Considerations for Swap, Upgrade, and Downgrade Amendments" (p 882). Verified content.

### Business Objective

Asset lifecycle management previously required workarounds for swaps (replacing one asset with another) and complex upgrades/downgrades — these often had to be modeled as a "rip and replace" (cancellation followed by new sale) or a simple reduction. Spring '26 introduces **complete end-to-end swaps, upgrades, and downgrades** as specialized amendment types that accurately capture the relationships between swapped-out and swapped-in assets in the quote line item, order item, asset action, and asset action source objects.

Business analysts and sales operations can now generate reports that differentiate products acquired via new sales versus those acquired through amendments, with clear asset-action subtypes:
- **SwapIn / SwapOut**
- **UpgradeFrom / UpgradeTo**
- **DowngradeFrom / DowngradeTo**

> ⚠️ **Critical compatibility constraints — read before authoring walkthroughs:**
> - **You can't swap, upgrade, or downgrade**: ramp assets, group ramp assets, expired assets, **usage-based assets**, or derived-price products.
> - **Not compatible with Dynamic Revenue Orchestration.**
> - **You can't roll back** swap transactions.
>
> These constraints rule out many obvious QB walkthroughs — the QB Database (`QB-DB`) and QB Database with Token rating (`QB-DB-TOKEN`) are *both* usage-based, so a QB-DB → QB-DB-TOKEN swap **isn't supported**. Pick swap walkthroughs that use **non-usage products** (e.g., hardware bundles, term-defined subscriptions).

### Use Cases

- **Swap (non-usage assets only)**: customer wants to replace **QB Starter** bundle with **QB Complete** bundle as their needs grow — swap is a single transaction that retires QB Starter and creates QB Complete.
- **Upgrade**: customer wants to upgrade from **QB Server (basic)** to **QB Server (high-availability)** — the upgrade preserves contractual terms while adjusting the underlying product.
- **Downgrade**: customer wants to scale back hardware spec — downgrade respects pro-ration policies.

### Design Time Configuration

> **Permission required:** `Initiate Amend` user permission.

**Optional pre-step:** Add **Type** and **Subtype** columns to the Sales Transaction Line Table component on the Quote/Order page so users can see SwapIn/SwapOut/UpgradeFrom/UpgradeTo/DowngradeFrom/DowngradeTo line groupings clearly.

**Swap procedure:**

1. From the App Launcher, go to **Accounts**, select the customer's account, then select the **Assets** tab to open the Managed Assets viewer.
2. Select the assets to swap out, then from the actions dropdown select **Swap**.
3. From the **Swap Selections** page, select a date for the swap.
4. Select the products to swap out, the quantity, and click **Next**.
5. Click **Add** for the products to swap in, click **Next**.
   - The resulting quote shows the swap-out line item with negative price + the swap-in line item with positive price.
6. Click **Create Order**, then **Create Single Order**.
7. Activate and mark the order complete.
8. Verify in the Managed Assets viewer:
   - **Swapped-out asset** → Related tab → Asset Actions → new entry with Business Category = `Swaps` and **negative quantity**.
   - **Swapped-in asset** → Related tab → Asset Action → new entry with Business Category = `Swaps` and **positive quantity**.

(Upgrades and downgrades follow the same pattern with respective action types.)

### QuantumBit walkthrough scenario (non-usage)

1. Set up a customer Account with an active **QB Starter** bundle assetized.
2. Open the Managed Assets viewer for the account.
3. Select the QB Starter asset → actions dropdown → **Swap**.
4. Select date for the swap; choose to swap out QB Starter for **QB Complete**.
5. Walk through the resulting swap quote → create order → complete.
6. Verify swap asset actions appear with SwapIn (QB Complete) and SwapOut (QB Starter) subtypes.

### Billing-side behavior

> **From the 260 Billing Solution Overview** (RCA + RCB):
>
> When a swap, upgrade, or downgrade activates, the billing engine automatically:
> - Creates a **negative Billing Schedule Group (BSG)** to adjust the old asset
> - Creates a **new BSG** for the swapped/upgraded/downgraded product
>
> No additional billing setup is required beyond core RCA + RCB enablement. Customers using Invoice Management (in RCA) or Revenue Cloud Billing get this behavior transparently.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview doesn't explicitly list a Swaps demo. May be covered in a broader Advanced Amendments demo.

---

## Feature 8: Amend, Renew, and Cancel Assets with Future-Dated Changes

> **Source:** master PDF "Amend, Renew, and Cancel Assets with Future-Dated Changes" (pp 882–884) + "Examples of Amendment Types and Results" (pp 883–885) + "Considerations for Assets with Future-Dated Changes" (pp 885+). Verified content.

### Business Objective

Customers can change assets that have **scheduled future transactions** — upsell, downsell, renewal, transfer, swap, or attribute change. Previously, an asset with a booked future-dated change couldn't be modified before that future change took effect. Spring '26 supports amending, renewing, or canceling assets *before* their future asset state period (ASP) starts, with the system creating a single quote line item (QLI) or order item (OI) per asset transaction and resetting the ASP timeline through the end of the subscription period.

> ⚠️ **Critical compatibility constraints:**
> - The amended asset must have **more than one** subsequent future-dated change recorded as an ASP. If the transaction has only one ASP or it's occurring in the last ASP, a regular amend/renew/cancel is created instead.
> - **You can't amend, renew, or cancel before a future ASP on ramp deals.**
> - **You can't amend a usage-based product with a future-date change.**
> - **You can't use derived-pricing products (DPP) for future-dated ARC transactions** — the amended date that results in a future-dated change can't add DPP assets to a future-dated transaction or select a DPP asset.

### Use Cases

**Sales Rep persona:**

- **Adjust quantities before a scheduled growth ramp** — customer has an asset with two ASPs (1/1/26–6/30/26 quantity 10, 7/1/26–12/31/26 quantity 15). Sales rep needs to amend the start date 2/1/26 with quantity reduction of 7 — the system handles the LIFO reduction across the impacted ASPs automatically.
- **Modify attributes before a future-dated swap** — customer has a future-dated upgrade scheduled but needs an interim attribute change before that upgrade takes effect.
- **Cancel before a future-dated change** — cancellation is a special type of reduction that puts the asset in terminal state; assetization of the cancellation order impacts all future-dated ASPs.

### Amendment Types and Their Results

The master PDF documents detailed examples for each amendment type. Authors should reference these when constructing walkthroughs:

- **Positive Amendments (Upsell or Add Quantity)**: delta quantity applies to all ASPs that exist beyond the new amendment start date. No detail lines for termed assets on positive increases.
- **Negative Amendments (Reduction or Downgrade)**: LIFO reduction across affected ASPs. Each future-dated ASP gets a detail line. Over-reduction validation error fires if an ASP doesn't have enough quantity.
- **Early Renewal**: a renewal dated before the scheduled renewal date overrides all future ASPs and amendments/renewals. With "As-Is Renewals" enabled, asset renews at the latest ASP quantity but with potentially different prices/quantities.
- **Cancellation**: terminal state for the asset, no further ARC operations allowed. Impacts all future-dated ASPs.
- **Attribute / Field Amendments That Require Repricing**: cancel + reprice operation. Multiple cancel + reprice detail lines per impacted ASP; attribute on the amendment line overrides all future ASP attribute values.
- **Transfers**: copies ASP from source account to destination; negative amendment on source (reduces from all future-dated ASPs); add amendment on destination. Transfer minimum quantity to all current and future ASPs.
- **Swaps**: acts as add amendment + negative amendment. Swapped products inherit ASP and relevant actions. Negative amend quantity reduces from all future-dated ASPs starting on the swap start date.

### Design Time Configuration

> **Permission required:** `Initiate Amend` user permission OR `initiateAmendment` API access (for amendments + transfers + swaps with future-dated ASPs). For renewals/cancellations, also `Initiate Renew` and `Initiate Cancel` user permissions OR `initiateRenew` API and `initiateCancel` API access.

**Procedure:**

1. For the customer's account, go to the **Assets tab** and open the **Managed Assets viewer**.
2. Select the assets and click **Amend**, **Renew**, or **Cancel**.
3. Enter the **date** for the change to take effect. (This date can be before the start date of an existing future ASP — that's the new 260 capability.)
4. Click **Create Order**, then **Create Single Order**.
5. Select the new order, activate it, and set the status to **complete**.

The create-order process resets the ASP timeline to reflect the new transaction through the end of the subscription period.

### QuantumBit walkthrough scenario

1. Set up a customer Account with a **QB Server** asset (non-usage, non-ramp, non-DPP).
2. Schedule a future-dated quantity increase: amend the asset with start date 6/1/26, quantity +5.
3. Now (May 2026) — using the new 260 capability — initiate a *new* amendment with a start date of 5/15/26 (before the 6/1/26 ASP) — for example, reduce quantity by 3.
4. Verify the resulting quote creates a single quote line item per asset transaction and the ASP timeline resets to reflect both transactions correctly.
5. (For demonstrating attribute repricing) — modify a custom attribute on the asset alongside the quantity change; verify multiple cancel + reprice detail lines are generated per impacted ASP.

### Billing-side behavior

> **From the 260 Billing Solution Overview** (RCA + RCB):
>
> Several future-dated amendment patterns trigger automatic billing schedule adjustments. No billing setup is required:
>
> - **ARC before FDO (Amend & Renew with Future-Dated Order)** — billing evaluates existing schedules and creates **adjustment Billing Schedules** that reflect the changes accurately.
> - **Change End Date** — billing autonomously evaluates existing schedules and creates adjustment Billing Schedules.
> - **Undo Future Dated ARC (Rollback)** — on order activation, billing creates **negative billing schedules** to counterbalance the previously created schedules. Use the Rollback action in Managed Assets Viewer.
> - **Price Amendments (no quantity change)** — billing creates negative BS for old pricing + new BS for updated price. Previously, a price change required a quantity change to trigger an amendment; 260 lifts that limitation.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview doesn't explicitly list a Future-Dated Amendment demo.

---

## Feature 9: Enhanced Price Waterfall UX Hover

> **Source:** Solution Overview "Enhanced Price Waterfall UX hover" page.

### Business Objective

The Price Waterfall component shows the discount path applied to a line item. Spring '26 enhances the **hover state** so users see more information without clicking through — making the waterfall more glanceable for sales reps and approvers reviewing pricing.

### Use Cases

- Sales rep verifying the order of pricing element execution on a complex line item by hovering across waterfall steps.
- Approver reviewing the discount cascade before approving — quickly scanning hover-state details to spot anomalies.

### Design Time Configuration

> **No configuration required.** Hover enhancement is automatic.

The Price Waterfall component, when added to a record page or used inline in STLE, displays enhanced hover-state information by default in 260.

### Configuration and Runtime Video

📹 **"Price Waterfall Enhancements Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 10: Always On Instant Pricing

> **Source:** Solution Overview "Always On Instant Pricing" page.

### Business Objective

Sales reps previously had to **manually enable Instant Pricing** every time their quote or order page loaded — adding a click and creating opportunities for missed pricing updates. Spring '26 introduces an org-level default that keeps Instant Pricing on across all sessions.

### Design Time Configuration

> **Permission required:** Admin (Revenue Settings).

1. From Setup → Revenue Settings, find and enable **Instant Pricing Active by Default**.
2. Sales reps see Instant Pricing toggled on automatically on every Quote/Order page load.

### Configuration and Runtime Video

📹 **"Always On Instant Pricing Demo"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 11: Enhanced Import CSV to Quote with Auto-Loading of Defaults

> **Source:** Solution Overview "Enhanced Import CSV to quote with Auto-Loading of Defaults" page.

### Business Objective

When sales reps imported CSV files containing bundle products or products with default attributes, they hit validation errors about defaults not being selected — requiring manual edits per line. Spring '26 introduces **auto-loading**: bundle imports auto-include default child products, and products with default attributes import with attributes pre-selected.

### Design Time Configuration

> **Permission required:** Advanced CSV Data Import permission set (`CSVImportLicenseAddOn`).

1. From Setup → Revenue Settings, enable **Import Quote Line Items**.
2. From Setup → Data Processing Engine, **Save As "Create Quote Line Items from CSV File"** and **activate** it.
3. From Setup → Revenue Settings → Data Processing Engine Definition for Import Quote Line Items → select your cloned definition.
4. Assign the `CSVImportLicenseAddOn` permission set to users who'll import.

### QuantumBit walkthrough scenario

1. Prepare a CSV with QB Complete bundle and QB Server (both have default child components and default attributes).
2. From a Quote, use Import Quote Line Items to load the CSV.
3. Verify each bundle imports with default child products selected, and products with default attributes have attributes pre-set — no validation errors, no manual adjustments needed.

### Configuration and Runtime Video

📹 **"Import Quote Line Enhancements"** — recorded demo confirmed in Solution Overview. [NEEDS REVIEW — get URL.]

---

## Feature 12: Elevated Data Access for Pricing Quotes and Orders

> **Source:** Solution Overview "Elevated Data Access for Pricing Quotes and Orders" page.

### Business Objective

Customers sometimes need sales reps to take pricing actions (calculate price, apply discounts) without granting them direct access to all the underlying data inputs (e.g., cost data, internal margins). Spring '26 introduces **elevated data access** — sales reps can act on pricing while restricted data stays protected.

### Design Time Configuration

> **Permission required:** Admin.

From Setup → Revenue Settings, enable **Elevated Data Access for Pricing Quotes and Orders**.

After enabling, sales reps can view computed prices and apply discounts even when underlying input fields they don't have field-level security to read are referenced by the pricing procedure.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview lists no demo.

---

## Feature 13: Automated Predictable Line Sequencing (Pilot)

> **Source:** Solution Overview "Automated Predictable Line Sequencing (Pilot)" page. Pilot — requires both BT org perm and customer org pref.

### Business Objective

Customers wanted line item sequencing on Quotes to consistently propagate to derived Orders, quote documents, and STLE — without ad-hoc reordering. Spring '26 introduces a **pilot** that enforces consistent line sequencing automatically.

### Design Time Configuration

**Two-step gate** — both must be enabled for the pilot:

1. **Salesforce-side (BT org perm):** Salesforce internally enables the org perm `Revenue Cloud: Automated Predictable Line Sequencing`.
2. **Customer-side (Revenue Settings):** From Setup → Revenue Settings, enable **Automatic Line Item Sequencing**.

### Use Cases

- **Order Manager**: when creating an Order from a Quote, line items reflect the exact sequential order from the Quote.
- **Quote Document generation**: line item order in generated documents matches the Quote view consistently.

### Configuration and Runtime Video

[NEEDS REVIEW] — Pilot features may not have public demos.

---

## Feature 14: Quoting Agent Enhancements

> **Source:** 260 highlights "Quoting Agent Enhancements" listed under Other Enhancements. Detailed content not extracted on initial scan.

### Business Objective

Agentforce-powered quoting capabilities are enhanced in Spring '26.

### Design Time Configuration

[NEEDS DEEPER SOURCE LOOKUP] — pull from master PDF Agentforce-related sections.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## QuantumBit data reference

QuantumBit catalog has both **non-usage** and **usage-rated** products. Transaction Management exercises should reference both as appropriate.

### Non-usage products (one-time / term-defined)

Use these for standard quote/order walkthroughs (Filters, Ramp Schedules without usage components, Always On Instant Pricing, CSV Import, etc.):

| Product Type | Examples |
|---|---|
| Hardware bundles | QB Complete, QB Server (with CPU + Memory + Storage components) |
| Hardware components | QuantumBit CPU, Memory modules, Network Adapters, Storage drives |
| Software subscriptions (term-defined) | QuantumBit Subscription products in the `PC-QB-SUB` classification |
| Professional Services | Professional Services Bundle, Engineering Resources (T&M) |
| Rack accessories | QuantumShell rack mounting, sliding shelves, rack PDUs |

### Usage-rated products (consumption-based)

Use these for walkthroughs involving usage rating, ramp schedules with usage components, asset amendments with usage assets, and 15K-scale tests (where usage rating exercises both Pricing and Rating engines):

| SKU | Product | Rating model |
|---|---|---|
| `QB-DB` | QuantumBit Database | CPU time + Data Storage (multi-resource) |
| `QB-DB-TOKEN` | QuantumBit Database (Token rating) | Quantum Tokens + sub-resources |
| `QB-DAT-THPT` | QuantumBit Data Throughput | Per GB/throughput |
| `QB-TOKENS-PACK` | Token Pack | Quantum Tokens (consumption tokens) |
| `QB-CMT-TKN-EACH` | Commitment Tokens (Each model) | Per-token commitment |
| `QB-CMT-TKN-FLAT` | Commitment Tokens (Flat model) | Flat-fee commitment |
| `QB-CMT-TKN-TIER` | Commitment Tokens (Tiered model) | Tiered commitment |
| `QB-MTY-CMT` | Monetary Commitment | Currency commitment |
| `QB-QTY-CMT` | Quantity Commitment | Quantity commitment |

Usage Resources powering these products:

| Code | Name |
|---|---|
| `QB-TOKEN` | Quantum Tokens (token resource) |
| `UR-CPUTIME` | Compute Time |
| `UR-DATASTORAGE` | Data Storage |
| `UR-DATAXFR` | Data Throughput |

> When walkthroughs involve usage products, ensure the org has been provisioned with `prepare_rating` flow (`rating=true`, `qb=true`) so all 9 usage-rated products and their rate cards are loaded. Without it, usage products won't price correctly at quote time.

---

## Cross-Area: Promotions in Pricing Procedures

**Primary home:** `260-salesforce-pricing-hands-on.md` § Promotions (Beta).

When pricing procedures include the **Promotion Execution Element** (a 260 Beta), pricing procedures evaluate eligible promotions at runtime. From the Transaction Management perspective:

- Sellers see eligible/applicable promotions in the **Quote line item product details panel** during quote authoring.
- **Automatic** promotions apply without seller action; **manual / coupon-code** promotions require seller selection.
- Applied promotions surface on the side panel of product details.
- Assets carry applied-promotion information via `AssetActionSource → PriceAdjustment`.
- Amendment behavior depends on the asset's pricing source: **Last Transaction Price** carries promotions forward; **List Price** re-evaluates current eligible promotions.

→ **Full configuration:** `docs/enablement/260/260-salesforce-pricing-hands-on.md` § Promotions (Beta).

---

## Cross-Area: Header Adjustments / Discount Distribution Service

**Primary home:** `258/Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf` (carry-forward — introduced 258, no change in 260).

Header Adjustments (also called Discount Distribution Service) lets sales reps apply a single discretionary discount at the **transaction header level** that propagates to all line items. From the Transaction Management perspective:

- Sales rep applies a percentage, fixed-amount, or total-price-override at the quote header via the **Manage Header Adjustment** action.
- The discount automatically distributes across eligible line items.
- The Price Waterfall shows distribution per line.
- Discounts carry from Quote → Order via standard place-sales-transaction flow.

→ **Full configuration:** `docs/enablement/258/Salesforce Pricing - Winter '26 Revenue Cloud - External.pdf` § Header Adjustments.

---

## Open questions for author / PM

1. **Demo URLs** — Solution Overview confirms recorded demos for: Price Waterfall Enhancements, Always On Instant Pricing, Import Quote Line Enhancements. Need the actual URLs.
2. **Smart Approvals + flow tooling** — does the existing approvals demo exercise QB-shaped data, or do we need to author a QB-specific approval flow before the walkthrough is meaningful?
3. **Swaps/Upgrades/Downgrades configuration** — full master PDF setup steps not yet extracted. Pull from the Asset/Amendment sections (master PDF pp 853–887).
4. **Future-Dated Transactions Amendment** — same. Pull steps from master PDF.
5. **Filters property location** — confirm whether filters live on the STLE component or the page layout, and whether they're admin-configurable per persona.
6. **Quoting Agent Enhancements** — content gap. Pull from master PDF Agentforce sections or get from PM.
7. **15K Beta data** — for the QB walkthrough scenario, is there a way to programmatically generate a 15K-line QB quote (Apex script or Robot test setup), or is it manual via repeated CSV import?
8. **Usage-product context placement** — is the prerequisite + critical-context callout sufficient, or should each feature involving usage have its own usage-callout block? Current draft uses a single top-level callout. Refine after first review.
9. **Branding for 262 forward-look** — 262 brings Slack Approvals + Approval Preview UX. Should 260 TM mention these as upcoming, or stay 260-focused? Currently silent on 262.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
