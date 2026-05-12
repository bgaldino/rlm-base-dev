# Modules 4 + 5 — 262 Snapshot LO Validation Report

**Date:** 2026-05-12
**Validator:** Claude (via revenue-cloud-docs skill)
**Source of truth:** `docs/salesforce/262/help/articles/` (838 articles across 10 RC functional areas, captured 2026-05-11 / 2026-05-12)
**Subject doc:** `docs/trailhead-l2-review/modules-3-4-5-proposed-los.md` (Module 4 and Module 5 sections)
**Scope:** LO-level validation only. Body content is not yet authored for Modules 4 / 5.

## TL;DR

Modules 4 and 5 LOs are **mostly accurate** against the complete 262 snapshot. The data model objects (BillingArrangement, DebitMemo, PaymentGatewayProvider, etc.) are confirmed. The invoice production chain (Invoice Scheduler → DocGen → Email) is correct. The agent product names (Subagent: Invoice Line Explanation, Subagent: Billing Collections Management) are now grounded against verified Help articles. There are **four substantive corrections** to apply across the two modules before body content authoring, plus **two open questions for Mike**.

**Substantive corrections:**

1. **M5 LO 1.1 — native gateway framing is structurally off.** Salesforce Payments is the *feature* that wraps native gateway integrations to **Stripe and Adyen** — not a gateway itself. The LO currently says "Salesforce Payments and Adyen" as two separate gateways; the actual structure is "Salesforce Payments → Stripe and Adyen."
2. **M5 LO 1.3 — "Smart Retry" naming.** The 262 Help portal calls this feature **Payment Retry Rules** (with **Payment Retry Rule Sets** as the parent). "Smart Retry" doesn't appear. The underlying mechanic (configure retry intervals per error category) matches the LO's intent but the formal name is different. "Soft decline vs hard decline" framing also doesn't appear — 262 uses **payment gateway error category** + optional error code.
3. **M5 LO 1.4 — "Payment Runs" formal name.** The 262 product names: **Payment Batch Run** is the record type; **Payment Scheduler** is the configuration (a Billing Batch Scheduler with Job Type = Payment). Same naming pattern as Invoice Batch Run / Invoice Scheduler. LO should mention both names.
4. **M5 LO 2.2 — capability naming for the Billing Collections Management subagent.** The 262 article surfaces two specific named actions: **Get Account Billing Summary** and **Get Dunning Strategy** (both singular). M5 LO 2.2's earlier framing of "Account Billing Summaries" and "Dunning Strategy Recommendations" (both plural, from Mike's pre-GA naming) is close but not the 262-shipped names.

**Module 4 corrections:** None substantive — the LOs already incorporated the formal-name notes from earlier prep ("Invoice Batch Run" as the formal name behind "Bill Run," "Document Generation Service" as the formal name behind "DocGen"). The "Subagent: Invoice Line Explanation" naming is already correct per the prior agents-snapshot validation.

---

## Module 4 — confirmed against snapshot

All M4 LOs hold against the 262 snapshot:

| LO | Status | Citation |
|---|---|---|
| 1.1 — BillingArrangement / BillingArrangementLine | ✓ | `ind.billing_billing_arrangements.htm`, `ind.billing_billing_arrangement_create.htm`, `ind.billing_setup_billing_arrangements.htm` |
| 1.2 — BillDayOfMonth / NextBillingDate | ✓ | `ind.billing_understand_period_boundaries_and_billing_day_of_month.htm`, `ind.billing_billing_profiles_create.htm` |
| 1.3 — Bill Run (formal: Invoice Batch Run) | ✓ | `ind.billing_invoice_batch_run.htm` titled "Invoice Batch Run Process" |
| 1.4 — Debit Memo Lines convert to Invoice Lines based on NextBillingDate | ✓ | `ind.billing_debit_memo.htm` titled "Manage Debit Memos in Agentforce Revenue Management" — confirms "When debit memo lines are converted to invoice lines, the balance of the related invoices increases." |
| 2.1 — Invoice Scheduler → Document Generation Service → Send Invoices Through Email | ✓ | Verified earlier in M2v2 work + `ind.billing_setup_document_generation.htm` |
| 2.2 — Convert Negative Invoice Lines to Credit Memo Lines | ✓ | `ind.billing_setup_negative_invoice_lines_conversion_to_credit_memo_lines.htm` |
| 2.3 — Self-Service Portal | ✓ | `ind.billing_self_service_portal.htm` titled "Self-Service Billing Portal" |
| 2.4 — Invoice Line Explanation subagent | ✓ | `ind.rev_agent_billing_topic_invoice_line_explanation.htm` (per agents snapshot) |

**No substantive M4 LO changes needed.** The LO list is body-content ready.

---

## Module 5 — substantive corrections needed

### M5 LO 1.1 — Salesforce Payments structure

**Current text:**
> 1.1 Configure connections to natively supported payment gateways: Salesforce Payments and Adyen.

**What 262 actually documents** (per `ind.billing_setup_salesforce_payments_features.htm`):
> "Accept electronic payments from your customers on Stripe and Adyen payment gateways by using the Salesforce Payments native payment service."

**Salesforce Payments is the native payment service that integrates to Stripe AND Adyen** — both are equally first-class native gateways via Salesforce Payments. The LO currently treats Salesforce Payments and Adyen as parallel gateways, which is structurally wrong.

**Proposed rewrite:**
> 1.1 Configure native payment gateway connections through **Salesforce Payments** to **Stripe** and **Adyen** — the two gateways natively supported by Salesforce Payments.

### M5 LO 1.3 — "Smart Retry" → "Payment Retry Rules"

**Current text:**
> 1.3 Configure Smart Retry rules to differentiate soft declines from hard declines.

**What 262 actually documents** (per `ind.billing_setup_payment_retry_rules.htm`):
- The feature is called **Payment Retry Rules** (rules) with **Payment Retry Rule Sets** (the parent grouping).
- Rules are scoped by **payment gateway error category** + optional error code, not by "soft / hard decline" binary.
- Retry interval types: **Fixed** (consistent intervals between attempts) or **Staggered** (varied intervals).
- Max retry attempts cap at 10 for Fixed; max interval value 60.

"Smart Retry" doesn't appear in the 262 Help portal. "Soft decline vs hard decline" doesn't appear either — the 262 framing is per-error-category with explicit retry intervals.

**Proposed rewrite:**
> 1.3 Configure **Payment Retry Rules** and **Payment Retry Rule Sets** to retry failed payments by gateway error category, with Fixed or Staggered retry intervals.

### M5 LO 1.4 — "Payment Runs" → "Payment Batch Runs" + "Payment Scheduler"

**Current text:**
> 1.4 Set up Payment Runs to sweep posted invoices automatically against connected gateways.

**What 262 actually documents** (per `ind.billing_payment_runs_schedule.htm` titled "Schedule Payment Batch Runs to Process Payments"):
- **Payment Scheduler** is the configuration record (created via "Billing Batch Schedulers → New Payment Scheduler"). It's a Billing Batch Scheduler with Job Type = Payment.
- **Payment Batch Run** is the record created at the scheduler's start time. Same shape as Invoice Batch Run from Module 4.
- Payment Schedules and Payment Schedule Items are the underlying payment-side records the batch run processes.

The naming pattern is identical to Module 4's Invoice Batch Run / Invoice Scheduler — useful for cross-module consistency.

**Proposed rewrite:**
> 1.4 Set up a **Payment Scheduler** (a Billing Batch Scheduler with Job Type = Payment) to create **Payment Batch Runs** that automatically collect payments against connected gateways and apply them to posted invoices.

### M5 LO 2.2 — Subagent capability naming

**Current text:**
> 2.2 Describe how the **Billing Collections Management** subagent (under the **Agentforce for Billing Employee Assistance** parent agent) helps collections teams assess account health, highlight high-risk invoices based on payment history, disputes, and outstanding balances, and surface recommended next actions.

**What 262 actually documents** (per `ind.rev_agent_topic_billing_collections_management.htm`):
- The subagent name is correct: **Subagent: Billing Collections Management**.
- API Name: `BillingCollections`.
- Two named actions: **Get Account Billing Summary** (singular) and **Get Dunning Strategy** (singular).
- Required Setup: Billing Collections AND Recovery Specialist permission sets.

The current LO description is accurate but doesn't name the two specific actions. Adding them gives sellers concrete handles.

**Parent agent naming consistency call needed.** The L2 mix straddles two documented parent agents:
- **Agentforce for Revenue Management** (the suite of 7 subagents, captured in the dedicated agents area `ind.rev_agent_*`).
- **Agentforce for Billing Employee Assistance** (a Billing-area-scoped product covering 3 subagents — Invoice Line Explanation, Billing Collections Management, Billing Inquiries — same articles surface from `ind.billing_agentforce_*` paths).

Both names are documented. **Recommendation: pick one parent name and use it consistently across Modules 1, 4, and 5.** Since Module 3 needs the broader "Agentforce for Revenue Management" name to include the Consumption Management subagent, using the same name in M4 and M5 keeps the subagent taxonomy coherent across the L2 mix. M5 LO 2.2 should switch from "Agentforce for Billing Employee Assistance" to "Agentforce for Revenue Management."

**Proposed rewrite:**
> 2.2 Describe how the **Subagent: Billing Collections Management** (under the **Agentforce for Revenue Management** agent suite) helps collections teams assess account health and recommend next actions through two named capabilities: **Get Account Billing Summary** (high-risk invoices, late payment history, open disputes) and **Get Dunning Strategy** (recommended dunning approach based on prior communications, payment history, and open disputes).

### M5 LO 2.3 — Manage Billing Disputes — confirmed

Per `ind.billing_manage_disputes.htm` (from prior M2v2 validation): the dispute management feature exists with the capabilities the LO describes (capture, validate, resolve from Self-Service Portal). The LO holds.

### M5 LO 2.4 — Self-Service Portal payment surface — confirmed

Per `ind.billing_self_service_portal_pay_invoices.htm` (titled "Pay Invoices with the Self-Service Billing Portal"): "When your customers log in to the self-service billing portal, they can view invoices, download invoice PDF documents, and pay outstanding balances for the invoices." Also per `ind.billing_generate_pay_now_payment_links_for_business_accounts.htm`: the Pay Now link is a real product capability. LO holds.

### M5 LO 2.5 — DSO framing — confirmed

The LO is about positioning skill rather than a product feature, so the 262 Help doesn't directly validate it. But the underlying capability (Payment Batch Runs + Dunning Orchestration + Subagent: Billing Collections Management) is exactly what reduces DSO. LO holds.

---

## Open questions for Mike

1. **Parent agent name consistency (M5 LO 2.2 + cross-module).** Recommend standardizing on **Agentforce for Revenue Management** across Modules 1, 3, 4, and 5 for taxonomy coherence. M5 LO 2.2 currently uses "Agentforce for Billing Employee Assistance" (also valid). Confirm direction.
2. **"Smart Retry" as marketing branding.** If "Smart Retry" is the official seller-facing brand name for what Help docs call Payment Retry Rules, the LO can keep "Smart Retry" in the headline and add "(formally: Payment Retry Rules)" parenthetically. Otherwise, drop "Smart Retry" entirely and use Payment Retry Rules everywhere. Same pattern decision as Bill Run / Invoice Batch Run in M4.

---

## Recommended LO edit sequence

If you want to apply these in priority order:

1. **M5 LO 1.1 rewrite** — Salesforce Payments structure (Stripe + Adyen are the gateways, Salesforce Payments wraps them).
2. **M5 LO 1.3 rewrite** — Smart Retry → Payment Retry Rules + Rule Sets, drop soft/hard decline framing.
3. **M5 LO 1.4 rewrite** — Payment Runs → Payment Batch Runs + Payment Scheduler.
4. **M5 LO 2.2 rewrite** — name the two actions (Get Account Billing Summary, Get Dunning Strategy), align parent agent name.
5. **Cross-module parent-agent name standardization** — Mike's input on Open Question 1, then apply consistently to M1, M3, M4, M5.

After Mike confirms direction on the parent agent name and Smart Retry branding, M4 + M5 are body-content ready (same maturity level as M3 was when M3 v2 drafting started).

---

*All citations resolve to articles in `docs/salesforce/262/help/articles/`. Where a claim depends on project metadata rather than the snapshot, the citation says so explicitly.*
