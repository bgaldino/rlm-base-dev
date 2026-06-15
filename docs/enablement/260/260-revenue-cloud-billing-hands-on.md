---
release_version: 260
release_name: "Spring '26"
api_version: 66.0
area: "Revenue Cloud Billing"
document_version: 0.1
status: draft
last_updated: 2026-05-06
authors:
  - Brian Galdino
data_shape: qb
prerequisites:
  - "`cci flow run prepare_rlm_org` completed against the target org"
  - "QuantumBit catalog loaded (`qb=true` feature flag)"
  - "Revenue Cloud Billing license enabled"
  - "Billing data plan loaded (`prepare_billing` flow with `billing=true`) — provisions billing policies, payment terms, tax policies"
  - "Rating set up (`prepare_rating` with `rating=true`) — required for usage invoicing walkthroughs"
  - "DocGen Setup completed — required for invoice document generation"
sources:
  - "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf — master Help compendium § Billing"
  - "docs/salesforce/260/solution-overview-spring-26-billing.pdf — internal Solution Overview deck (Billing, CONFIDENTIAL, 60 pages)"
  - "docs/salesforce/260/feature-index.md — per-area feature inventory (Invoice Management & Billing section)"
  - "datasets/sfdmu/qb/en-US/qb-billing/ — QuantumBit billing data plan"
  - ".cursor/skills/release-enablement/authoring-patterns.md"
---

# Revenue Cloud — Revenue Cloud Billing

**Enablement Exercises** · Version 0.1 (draft), Spring '26

> **Branding note:** Salesforce has rebranded *Revenue Cloud* as *Agentforce Revenue Management* in Spring '26. This exercise series continues to use "Revenue Cloud" throughout 260 to match what users see in the product UI.

> **License scope of this exercise:** Revenue Cloud Billing (RCB) is the **comprehensive billing license** — a superset of Invoice Management. RCB customers get everything Invoice Management provides plus Billing Arrangement, Usage Invoicing, Milestone Charges, Debit Memos, Standalone Billing, full Doc Gen + Email Delivery, GL Accounts + Journal Entries (AR), FX Gain/Loss + Functional Currency, full Payments + Refunds + Collections, and Billing Agents (Agentforce).

> Org / data shape: QuantumBit (`qb`). These exercises assume an org provisioned by `rlm-base-dev`'s `prepare_rlm_org` flow with the QuantumBit catalog and billing/rating data loaded.

---

## Status of this document

🚧 **DRAFT — features verified against Spring '26 Solution Overview Billing deck and feature index.** This is the largest single-license exercise in the catalog (RCB has the broadest feature surface of any Revenue Cloud area). Configuration steps for Tax features, Payments features, and Doc Gen are detailed in the Solution Overview; some master-PDF-deep configuration steps remain `[NEEDS REVIEW]`.

> **Cross-area dependencies:** The TM exercise documents billing-side behavior for all Advanced Amendments. The Invoice Management exercise covers the RCA-shared subset. The Usage Management exercise covers Consumption Agent details. This RCB exercise focuses on **what's RCB-only** plus a brief callback to those linked exercises.

---

## RCA vs RCB Capability Matrix

> Sourced from the 260 Billing Solution Overview comparison table.

| Capability | Invoice Management (RCA) | Revenue Cloud Billing (RCB) |
|---|---|---|
| One-Time & Subscription Charges | ✅ | ✅ |
| **Billing Arrangement, Usage Invoicing, Milestone Charges** | | ✅ |
| **Usage Rating & Consumption calculation** | | ✅ |
| Tax (Standard) | ✅ | ✅ |
| Invoicing, Credits | ✅ | ✅ |
| **More Invoicing — Grouping, Write-off** | | ✅ |
| **Debit Memos** | | ✅ |
| **Standalone Billing for any object or external transaction** | | ✅ |
| **Invoice Doc Gen & Email Delivery (on demand + batch)** | | ✅ |
| Accounting Periods & Closure | ✅ | ✅ |
| **GL Accounts, Journal Entries (AR), FX Gain/Loss, Functional Currency** | | ✅ |
| **Payments, Refunds & Collections** | | ✅ |
| Analytics & Ops Console | ✅ | ✅ |
| **Billing Agents** | | ✅ |

**This exercise focuses on the RCB-only rows** (bold). For shared RCA + RCB features, see `260-invoice-management-hands-on.md`.

---

## Carry-forward inventory (from prior releases)

> Revenue Cloud Billing was introduced as a New Product in 254 (Spring '25). Substantial feature accumulation across 254 + 256 + 258 — the carry-forward inventory is the largest of any 260 exercise.

### From Spring '25 (254 — RCB introduction release)

| Feature | Reference | 260 status |
|---|---|---|
| Revenue Cloud Billing Unified Setup | `docs/enablement/254/Spring '25 Revenue Cloud Billing Hands On Exercises.pdf` | ✅ no change |
| Create Billing Policies, Rules, & Treatments | same | ✅ no change |
| Billing in Advance or Arrears | same | ✅ no change |
| Context Aware Billing Schedule API | same | ✅ no change |
| Configure Invoice Documents | same | 🔄 **enhanced** in 256 (Enhanced Invoice Document Template) and 260 (On Demand Invoice PDF generation — Feature 2) |
| Milestone Billing | same | 🔄 **enhanced** in 256 (Milestone Billing UI) |
| Configure Tax Engine | same | 🔄 **enhanced** in 260 (Tax Treatment Resolution — Feature 11) |
| Multi-Currency Conversion Support | same | 🔄 **enhanced** in 260 (Functional Currency — see Invoice Management Feature 5) |
| One Time Charge Support | same | ✅ no change |

### From Summer '25 (256)

| Feature | Reference | 260 status |
|---|---|---|
| Billing App and Account 360 | `docs/enablement/256/Summer '25 - Revenue Cloud Billing.pdf` | ✅ no change |
| Billing Operations Console | same | ✅ no change |
| Preview Invoice UI and Document Generation | same | ✅ no change |
| Milestone Billing UI | same | ✅ no change |
| Enhanced Invoice Document Template | same | 🔄 **enhanced** in 260 (Feature 2 below) |

### From Winter '26 (258)

258 RCB carry-forward features — see `docs/enablement/258/` for the W'26 RCB Hands-On if it exists separately, or merged into Invoice Management. (The 258 journey map shows Invoice Management with RCB cross-listed.)

---

## Upgrade Guidance from Winter '26

The master PDF "Upgrade Guidance for Spring '26" → Billing section (p 119+) is brief — no major upgrade actions required. Standard configuration migration practices apply.

---

## Known Issues for Spring '26

These ship with 260 GA and affect RCB customers specifically:

### Billing Arrangement Fails Intermittently During Tax Processing

Billing arrangement fails intermittently during tax processing when split invoices are partially posted across multiple invoice run batches. Tax validation runs before all split invoices are processed; Billing detects a mismatch between expected billing arrangement lines and the number of posted invoices, causing invoice generation to fail.

**Workaround:** Keep invoice record volume **under 2,000** per batch. (master PDF p 127)

### Invoice Generation Fails for Large Invoice Address Groups

Invoice generation for billing arrangements fails in core DPE when the associated invoice address group contains **more than 50,000 records**.

**Workaround:** Keep invoice address group records under 50,000 when billing arrangement uses real-time DPE. (master PDF p 127)

### Billing Stores Bill-To Contact Incorrectly During Concurrent Usage Billing

When usage billing runs concurrently for multiple orders, Billing stores the **Bill To Contact** for usage-based billing schedules incorrectly. Result: invoices generate with the wrong Bill To Contact.

**No workaround currently available.** (master PDF p 127)

### Standard Tax Engine — Decision Table Treats Missing Values as Valid

The revenue standard tax engine doesn't process the `LegalEntity` and `ProductCode` values as expected. Even if a tax request is missing these values, decision table matching logic still treats them as valid entries, producing inaccurate tax calculations.

**Workaround:** Validate that tax requests always include legal entity and product code values before processing. (master PDF p 127)

---

## Release Overview

Spring '26 Revenue Cloud Billing includes the following net-new features (in addition to the RCA-shared features documented in `260-invoice-management-hands-on.md`):

### Customer 360 / Service
1. **Billing Service Requests & Dispute Management** — unified intake + automated resolution of billing disputes
2. **On Demand Invoice PDF Generation** — account-specific invoice templates + on-demand single-invoice generation

### Debits & Credits
3. **Credit Memo Sequencing** — gapless sequence numbers on posted Credit Memos for legal compliance
4. **Credit Memo Void & Debit Memo Creation** — voiding a credit memo automatically creates an offsetting debit memo
5. **Convert Debit Memos to Invoices** — Invoice Ingestion API converts debit memos to invoices for collection

### Payments & Collections
6. **Import & Save Externally Generated Tokens** — bring saved payment tokens from existing merchant gateways into RCB
7. **Rule-Based Cash Application** — define rules to prioritize how cash/credits/payments settle invoices
8. **Payment Retry Rules** — automated retry of failed payments based on error category / raw error code
9. **Edit Default Payment Method against Account** — declare a saved token as default for an account

### Consumption & Wallets
10. **Consumption Traceability — API** — per-resource consumption traceability surfaced at usage-resource level
11. **Wallets Support for Partners** — wallet details, balances, and consumption entities for partner/customer community users

### Tax
12. **Tax Treatment Resolution** — extended tax treatment resolution for countries like Brazil and India
13. **Void Taxes / Recovery Enhancements** — void tax on canceled credit memos

---

## Feature 1: Billing Service Requests & Dispute Management

> **Source:** 260 Billing Solution Overview "Billing Service Requests & Dispute Management" page.

### Business Objective

Service reps handling billing disputes have no centralized way to submit cases, track resolution, or view dispute details on behalf of customers — leading to delays, missed follow-ups, and frustrated buyers. Spring '26 introduces a **unified streamlined mechanism** to capture, validate, and resolve billing inquiries + disputes — reducing manual bottlenecks and preventing revenue leakage.

### Use Cases

- **Service Reps raise billing disputes and cases** on behalf of customers in real time — over phone or email — from a single Account view.
- **Billing Ops track open cases, dispute details, and resolution status** at a glance with new UI components built for visibility.
- **Finance teams build custom dispute reports** using the Case Service Process Extension entity — turning case data into actionable billing insights.

### Design Time Configuration

> **Permission required:** Billing Admin + Salesforce Admin.

1. From Setup → **Billing Settings**, enable **Manage Billing Disputes and Service Requests**.
2. Assign **Unified Catalog** permission sets to relevant users.
3. Configure sharing settings for the Billing Service Process objects.
4. Click **Install** on the Billing Service Process templates from the **Unified Catalog**.
5. **Publish** the self-service portal with the Catalog (so community users can raise billing inquiries).
6. Configure **Case Assignment Rules** to auto-route new dispute cases to appropriate queues.

### QuantumBit walkthrough scenario

1. Set up a QB customer Account with active assets and posted invoices.
2. Configure the Billing Service Catalog on the Action Launcher.
3. Configure Case Assignment Rules to route disputes to the **Billing Ops** queue.
4. Publish the self-service portal.
5. As a community user (or Service Rep on behalf of customer), raise a billing inquiry/dispute against an existing invoice.
6. Verify the case routes to the Billing Ops queue, surfaces in the dispute tracking UI, and Finance can pull a custom report.

### Configuration and Runtime Video

[NEEDS REVIEW] — Solution Overview Billing deck doesn't list a dedicated demo URL.

---

## Feature 2: On Demand Invoice PDF Generation

> **Source:** 260 Billing Solution Overview "On Demand Invoice PDF generation" page.

### Business Objective

Businesses require flexibility to **tailor invoice presentation** (branding, fields, language) per customer, plus the ability to **instantly generate and email invoice documents** directly from the invoice record on demand. Spring '26 brings account-specific invoice templates and a Generate Invoice Document quick action.

### Use Cases

**Billing Ops persona:**

- **Override org-default template per customer** — for a high-touch enterprise customer, use a customized invoice template with their branding; for SMB customers, use the org-default template.
- **Regenerate invoice documents on demand** — when an invoice's underlying data changes mid-cycle (rare, but possible during dispute resolution), regenerate the doc using the appropriate billing profile template.

### Design Time Configuration

> **Prerequisite:** DocGen Setup completed.

1. Enable **Document Generation** in Billing Settings.
2. Select an org-default invoice doc template.
3. (Optional) For each Account where customization is needed, configure the **Account's Billing Profile** with a custom invoice doc template that overrides the org-default.

### Runtime use

1. Open an Invoice record.
2. Use the **Generate Invoice Document** quick action.
3. View the existing document, or regenerate using the billing profile template.

### QuantumBit walkthrough scenario

1. Configure DocGen Setup with two invoice templates: one default, one custom-branded for a specific QB enterprise customer.
2. Set the custom template on the enterprise customer's Billing Profile.
3. Generate an invoice for the enterprise customer; use the Generate Invoice Document quick action.
4. Verify the resulting PDF uses the custom-branded template.
5. Generate an invoice for an SMB QB customer (no Billing Profile customization).
6. Verify the resulting PDF uses the org-default template.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 3: Credit Memo Sequencing

> **Source:** 260 Billing Solution Overview "Credit Memo Sequencing" page.

### Business Objective

All posted credit memos must have a **unique gapless sequential code** for legal compliance, audit trails, and reconciliation — particularly important in jurisdictions with strict sequential numbering requirements (much of LATAM, parts of EU and APAC).

### Design Time Configuration

> **Permission required:** Billing Admin.

1. From Setup → Billing Settings, enable:
   - **Configure Gapless Sequential Numbering for Billing**
   - **Mandate Sequence Policy for Posted Credit Memos**
2. Create **Sequence Policies** for Credit Memos with appropriate **selection conditions**.
3. Configure **sequence patterns** that adhere to regional compliance requirements.

### Runtime behavior

Upon credit memo posting, the system **auto-assigns a unique sequential number** based on the matching sequence policy.

### Use Case

Operating in Brazil with strict gapless sequencing requirements:

1. Configure a Sequence Policy with selection condition `LegalEntity = 'BR-LE'`.
2. Configure the sequence pattern as `CM-BR-{YYYY}{0000000}` (year + 7-digit sequence).
3. Post a credit memo for a Brazilian customer.
4. Verify the credit memo gets the next gapless sequential number for the year.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 4: Credit Memo Void & Debit Memo Creation

> **Source:** 260 Billing Solution Overview "Credit Memo Void & Debit Memo Creation" page.

### Business Objective

Customers sometimes issue credits **by mistake** — wrong amount, wrong customer, wrong invoice. Spring '26 introduces **void + auto-debit-memo**: voiding a credit memo automatically creates an offsetting debit memo to nullify the transaction and close the accounting cleanly.

### Use Cases

**Billing Ops persona:**

- **Reverse a mistakenly issued credit** — credit was issued to the wrong customer; void it; system auto-creates a debit memo for the same value, restoring the original receivable balance.

### Design Time Configuration

[NEEDS REVIEW] — full configuration steps. Likely a Billing Settings toggle that enables auto-debit-memo on credit memo void.

### QuantumBit walkthrough scenario

1. Issue a credit memo for a QB customer Account in error.
2. Void the credit memo.
3. Verify a debit memo is auto-created with the same value, nullifying the original transaction.
4. Verify the customer's account balance returns to the pre-credit-memo state.

### Configuration and Runtime Video

📹 **"Credit Memo Void & Debit Memo Creation Demo"** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 5: Convert Debit Memos to Invoices

> **Source:** 260 Billing Solution Overview "Convert Debit Memos to Invoices" page.

### Business Objective

Customers issuing debit memos to charge additional fees previously couldn't easily bill those fees as a formal Invoice. Spring '26 leverages the **Invoice Ingestion API** to convert a debit memo into an Invoice — enabling collection of the additional charges through standard invoicing channels.

### Design Time Configuration

[NEEDS REVIEW] — full Invoice Ingestion API request shape for debit memo conversion. Pull from master PDF.

### Use Case

**Billing Ops persona:**

- **Convert ad-hoc charges to a billable invoice** — debit memo was created for an additional service charge; use the Invoice Ingestion API to spin up a corresponding Invoice for collection.

### Configuration and Runtime Video

📹 **"Convert Debit Memos to Invoices Demo"** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 6: Import & Save Externally Generated Tokens

> **Source:** 260 Billing Solution Overview "Import & Save Externally Generated Tokens" page.

### Business Objective

Customers migrating to RCB from another billing system already have **merchant accounts with payment gateways** and **saved payment tokens** for their customers' payment methods. They expect RCB to support these existing tokens — without forcing them to re-collect customer payment details.

Spring '26 enables **importing externally generated tokens** as `Save Payment Method` records for use in RCB's recurring payment engine.

### Supported payment methods

| Method | Native UI? | 3rd-party gateway support |
|---|---|---|
| Credit Card | ✅ | (implement own gateway components + use `tokenize` API or `Save Payment Method` API) |
| ACH | ✅ | same |
| SEPA | (no native UI yet) | same |
| BACS | (no native UI yet) | same |
| BECS | (no native UI yet) | same |
| BanContact | (no native UI yet) | same |
| Digital Wallet | (no native UI yet) | same |
| BNPL — Affirm, Klarna, AfterPay | (no native UI yet) | same |
| UPI (India) | (no native UI yet) | same |
| PIX (Brazil) | (no native UI yet) | same |

### Use Cases

- **Migration to RCB** — bring already-saved payment tokens from a previous billing platform into RCB's `Save Payment Method` records to continue automated payments processing without customer re-onboarding.

### Design Time Configuration

[NEEDS REVIEW] — exact API endpoints (`tokenize` API, `Save Payment Method` API). Pull from master PDF + developer guide.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 7: Rule-Based Cash Application

> **Source:** 260 Billing Solution Overview "Rule Based Cash Application" page.

### Business Objective

In B2B businesses, **cash on the account** (additional payments, credits, or unapplied amounts) is common. Customers need flexibility to **define rules** for how this cash settles invoices — including **priority order** between credits and payments and the **execution order** among multiple rules.

### Use Cases

- **Define priority** — credits should settle invoices before payments (or vice versa).
- **Define rule execution order** — multiple cash application rules with priority sequence so the most specific rules apply first.
- Applies to invoices generated via **Invoice Batch Run** + **Bill Run**.

### Design Time Configuration

[NEEDS REVIEW] — full rule definition UI / setup steps. Pull from master PDF.

### Configuration and Runtime Video

📹 **"Rule Based Cash Application Demo"** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 8: Payment Retry Rules

> **Source:** 260 Billing Solution Overview "Payment Retry Rules" page.

### Business Objective

Failed payments are a **major contributor to slow cash realization and involuntary churn**. Customers expect their billing engine to handle payment failures gracefully and **attempt retries automatically** — based on the failure reason — without manual intervention.

### Use Cases

- **Define retry rules by error category** — e.g., for "insufficient funds" errors, retry after 3 days; for "expired card" errors, don't retry, escalate to dunning.
- **Define retry rules by raw error code** — for very specific gateway error codes, configure custom retry behavior.

### Design Time Configuration

[NEEDS REVIEW] — full rule UI configuration. Pull from master PDF.

### Configuration and Runtime Video

📹 **"Payment Retry Rules Demo"** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 9: Edit Default Payment Method Against Account

> **Source:** 260 Billing Solution Overview "Edit Default Payment Method against Account" page.

### Business Objective

In automated payments processing, customers must be able to **declare a payment method as default** against the customer account — so this default is used for subsequent payments if the chosen method fails. Spring '26 introduces an EDIT API that lets customers programmatically declare a saved token as default.

### Design Time Configuration

[NEEDS REVIEW] — exact EDIT API endpoint and request shape.

Approximate flow:

1. Use the EDIT API to set a saved token / `Save Payment Method` record as default against an Account.
2. The default applies across any gateway the account uses.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 10: Consumption Traceability — API

> **Source:** 260 Billing Solution Overview "Consumption Traceability- API" page.

### Business Objective

Customers using usage-based billing need **clear understanding of their usage end-to-end** — including how usage affects billing, entitlements, renewals, and overage rates. Without this visibility, confusion arises about charges. Spring '26 introduces an API exposing **per-resource consumption traceability**.

### Use Cases

- Tech Innovators Inc. needs traceability on overages to identify usage patterns, monitor resource allocation, understand drawdowns from commits and grants, and see the rates used for computing overages — for cloud spending optimization, predictability, and compliance.

### What the API exposes

For each billing period:

- **Total consumption** per usage resource
- **Overage quantity** + amounts
- **Final unit rate** for the period
- **Consumption sources** — distinguishes drawdown from a **grant** vs. drawdown from a **commitment**
- Billing periods with associated usage resources surfaced
- Asset listings with billing periods

### Design Time Configuration

> **No configuration needed.** Users consume the API directly.

Pass the **`LiableSummaryId`** in the API request to obtain consumption traceability for that liable summary period.

### QuantumBit walkthrough scenario

1. Set up QB customer with usage assets (QB-DB, QB-TOKENS-PACK).
2. Generate consumption for a billing period.
3. Use the Consumption Traceability API with the customer's LiableSummaryId.
4. Verify the API returns: per-resource consumption, overage quantities/amounts, final unit rates, drawdown sources (grant vs commitment).

### Configuration and Runtime Video

📹 **Demo Link** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 11: Wallets Support for Partners

> **Source:** 260 Billing Solution Overview "Wallets support for Partners" page.

### Business Objective

Partner and customer community users on **Experience Cloud** previously had no access to wallet details — wallet balances, consumed units per usage resource, etc. Spring '26 exposes wallet details, statements, and consumption entities for partner/customer users.

### Design Time Configuration

> **Permission required:** Billing Admin + Experience Cloud Admin.

1. Add the **"Wallet Details"** tab on the Account page in the partner/customer community site.
2. Configure visibility against Assets, BOCE (Billing Operating Customer Entity), and Contracts as applicable.
3. (Optional) Enable drill-down to **Wallet Statement** on `UsageEntitlementBucket` for granular Usage Details.
4. (Optional) Configure the **Billing Self-Service portal template** — Wallet is available as a flexipage OOTB.

### Use Cases

- **Self-service balance check** — partner users see current balances of usage resources on their Account page in the community.
- **Granular usage drill-down** — drill from balance summary into per-bucket consumption detail.
- **Self-service portal access** — RCB Self-Service portal template provides Wallet as a built-in flexipage.

### Configuration and Runtime Video

📹 **Demo Link** — confirmed in Solution Overview Billing deck. [NEEDS REVIEW — get URL.]

---

## Feature 12: Tax Treatment Resolution

> **Source:** 260 Billing Solution Overview "Tax Treatment Resolution" page.

### Business Objective

Existing Tax Treatment Resolution **stops at certain depths** — limiting taxation in countries with multi-step compliance like **Brazil and India**. Spring '26 enhances Treatment Selection by adding **Information** along with **Legal Entity** to the resolution logic.

### Use Cases

- **Brazil tax compliance** — multi-tier tax rules (federal + state + municipal) require resolution beyond the prior single-step depth.
- **India GST compliance** — CGST + SGST + IGST resolution depending on inter-state vs intra-state transactions.

### Design Time Configuration

[NEEDS REVIEW] — full Tax Treatment Resolution enhancement details. Pull from master PDF.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Feature 13: Void Taxes / Recovery Enhancements

> **Source:** 260 Billing Solution Overview "Void Taxes / Recovery Enhancements" page.

### Business Objective

When credit memos that have been **posted** are later **canceled / voided**, the corresponding tax records on those memos must be voided too. Spring '26 enables voiding tax on a posted-then-canceled credit memo with proper recovery handling.

### Design Time Configuration

[NEEDS REVIEW] — full void+recovery configuration. Pull from master PDF.

### Configuration and Runtime Video

[NEEDS REVIEW]

---

## Cross-Area: Billing-Side Behavior of Advanced Amendments

> **Primary home:** `260-transaction-management-hands-on.md` § Features 7 + 8.

When TM Advanced Amendments execute, RCB automatically generates the corresponding billing schedule adjustments. **No additional billing setup needed** beyond core RCB enablement.

| TM Action | Billing-Side Behavior |
|---|---|
| Swap / Upgrade / Downgrade | Negative BSG to adjust old asset; new BSG for new product |
| ARC before FDO | Adjustment Billing Schedules reflecting the changes |
| Change End Date | Adjustment Billing Schedules autonomously created |
| Undo Future Dated ARC (Rollback) | Negative billing schedules to counterbalance |
| Price Amendments (no quantity change) | Negative BS for old pricing + new BS for updated price |
| Multiple Ramp Schedules | BSG per individual product + BS for all ramped terms |

→ **Full TM walkthroughs:** `docs/enablement/260/260-transaction-management-hands-on.md` Features 7 + 8.

---

## Cross-Area: Consumption Agent (Agentforce) — Token Overage Visibility

> **Primary home:** `260-usage-management-hands-on.md` § Feature 5 (Consumption Agent).

The Consumption Agent in 260 gains the ability to **view overages in tokens** (not just native UoM). **Requires both RCA and RCB licenses** — RCA provides the agent and Usage Management context; RCB provides the token-resource billing logic.

### Use Case (token overage view)

For a customer using a cloud service that charges for storage (rated 2 Flex Credits/GB) and compute (rated 3 Flex Credits/hour), overages can now be viewed **in Flex Credits at resource level** — not just in GB or hours separately. Helps with budgeting, forecasting, and proactive token-pack purchasing.

→ **Full configuration:** `docs/enablement/260/260-usage-management-hands-on.md` § Feature 5.

---

## Cross-Area: RCA-Shared Features

For features available with both RCA and RCB licenses:

- **'All Invoices' Related List on Order**
- **Standard Tax Engine, Header Taxes, Support VAT**
- **Functional Currency support**

→ See `260-invoice-management-hands-on.md` Features 1–5.

---

## QuantumBit data reference for Billing

`datasets/sfdmu/qb/en-US/qb-billing/` provisions billing design-time configuration for the QB catalog.

### Sample QB Billing Walkthroughs

| Feature | Suggested QB walkthrough |
|---|---|
| On Demand Invoice PDF | Use a QB enterprise customer Account with a custom Billing Profile + customized template |
| Credit Memo Sequencing | Configure for QB-BR-LE legal entity with regional compliance pattern |
| Credit Memo Void + Debit Memo | Issue a credit on a QB-COMPLETE invoice in error; void it; verify auto-debit |
| Convert Debit Memos to Invoices | Issue a debit memo for an additional service charge on a QB customer; convert via API |
| Import External Tokens | Mock external CC tokens for QB customers; verify `Save Payment Method` records created |
| Rule-Based Cash Application | Configure rules for QB customer Accounts; run Invoice Batch Run + Bill Run |
| Payment Retry Rules | Configure retry rules for "insufficient funds" + "expired card"; trigger failed payments via test gateway |
| Default Payment Method | Set default token for a QB customer Account via EDIT API |
| Consumption Traceability | QB-DB usage with overages — hit the API with the customer's LiableSummaryId |
| Wallets for Partners | QB partner community user accessing their organization's wallet |

---

## Open questions for author / PM

1. **Demo URLs** — Solution Overview Billing deck confirms demos for: Credit Memo Void & Debit Memo Creation, Convert Debit Memos to Invoices, Rule-Based Cash Application, Payment Retry Rules, Consumption Traceability, Wallets Support for Partners. Need actual URLs.
2. **Tax Treatment Resolution detail** — extension to support Brazil/India needs deeper master-PDF research.
3. **Void Taxes detail** — recovery semantics need confirmation.
4. **Payment API details** — Save Payment Method API + tokenize API + EDIT API endpoints. Pull from developer guide.
5. **Cash application rule UI** — full setup steps. Pull from master PDF.
6. **Payment retry rule UI** — same.
7. **258 RCB carry-forward** — the Winter '26 Invoice Management exercise covered RCB-relevant content, but is there a separate 258 RCB doc that should be cross-referenced?
8. **Migration aid** — should this exercise include a "Moving from RCA Invoice Management to RCB?" decision aid for customers evaluating the upgrade? Recommendation: yes.
9. **End-to-end scenario** — should 260 add a stitched scenario covering a full RCB flow (subscription order → recurring billing → consumption rating → invoice generation → payment → dunning)? Probably yes given RCB's breadth.

---

## Footer (rendered at end of distribution PDF)

© Copyright 2000–2026 Salesforce, Inc. All rights reserved. Salesforce is a registered trademark of Salesforce, Inc., as are other names and marks.
