# Mike's Comments on Modules 3 / 4 / 5 Proposed LOs

**Date captured:** 2026-05-12 (Google Docs version 1WiRfAg6uoTCLwdWBpIAzEm0p9hXguRClN1OFmv2af1s)
**Source doc state:** Mike's suggestions are against a version of `modules-3-4-5-proposed-los.md` that **pre-dates** the substantive corrections we applied after the M3 LO validation report and the M4+M5 LO validation report. He's reviewing the older LO text, not the post-validation version currently in the repo.
**Captured suggestions:** 22 total

## How to read this document

Each row pairs Mike's suggestion with the corresponding LO in the **current** repo state (after our validation work) and proposes a response.

Three kinds of responses:

- ✅ **Accept** — Mike's change matches our current state, or it's a structural fix (renumbering, reordering, adding/removing LOs) we'd apply as-is.
- ⚠️ **Tension** — Mike's wording conflicts with a 262-snapshot-grounded change we made. Need his call.
- 🔧 **Refine** — Mike's intent is right but the specific phrasing needs adjustment for evergreen-language or AI Review Checklist patterns.

---

## Module 3

### Mike's changes on Unit 2 LO 2.3 (Rating Procedure description)

| # | Mike's suggestion | Current repo state | Response |
|---|---|---|---|
| 1 | Delete: "consumes Asset Rate Card Entries and Asset Rate Adjustments to" | LO 2.3 already mentions "Rating Procedures (Default Rating Procedure or Negotiable Rating Procedure ... ) and Rating Discovery Procedures" | ⚠️ **Tension.** Removing the "consumes Asset Rate Card Entries and Asset Rate Adjustments to produce" phrasing simplifies the LO but loses the mechanical link to the rating inputs. Recommend keeping but tightening. |
| 2 | Add: "s" (minor typo fix on "produce" → "produces") | Current LO already says "produce" correctly | ✅ Accept (already in current state). |

### Mike's changes on Unit 2 LO 2.4 (Mediation note)

| # | Mike's suggestion | Current repo state | Response |
|---|---|---|---|
| 3 | Comment: "I dont think we need a learning objective for this one" | LO 2.4: "Recognize that mediation (cleaning and normalizing raw usage data before it reaches the Transaction Journal) is customer-side responsibility, not part of Revenue Cloud Billing." | ⚠️ **Tension.** Mike originally said (in v1 review) "The system does not support Mediation, remove this" — and we ADDED LO 2.4 to make that boundary explicit. Mike now wants the boundary statement gone too. **Recommend keeping as a body-content paragraph in the v2 draft** (already done — M3 v2 Unit 2 includes a "Mediation is Customer-Side" section). Drop LO 2.4 from the LO list per Mike's direction. |
| 4 | Delete: entire LO 2.4 ("2.4 Recognize that mediation...") | Same as above | ✅ Accept — drop LO 2.4 from the LO list. Body content already covers this in M3 v2 draft. |

### Mike's changes on Unit 3 LO 3.2 (Drawdown Policies)

| # | Mike's suggestion | Current repo state | Response |
|---|---|---|---|
| 5 | Add: "3.2 Describe how Drawdown and Rollover Policies impact Usage Entitlement Buckets." | LO 3.2: "Describe the three Drawdown Policies (Expiring First, Granted First, Granted Last) and how the system applies them automatically to Usage Entitlement Buckets — they are not user-configured." | 🔧 **Refine.** Mike wants to broaden the LO to include **Rollover Policies** (which the 262 snapshot confirms exist as a separate concept — the rollover policy on `TransactionUsageEntitlement` controls how unused grants carry over). His simpler wording loses the three named values. Recommend combining: include both Drawdown and Rollover concepts plus the three Drawdown Order values. |
| 6 | Delete: existing LO 3.2 | Same as above | (paired with #5; merge into one LO) |

---

## Module 4

### Mike's changes on Unit 1 LO 1.3 (Bill Run)

| # | Mike's suggestion | Current repo state | Response |
|---|---|---|---|
| 7 | Replace: "and" with "to" | LO 1.3: "Map how the Bill Run (formal product name: **Invoice Batch Run**) picks up ready-to-bill Billing Schedules and produces Invoices and Invoice Lines." | 🔧 **Refine.** Mike wants the LO to flow "...Billing Schedules **to** produce Invoices." — better grammar. ✅ Apply. |
| 8 | Delete: "s" (probably on "produces" → "produce") | Same as above | ✅ Apply paired with #7 — "to produce" not "to produces". |
| 9 | Replace: "and Invoice Lines." with "." | Same as above | ✅ **Apply.** Mike's tightening — drop "and Invoice Lines" since Invoice Lines are an obvious component of Invoices. LO becomes "...to produce Invoices." |

### Mike's changes on Unit 1 LO 1.4 (Debit Memos)

| # | Mike's suggestion | Current repo state | Response |
|---|---|---|---|
| 10 | Replace: "Describe how Debit Memo Lines convert to Invoice Lines based on Next Billing Date." with "Analyze the automated conversion of debit memo lines into invoice lines" | Same as the existing text | ⚠️ **Tension.** Mike's verb shifts from "Describe" to "Analyze" — a stronger verb for Bloom's taxonomy purposes. But the original explicitly cites the NextBillingDate mechanism, which is the concrete connector. Recommend: "Analyze the automated conversion of Debit Memo Lines into Invoice Lines, driven by `NextBillingDate` on the Debit Memo record." |

---

## Module 5 — significant restructuring

### Mike's changes on Unit 1 — reorder Payment Runs and Smart Retry

Mike's suggestions reorganize Unit 1 LOs 1.3 and 1.4. The current order is:
- 1.3 Payment Retry Rules
- 1.4 Payment Scheduler / Payment Batch Runs

Mike wants:
- 1.3 Payment Runs (Payment Batch Run sweeping invoices)
- 1.4 Smart Retry strategy

| # | Mike's suggestion | Current repo state | Response |
|---|---|---|---|
| 11 | Replace: "Configure connections to natively supported payment gateways: Salesforce Payments and Adyen." with "Establish integrations between the billing system and payment gateways to enable secure payment processing." | LO 1.1: "Configure native payment gateway connections through **Salesforce Payments** to **Stripe** and **Adyen** — the two gateways natively supported by the Salesforce Payments service." | ⚠️ **Tension.** Mike's reword is more abstract and loses the specific Stripe + Adyen names. Our snapshot-grounded version is more concrete (and matches M2v2/M3v2/M4v2 conventions for naming actual products). Recommend: **keep our version** but flag for Mike's call. |
| 12 | Add: "1.3 Set up Payment Runs to sweep posted invoices automatically against connected gateways." | LO 1.4: "Set up a **Payment Scheduler** (a Billing Batch Scheduler with Job Type = Payment) to create **Payment Batch Runs** that automatically collect payments against connected gateways and apply them to posted invoices." | 🔧 **Refine.** Mike's wording is more accessible ("Payment Runs sweep posted invoices"); our wording is more accurate (Payment Scheduler / Payment Batch Run dual-name). Recommend merge: use Payment Run as the seller-facing term, cite Payment Batch Run as the formal name. Same dual-name pattern as Bill Run / Invoice Batch Run in M4. |
| 13 | Replace: "3" with "4" (renumber) | (numbering change) | ✅ Apply (paired with #15). |
| 14 | Replace: "Configure Smart Retry rules to differentiate soft declines from hard declines." with "Implement a Smart Retry strategy that optimizes recovery rates" | LO 1.3: "Configure **Payment Retry Rules** and **Payment Retry Rule Sets** to retry failed payments by gateway error category, with **Fixed** or **Staggered** retry timing." | ⚠️ **MAJOR TENSION — open question resolution.** Mike's still using "Smart Retry" branding (which was one of my open questions). He confirms it's a real product name we should use. **But** the 262 Help portal calls this "Payment Retry Rules" — Smart Retry doesn't appear. Recommend: use Mike's branding ("Smart Retry strategy") in the LO with "(implemented via Payment Retry Rules and Payment Retry Rule Sets)" as a parenthetical. Mike's wording "optimizes recovery rates" is more value-statement; my wording is more concrete. Lean toward Mike's framing for sellers; keep the implementation noun cited. |
| 15 | Delete: "1.4 Set up Payment Runs..." | (old position) | ✅ Apply (paired with #12 — the LO moves from 1.4 to 1.3). |

### Mike's changes on Unit 2 — major restructure

Mike wants Unit 2 to be ordered:
- 2.1 Self-Service Portal payment surface (was 2.4)
- 2.2 Dunning workflows
- 2.3 Manage Billing Disputes
- 2.4 DSO articulation (was 2.5)
- 2.5 Collections Agent (was 2.2)

| # | Mike's suggestion | Current repo state | Response |
|---|---|---|---|
| 16 | Add: "2.1 Set up the Self-Service Portal's payment surface: Pay Now link, payment method updates, one-time payments." | Currently LO 2.4 | ✅ Apply renumbering — move to 2.1 (Mike prioritizes Self-Service first). |
| 17 | Replace: "1" with "2" (renumber Dunning) | Currently LO 2.1 | ✅ Apply paired with #16/#18. |
| 18 | Replace: "Configure automated Dunning workflows to escalate aging invoices through email, SMS, and portal nudges." with "Execute automated Dunning workflows to reduce Days Sales Outstanding (DSO) by deploying tiered communications across multiple channels." | Currently LO 2.1 | 🔧 **Refine.** Mike rewords to lead with the DSO outcome (the business value). Recommend a hybrid: "Configure automated Dunning workflows that deploy tiered communications across email, SMS, and portal — reducing Days Sales Outstanding (DSO) for aging invoices." Keeps the concrete channels AND the DSO outcome. |
| 19 | Delete: "2.2 Describe the Collections Agent's role..." (current position) | Currently LO 2.2 | ✅ Apply paired with #22 — Collections Agent moves to 2.5. |
| 20 | Delete: "2.4 Set up the Self-Service Portal's payment surface..." (current position) | Currently LO 2.4 | ✅ Apply paired with #16 — moves to 2.1. |
| 21 | Replace: "5" with "4" (DSO LO renumber) | Currently LO 2.5 | ✅ Apply paired with #22. |
| 22 | Add: "2.5 Describe the Collections Agent's role in producing Account Billing Summaries and Dunning Strategy Recommendations." | Currently LO 2.2 with this content (just at a different number) | ⚠️ **MAJOR TENSION — open question resolution.** Mike's keeping the **"Collections Agent"** naming with capabilities **"Account Billing Summaries"** and **"Dunning Strategy Recommendations"** (plural). Per the 262 snapshot, the actual product is **Subagent: Billing Collections Management** (API name `BillingCollections`) with actions **Get Account Billing Summary** and **Get Dunning Strategy** (singular). **Mike's using pre-GA branding; the GA-shipped names are different.** Recommend pushing back politely with the snapshot evidence — but he's the SME, so if he confirms after seeing the evidence, we use his preferred naming. |

---

## Two cross-module open questions Mike's comments resolve

1. **"Smart Retry" branding (Open Question 2 from M4+M5 validation report).** Mike's suggestion #14 confirms he wants "Smart Retry" as the seller-facing brand name. The 262 Help portal calls this Payment Retry Rules; Mike's name is pre-GA marketing. **Decision: use "Smart Retry" in LO/body with "(via Payment Retry Rules)" as the formal-name parenthetical.** Same Bill-Run-style dual-name pattern.

2. **Collections Agent naming (Open Question 1 / parent agent consistency).** Mike's suggestions #19 + #22 keep "Collections Agent" with plural "Account Billing Summaries" + "Dunning Strategy Recommendations." The 262 Help portal calls this Subagent: Billing Collections Management under Agentforce for Revenue Management, with singular "Get Account Billing Summary" + "Get Dunning Strategy" actions. **Recommend asking Mike directly** — this affects M1v2, M4v2, and M5v2 body drafts. If he confirms the pre-GA naming after seeing the snapshot evidence, we update all four drafts. If he agrees the GA naming is correct, no body changes needed.

---

## Proposed action plan

### Group A — Apply faithfully (low-risk structural changes)

| Mike's # | Change |
|---|---|
| 4 | Drop LO 2.4 mediation note from M3 LOs (body-content paragraph in M3 v2 stays). |
| 7, 8, 9 | M4 LO 1.3: "...Billing Schedules to produce Invoices." (drop "and Invoice Lines"). |
| 12, 13, 15 | M5 LO restructure: Payment Runs at 1.3 (was 1.4). |
| 16, 17, 20 | M5 LO restructure: Self-Service Portal at 2.1 (was 2.4). |
| 19, 21, 22 | M5 LO restructure: Collections Agent at 2.5 (was 2.2). |

### Group B — Apply with refinement (preserves Mike's intent + grounding)

| Mike's # | Refined approach |
|---|---|
| 1 | M3 LO 2.3: tighten by dropping "consumes Asset Rate Card Entries and Asset Rate Adjustments to" while keeping the Default/Negotiable distinction and Rating Discovery Procedures. |
| 5 | M3 LO 3.2: broaden to "Describe how Drawdown Policies (Expiring First / Granted First / Granted Last) and Rollover Policies impact Usage Entitlement Buckets." — keeps the three named values + adds Rollover Policies per Mike. |
| 10 | M4 LO 1.4: "Analyze the automated conversion of Debit Memo Lines into Invoice Lines, driven by `NextBillingDate` on the Debit Memo record." |
| 14 | M5 LO 1.4: "Implement a Smart Retry strategy (via Payment Retry Rules and Payment Retry Rule Sets) that optimizes recovery rates by gateway error category." |
| 18 | M5 LO 2.2: hybrid wording combining concrete channels + DSO outcome. |

### Group C — Tension worth surfacing to Mike directly

| Mike's # | Tension |
|---|---|
| 11 | M5 LO 1.1: Mike's abstract reword ("Establish integrations...to enable secure payment processing") vs. our snapshot-grounded concrete ("Configure native payment gateway connections through Salesforce Payments to Stripe and Adyen"). The Trailhead AI Review Checklist generally prefers concrete; M2v2 / M3v2 / M4v2 all use concrete product names consistently. Recommend pushing back. |
| 22 | M5 LO 2.5: pre-GA "Collections Agent" naming vs. 262-shipped "Subagent: Billing Collections Management." This is the cross-cutting subagent-naming question affecting M1v2, M4v2, M5v2. |

### What stays unchanged in M5

- LO 1.2: Payment Gateway Adapter pattern — Mike didn't touch.
- LO 2.3: Manage Billing Disputes — Mike didn't touch.

### Body draft impact

Mike's comments are on the **LO doc**, not on the M3 / M4 / M5 v2 body drafts. The v2 drafts are downstream — once we settle the LOs, the body drafts need to align. Most of Mike's restructure work on M5 Unit 2 means the M5 v2 body sections will need to be reordered (Self-Service Portal section moves to the front; Collections Agent section moves to the end).

---

*Comments captured 2026-05-12 from `https://docs.google.com/document/d/1WiRfAg6uoTCLwdWBpIAzEm0p9hXguRClN1OFmv2af1s/edit`. Mike's annotations were against a version of `modules-3-4-5-proposed-los.md` predating the M3 LO validation report and M4+M5 LO validation report — his comments are best read as "intent" rather than line-by-line edits to the current repo state.*
