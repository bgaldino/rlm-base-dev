---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Invoice Management"
document_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag)"
  - "Invoice Management enabled (Revenue Cloud Advanced license)"
  - "Billing data plan loaded (`prepare_billing` flow with `billing=true`) — provisions billing policies, payment terms, tax policies"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Billing"
  - "docs/salesforce/260/solution-overview-spring-26-billing.pdf — internal Solution Overview deck (Billing, CONFIDENTIAL)"
  - "docs/salesforce/260/solution-overview-spring-26.pdf — Solution Overview deck (RCA, CONFIDENTIAL)"
  - "docs/salesforce/260/feature-index.md — per-area feature inventory (Invoice Management & Billing section)"
  - "datasets/sfdmu/qb/en-US/qb-billing/ — QuantumBit billing data plan"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
---

# Revenue Cloud — Invoice Management

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> **License scope of this exercise:** Invoice Management is the **Revenue Cloud Advanced (RCA)** subset of full billing capabilities. This exercise covers features available with the RCA license — One-Time + Subscription Charges, Tax (Standard + Header + VAT), Invoicing/Credits, Accounting Periods, and Analytics & Ops Console. Features that require the **Revenue Cloud Billing (RCB)** license — Billing Arrangement, Usage Invoicing, Milestone Charges, Debit Memos, Standalone Billing, full Doc Gen, GL/Journal Entries, Payments/Refunds/Collections, Billing Agents — are documented in the separate `260-revenue-cloud-billing-hands-on.md` exercise.

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog and billing data loaded.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 Solution Overview Billing deck and feature index.** This area benefits from heavy structural support: most 260 Billing features are documented in detail in the Solution Overview deck. Authoring effort is medium because much of the cross-area amendment behavior lives in TM Features 7 + 8.

> **Cross-area dependency:** The TM exercise now documents billing-side behavior for Swaps/Upgrades/Downgrades, Future-Dated Amendments, Change End Date, Undo Rollback, Price Amendments, and Multiple Ramp Schedules. Readers wanting full amendment + billing flow should read both this exercise and `260-transaction-management-hands-on.md` § Features 7–8.

---

## RCA vs RCB Capability Matrix

> Sourced from the 260 Billing Solution Overview comparison table.

| Capability | Invoice Management (RCA) | Revenue Cloud Billing (RCB) |
|---|---|---|
| One-Time & Subscription Charges | ✅ | ✅ |
| Billing Arrangement, Usage Invoicing, Milestone Charges | | ✅ |
| Usage Rating & Consumption calculation | | ✅ |
| Tax (Standard) | ✅ | ✅ |
| Invoicing, Credits | ✅ | ✅ |
| More Invoicing — Grouping, Write-off | | ✅ |
| Debit Memos | | ✅ |
| Standalone Billing for any object or external transaction | | ✅ |
| Invoice Doc Gen & Email Delivery (on demand + batch) | | ✅ |
| Accounting Periods & Closure | ✅ | ✅ |
| GL Accounts, Journal Entries (AR), FX Gain/Loss, Functional Currency | | ✅ |
| Payments, Refunds & Collections | | ✅ |
| Analytics & Ops Console | ✅ | ✅ |
| Billing Agents | | ✅ |

**This exercise covers the RCA column only.** For features in the RCB column, see `260-revenue-cloud-billing-hands-on.md`.

---

## Carry-forward inventory (from prior releases)

Substantial — Invoice Management has accumulated significant feature surface across 256 + 258. Readers should reference the prior-release PDFs for full walkthroughs of these stable features.

| Feature | Introduced in | Reference | 260 status |
|---|---|---|---|
| Billing App and Account 360 | 256 | `docs/enablement/256/Summer '25 - Invoice Management.pdf` | ✅ no change |
| Billing Operations Console | 256 | same | ✅ no change |
| Create Standalone Credit Memo | 256 | same | ✅ no change |
| Create Credit Memo for Invoice Line | 256 | same | ✅ no change |
| Billing Schedule Group Visualization | 256 | same | ✅ no change |
| Billing Profile | 256 | same | 🔄 **enhanced** in 258 (Billing Profile Enhancements) |
| Legal Entity Based Invoice Grouping | 258 | `docs/enablement/258/Invoice Management - Winter '26 Revenue Cloud - External.pdf` | ✅ no change |
| Billing Profile Enhancements | 258 | same | ✅ no change |
| Asset Transfer Support | 258 | same | ✅ no change |
| Co-Terminous Contract Support | 258 | same | ✅ no change |
| Pull-in / Push-Out Support | 258 | same | ✅ no change |
| CPI Uplift Support | 258 | same | ✅ no change |
| Flexible Tax Contract | 258 | same | ✅ no change |
| Credit Taxes Using Same Tax Rate as Original Invoice Date | 258 | same | ✅ no change |
| Credit Memo: Create a Draft & Post | 258 | same | ✅ no change |
| Credit Memo Apply Flow | 258 | same | ✅ no change |
| Legal Entity Defaulting on Billing Transactions | 258 | same | ✅ no change |

---

## Upgrade Guidance from Winter '26

Master PDF "Upgrade Guidance for Spring '26" → Billing section (p 119+) is brief — no major upgrade actions are required for Invoice Management customers. Refer to the master PDF if anomalies occur post-upgrade.

---

## Known Issues for Spring '26 (Billing-related)

### Billing Arrangement Fails During Tax Processing for Split Invoices

Billing arrangement fails intermittently during tax processing when split invoices are partially posted across multiple invoice run batches. Tax validation runs before all split invoices are processed; Billing detects a mismatch between expected billing arrangement lines and posted invoices, causing invoice generation to fail.

**Workaround:** Keep invoice record volume **under 2,000** per batch to reduce likelihood of the issue. (master PDF p 127)

> *Note:* This is primarily an RCB issue (Billing Arrangement is an RCB capability), but Invoice Management readers configuring split-invoice patterns should be aware of the volume threshold.

### Invoice Generation Fails for Large Invoice Address Groups

Invoice generation for billing arrangements fails in core DPE when the associated invoice address group contains **more than 50,000 records**. Processing/fetching that volume can exceed system limits.

**Workaround:** Keep invoice address group records under 50,000 when billing arrangement is used with real-time DPE enabled. (master PDF p 127)

### Standard Tax Engine — Decision Table Matching Treats Missing Values as Valid

The revenue standard tax engine doesn't process the legal entity and product code values as expected. Even if a tax request is missing legal entity and product code values, decision table matching logic still treats them as valid entries — producing inaccurate tax calculations. (master PDF p 127)

**Workaround:** Validate that tax requests always include legal entity and product code values before processing.

---

## Release Overview

Spring '26 Invoice Management (RCA scope) includes the following net-new features:

1. **'All Invoices' Related List on Order** — unified view of all invoices for an order regardless of creation path
2. **Standard Tax Engine** — native configurable tax rates for simple tax use cases (no third-party tax engine integration required)
3. **Header Taxes** — tax calculation at transaction header level (in addition to line level)
4. **Support VAT** — VAT support for LATAM & APAC regions
5. **Summarize using Functional Currency** — full use of legal entity currency for accounting summaries

Cross-area: **Billing-side behavior of Advanced Amendments** — when Swaps/Upgrades/Downgrades, Future-Dated Amendments, Change End Date, Undo Future Dated ARC, Price Amendments, or Multiple Ramp Schedules are executed in Transaction Management, Invoice Management automatically generates the corresponding billing schedule adjustments. Documented in detail under `260-transaction-management-hands-on.md` Features 7–8 with billing-side callouts.

---

## Feature 1: 'All Invoices' Related List on Order

> **Source:** 260 Billing Solution Overview "'All Invoices' Related List on Order" page.

### Business Objective

Billing teams previously struggled to isolate the invoices for a specific order — given the many-to-many relationship between Orders and Invoices. They needed a single source of truth for all invoices ingested or created for a given order, regardless of how those invoices got there.

Spring '26 introduces an **'All Invoices' Related List** that lives directly on the Order record's page layout. It surfaces invoices generated via:

- Invoice Batch Run
- 'Generate Invoices' action
- Invoice Ingestion API

…all in one related list, without complex filtering or reporting logic.

### Use Cases

**Billing Operations persona:**

- **Track full billing history of an order** — open any Order record; the All Invoices related list shows every invoice associated with that order regardless of creation path.
- **Audit invoice provenance** — when a customer questions an invoice charge, the Billing Ops user can confirm which order the invoice came from and how it was created.

### Design Time Configuration

> **Permission required:** Salesforce Admin (page layout / Lightning App Builder access).

1. Open the **Order** object's record page in **Lightning App Builder**.
2. From the component panel, drag the **All Invoices** related list onto the page layout.
3. Save and activate the page layout.

Order records now display the All Invoices related list with all invoices linked to the order via any creation mechanism.

### QuantumBit walkthrough scenario

1. Create a QB customer Order with mixed line items (e.g., QB Server bundle + QB-DB usage product + QB Subscription).
2. Activate the Order.
3. Run an Invoice Batch Run that picks up the Order's billing schedules.
4. Separately, generate an invoice via the **Generate Invoices** action.
5. Open the Order record; verify the All Invoices related list shows both invoices.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview Billing deck doesn't list a dedicated demo URL.

---

## Feature 2: Standard Tax Engine

> **Source:** 260 Billing Solution Overview "Standard Tax Engine" page.

### Business Objective

Customers with **simple tax use cases** previously had to integrate a third-party tax engine (Avalara, Vertex, etc.) or implement custom tax calculation logic. Spring '26 introduces a **native configurable Standard Tax Engine** that captures tax calculation tables natively and integrates seamlessly with Invoice Management for tax calculations.

### Use Cases

**Tax / Billing Admin persona:**

- **Implement simple regional tax rates** — for an org operating in a small number of US states, configure the Standard Tax Engine with state-by-state rates without integrating a third-party engine.
- **Avoid third-party engine costs** — for orgs whose tax compliance needs are straightforward, the native engine eliminates the need for an external integration.

### Design Time Configuration

[NEEDS REVIEW] — full Standard Tax Engine setup details. Pull from master PDF Billing section.

Approximate flow (based on Solution Overview):

1. Configure tax rates in the Standard Tax Engine (table-driven).
2. Associate tax policies with products / product classifications.
3. Activate the engine.

Tax requests during invoicing route through the Standard Tax Engine and apply rates from the configured table.

### Important known issue (260)

> **Decision Table Matching with Missing Values** — the Standard Tax Engine's decision table treats requests with missing `LegalEntity` or `ProductCode` values as valid entries, which can produce inaccurate tax calculations. Validate tax requests carry these fields before processing. (master PDF p 127)

### QuantumBit walkthrough scenario

1. Configure Standard Tax Engine rates for QB customer locations (e.g., 8.875% for NYC, 7.25% for CA).
2. Associate the QB-COMPLETE bundle with a Tax Policy that points to the Standard Tax Engine.
3. Generate an invoice for a QB-COMPLETE order with a CA shipping address.
4. Verify the invoice shows tax calculated at the Standard Tax Engine's CA rate.

### Configuration and Runtime Video

📹 **Demo Link** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 3: Header Taxes

> **Source:** 260 Billing Solution Overview "Header Taxes" page.

### Business Objective

Tax calculations have historically applied at the **line level** — each invoice line gets its own tax calculation. Some scenarios (international shipping fees, regional surtaxes that apply once per invoice rather than per line) need tax calculated at the **transaction header level** instead.

Spring '26 adds **Header Taxes** support — tax computed once at the invoice header, in addition to (or instead of) per-line taxes.

### Use Cases

**Tax Admin persona:**

- **One-time delivery surcharge with VAT** — a delivery fee applies once to the invoice, with VAT calculated at the header level rather than distributed across lines.
- **Regional invoice-level tax** — certain jurisdictions require tax calculation at the invoice level for compliance reasons.

### Design Time Configuration

[NEEDS REVIEW] — full Header Taxes configuration steps. Likely involves a Tax Policy setting for header-level evaluation. Pull from master PDF.

### Configuration and Runtime Video

📹 **Demo Link** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 4: Support VAT

> **Source:** 260 Billing Solution Overview "Support VAT" page.

### Business Objective

VAT is the dominant tax model in **LATAM** (Mexico, Brazil) and **APAC** (Australia, Singapore, India). Spring '26 expands the Standard Tax Engine to support VAT calculation patterns — including reverse-charge VAT, VAT registration thresholds, and country-specific VAT rules.

### Use Cases

**Tax Admin persona:**

- **VAT in Mexico/Brazil/Argentina** — configure VAT rates and rules for LATAM customers without integrating a country-specific tax engine.
- **GST in Australia / India** — apply Goods & Services Tax (a VAT variant) for APAC customers.

### Design Time Configuration

[NEEDS REVIEW] — full VAT configuration. Pull from master PDF Billing → Tax sections.

### Configuration and Runtime Video

📹 **Demo Link** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 5: Summarize using Functional Currency

> **Source:** 260 Billing Solution Overview "Summarize using Functional Currency" page.

### Business Objective

Multinational customers operating with multiple legal entities have separate **functional currencies** per entity (USD for US LE, EUR for European LE, JPY for Japan LE, etc.). Accounting summaries (period-end totals, FX gain/loss, journal entries) historically used the org's master currency. Spring '26 introduces full use of **legal entity currency** for accounting summaries.

### Use Cases

**Accounting / Finance persona:**

- **Per-LE financial close** — at month-end, the EU LE's accounting summary reports in EUR; the JP LE's reports in JPY; the US LE's reports in USD. Each LE's books reconcile in its own functional currency.
- **FX gain/loss tracking** — when receivables collected in foreign currency settle, the gain/loss is properly attributed to the LE's functional currency.

### Design Time Configuration

[NEEDS REVIEW] — full functional currency configuration. Pull from master PDF Billing → Accounting sections.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview Billing deck doesn't explicitly call out a Functional Currency demo.

---

## Cross-Area: Billing-Side Behavior of Advanced Amendments

> **Primary home:** `260-transaction-management-hands-on.md` § Feature 7 (Swaps/Upgrades/Downgrades) + § Feature 8 (Future-Dated Amendments).

When customers execute Advanced Amendments in Transaction Management, Invoice Management automatically handles the corresponding billing schedule adjustments. **No additional billing setup is required** for any of these — they work transparently with RCA + RCB enablement.

| TM Amendment Action | Billing-Side Behavior |
|---|---|
| **Swap / Upgrade / Downgrade** | Negative BSG to adjust the old asset; new BSG for the swapped/upgraded/downgraded product |
| **ARC before FDO (Amend & Renew with Future-Dated Order)** | Billing evaluates existing schedules and creates **adjustment Billing Schedules** that reflect the changes |
| **Change End Date** | Billing autonomously evaluates existing schedules and creates adjustment Billing Schedules |
| **Undo Future Dated ARC (Rollback)** | On order activation, billing creates **negative billing schedules** to counterbalance the previously created schedules |
| **Price Amendments (no quantity change)** | Billing creates negative BS for old pricing + new BS for updated price (260 lifts the prior limitation requiring a quantity change) |
| **Multiple Ramp Schedules** | Billing creates BSG per individual product + BS for all ramped terms |

→ **Full TM walkthroughs:** `docs/enablement/260/260-transaction-management-hands-on.md` Features 7 + 8.

---

## Cross-Area: Consumption Agent — View Overages in Tokens

> **Primary home:** `260-usage-management-hands-on.md` § Feature 5 (Consumption Agent).

The Consumption Agent gains a 260 enhancement — customers with **token-rated resources** can view overages in **tokens** (not just native UoM). This requires **both RCA and RCB licenses**.

**For Invoice Management readers:** the agent's overage visibility surfaces in the same Invoice Management views that show line-level usage charges. No additional configuration needed in Invoice Management; the enhancement is on the Consumption Agent side.

→ **Full configuration:** `docs/enablement/260/260-usage-management-hands-on.md` § Feature 5.

---

## QuantumBit data reference for Invoice Management

`datasets/sfdmu/qb/en-US/qb-billing/` provisions billing design-time configuration for the QB catalog.

### Provisioned Records

[Author: list specific objects from the qb-billing data plan, including:]

- **Billing Policies** — `monthlytotal`, `monthlypeak`, etc.
- **Payment Terms** — net-30, net-60, etc.
- **Tax Policies** — links to Standard Tax Engine rates per region
- **Legal Entities** — for multi-LE walkthroughs (Functional Currency, Header Taxes)
- **Billing Profiles** — per-account billing preferences
- **Sequence Policies** — for invoice numbering compliance

### Sample QB Invoice Walkthroughs

QB's catalog supports two distinct invoice walkthrough patterns:

| Pattern | Suggested QB products |
|---|---|
| **One-time + Subscription invoicing** | QB Complete bundle + QB Subscription product |
| **Usage invoicing** *(requires RCB — defer to RCB exercise)* | QB-DB, QB-TOKENS-PACK |
| **Mixed invoicing** | QB Server (one-time hardware) + QB Subscription + QB-DB usage |
| **Multi-currency / multi-LE** | Configure QB Subscription with EUR pricing for the EU LE; verify Functional Currency summarization |

---

## Open questions for author / PM

1. **Demo URLs** — Solution Overview Billing deck confirms recorded demos for: Standard Tax Engine, Header Taxes, Support VAT (each marked "Demo Link"). Need actual URLs.
2. **Standard Tax Engine setup** — full configuration details (rate table format, tax policy attachment to products) need confirmation from master PDF Billing → Tax sections.
3. **Header Taxes configuration** — exact toggle/setting that enables header-level tax evaluation. Likely on Tax Policy. Pull from master PDF.
4. **VAT configuration** — country-specific VAT rules typically have nuances (reverse charge, B2B vs B2C, registration thresholds). Confirm how the Standard Tax Engine surfaces these for Mexico/Brazil/India use cases.
5. **Functional Currency setup** — multi-LE setup is a heavy initial configuration. Should the Invoice Management exercise include a quick how-to-configure-multiple-LEs callout, or assume that's already done as part of Salesforce Setup?
6. **Carry-forward feature deltas** — none of the 256/258 features are explicitly enhanced in 260, but several (Billing Profile, Tax Policy, Legal Entity defaulting) interact with the new 260 features (Standard Tax Engine, Header Taxes, VAT, Functional Currency). Worth a sentence in carry-forward markers calling out the interaction?
7. **Cross-area amendment cross-reference** — should the cross-area section duplicate any TM walkthrough steps (e.g., "perform a swap, then verify billing adjustments"), or strictly point to TM? Currently strict pointer.
8. **Invoice Management vs. Revenue Cloud Billing decision tree** — should this exercise include a brief "do I need RCB?" decision aid for readers who aren't sure which license they have? Recommendation: yes, add a section.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
