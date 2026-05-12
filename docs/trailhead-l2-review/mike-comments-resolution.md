# Mike's Responses on the LO Comment-Resolution Discussion

**Date captured:** 2026-05-12
**Source:** Mike's comments on `mike-comments-on-modules-3-4-5-los.md` (Google Docs ID `19KU5T7S33nfryKg1pEn-hmdnTEeSkRRb9ZstiCVzpQs`) — a meta-discussion where Mike replied to the proposed action plan rather than to the LOs themselves.
**Captured comments:** 16

## Style direction established

Mike's comments establish two cross-cutting style rules for LOs going forward:

1. **LO titles stay high-level and seller-facing.** Object names, field names, and specific product terminology go in the body content, not in the LO statements. ("LOs should be more high level and the specifics should be in the content details" / "keep these LO titles more seller-facing and the object/field names can be referenced as details in the content.")
2. **Vary the verbs.** "Describe" is overused in our LO list — Mike wants stronger or more varied verbs (Implement, Set Up, Configure, Map, Apply, Analyze, etc.).

These rules change the shape of the LO doc significantly. Many of my LOs currently lead with concrete object names (BillingArrangement, PaymentGatewayProvider, etc.) and use "Describe." Per Mike's direction, those move to the body and the LO statements get reworded.

## Decisions Mike made

| Topic | Mike's call |
|---|---|
| **M3 LO 2.4 (mediation note)** | Drop entirely — "We dont need a specific LO on us not doing something, remove it." (Body-callout question still open — see below.) |
| **M4 LO 1.4 (NextBillingDate detail)** | OK to keep the NextBillingDate connector in the LO. "OK, on the leaving the NextBillingDate." |
| **M5 LO 1.1 (gateway config scope)** | Use Mike's abstract wording. His reasoning: gateway config isn't just for natively supported gateways — it covers both native AND third-party. The current concrete wording is technically wrong at the LO level. **Mike's wording wins on this one.** |
| **"Payment Run" vs "Payment Batch Run"** | Use "Payment Run" globally. Drop the dual-name pattern (no more "Payment Run (formal: Payment Batch Run)"). Object/field names go in body content. |
| **"Smart Retry" vs "Payment Retry"** | **Reversal from his prior comment.** Mike now says: "Use Payment Retry." Drop "Smart Retry." The LO uses "Payment Retry"; the body content can reference the specific products (Payment Retry Rules, Payment Retry Rule Sets) as configuration details. |

## Items still open for Mike

| Topic | Status | What's blocking |
|---|---|---|
| **Mediation body callout in M3 v2** | ⏳ Mike answered "remove the LO" but didn't yet answer the follow-up: should the body-content paragraph in M3 v2 Unit 2 ("Mediation is Customer-Side") also be removed? | Awaiting Mike's reply to the follow-up comment. |
| **Agent naming — Billing Agent vs Subagent** | ⏳ Mike said "Lets use 'Billing Agent' universally." Brian pushed back: "this is something we should talk to annie about. The new agentforce materials want us to use subagent names and refer to an orchestrated agent as a superagent." | Brian to confirm with Annie which naming pattern is canonical for the L2 mix. |

## Brian's note in the discussion thread

Brian replied in two places agreeing with Mike's high-level direction:

- "i agree - the LOs should be more high level and the specifics should be in the content details."
- "it's keeping analyze change you made, just expanding down to the NextBillingDate specific callout for the concrete connector."

These ratify Mike's style direction. The implementation: rewrite LOs to be shorter, verb-led, seller-facing, with concrete product/object/field names dropped into the body content.

---

## Refined LO rewrite plan

Applying Mike's two style rules + his specific calls, here's the rewrite for each affected LO. Items in **bold** are object/field names that move from LO into body content.

### Module 3

- **LO 2.3** (rating procedures) — current LO leads with "Rating Procedures (Default Rating Procedure or Negotiable Rating Procedure ... ) and Rating Discovery Procedures" — that's body-content detail. Rewrite to higher-level: **"Map how rating procedures consume usage data and rate context to produce billable summaries."** Body content names the procedures, the metadata implementation, and the Discovery vs. core distinction.
- **LO 2.4** (mediation) — **DROP.** Per Mike.
- **LO 3.2** (Drawdown + Rollover) — broaden but keep verb-led and high-level: **"Apply Drawdown Policies and Rollover Policies to govern how usage entitlement buckets are consumed and renewed."** Body content names the three Drawdown Order values (Expiring First / Granted First / Granted Last) and the bucket-renewal mechanics.

### Module 4

- **LO 1.1** — current "Configure Billing Arrangements (`BillingArrangement` and `BillingArrangementLine`) to allocate invoice amounts..." rewrites to: **"Configure billing arrangements to allocate invoice amounts across multiple billing accounts."** Object names move to body content.
- **LO 1.2** — current "Describe the role of Bill Cycle Day (`BillDayOfMonth`) and Next Billing Date (`NextBillingDate`)..." rewrites to: **"Identify the cadence fields that drive when the bill run picks up a billing schedule."** (Avoid "Describe.") Body content names the specific fields.
- **LO 1.3** — Mike's tighten already applied: **"Map how the bill run produces invoices from ready-to-bill billing schedules."**
- **LO 1.4** — Mike's "Analyze" rewrite already applied: **"Analyze the automated conversion of Debit Memo Lines into Invoice Lines, driven by NextBillingDate."** Mike said OK to keep NextBillingDate.
- **LO 2.1** — current "Configure the invoice delivery flow: the Invoice Scheduler creates the invoice data, the Document Generation Service (DocGen) renders the PDF, and Send Invoices Through Email delivers..." rewrites to: **"Configure the invoice delivery flow from scheduled generation through document rendering to customer email."** Body content names the three features.
- **LO 2.2** — current "Describe how Credit Memo Lines are auto-created from negative Invoice Lines (via the 'Convert Negative Invoice Lines to Credit Memo Lines' feature...)" rewrites to: **"Apply the automatic conversion of negative invoice lines into credit memo lines, and the application of credits to outstanding invoices."** (Avoid "Describe.") Body content names the feature.
- **LO 2.3** — current "Describe the Self-Service Portal as a customer-facing surface..." rewrites to: **"Position the Self-Service Billing Portal as the customer-facing surface for viewing invoices."**
- **LO 2.4** — current "Explain how the Invoice Line Explanation Agent provides..." holds the LO at a higher level: **"Apply the Invoice Line Explanation capability to give customers plain-language breakdowns of complex charges."** (Note: "Billing Agent" vs "Subagent" naming pending Annie's input — currently using a neutral phrase.)

### Module 5

- **LO 1.1** — apply Mike's wording: **"Establish integrations between the billing system and payment gateways to enable secure payment processing."**
- **LO 1.2** — current Payment Gateway Adapter pattern LO is fine as-is at the verb level, but the object names move to body: **"Extend payment processing to third-party gateways through a payment gateway adapter pattern."**
- **LO 1.3** — apply Mike's wording: **"Set up Payment Runs to sweep posted invoices automatically against connected gateways."** (Drop the Payment Batch Run dual-name in the LO; body content cites it.)
- **LO 1.4** — apply Mike's intent with "Payment Retry" naming: **"Implement a Payment Retry strategy that optimizes recovery rates by gateway error category."**
- **LO 2.1** — apply Mike's restructure: **"Set up the Self-Service Portal's payment surface for customer-managed payment and updates."** (Pay Now Link, payment method updates, one-time payments go in body content.)
- **LO 2.2** — apply Mike's reword with hybrid: **"Execute automated Dunning workflows that reduce Days Sales Outstanding (DSO) by deploying tiered communications across multiple channels."**
- **LO 2.3** — Manage Billing Disputes (no change).
- **LO 2.4** — DSO articulation, renumbered from 2.5.
- **LO 2.5** — apply Mike's restructure (Collections Agent at 2.5). Wording pending agent-naming resolution with Annie.

### Cross-module agent naming — pending Annie's input

Currently the body drafts use "Subagent: Invoice Line Explanation," "Subagent: Billing Collections Management," etc., per the 262 Help portal naming. Mike wants "Billing Agent" universally. New Agentforce materials apparently use subagent + superagent vocabulary. Three possibilities depending on Annie's call:

1. **Subagent naming** (current state). Use "Subagent: Billing Collections Management" / "Subagent: Invoice Line Explanation" / etc. Matches 262 Help portal exactly. May not match new Agentforce branding.
2. **Billing Agent naming** (Mike's preference). Use "Billing Agent" as the umbrella name and avoid subagent vocabulary. Simpler for sellers. May not match Agentforce-area documentation.
3. **Hybrid** — use seller-facing name in LOs, formal subagent name in body content with first-mention parenthetical.

The body drafts (M1v2, M4v2, M5v2) and the M3 v2 draft all reference the Agentforce for Revenue Management suite and named subagents. Whatever Annie decides will need to propagate to all four module v2 drafts. Recommend pausing further LO-doc edits on the agent terminology until Annie's input is in.

---

## Proposed action plan

1. **Apply the structural M5 changes and M3 LO 2.4 drop now** (Group A from the prior doc) — no naming-tension blockers.
2. **Apply the Mike-direction rewrites** (Group B) to all affected LOs per the rewrite table above — uses Mike's "Payment Run / Payment Retry" preferences, keeps "Billing Agent" framing as a placeholder until Annie weighs in.
3. **Hold the agent-naming rewrite** until Annie's input. Add a clear note at the top of the LO doc flagging "Agent naming pending Annie" so it's visible to the next reviewer.
4. **Brian asks Mike for the mediation body-callout call** — keep the paragraph in M3 v2 Unit 2 or remove it entirely?
5. **Body drafts unchanged for now.** Once LOs settle, do a downstream pass on M1v2, M3v2, M4v2, M5v2 to align verb usage, drop object names from headings into body, and apply the chosen agent terminology.

---

*Mike's responses captured 2026-05-12 from `https://docs.google.com/document/d/19KU5T7S33nfryKg1pEn-hmdnTEeSkRRb9ZstiCVzpQs/edit`. The discussion thread spans Mike's annotations on the comment-response document and Brian's follow-up questions back to him; two items remain open pending Mike's reply (mediation body callout) and Annie's input (agent naming).*
