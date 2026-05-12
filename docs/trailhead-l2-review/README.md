# Trailhead L2 — Agentforce Revenue Management Billing Review

Review artifacts for the FY27 Trailhead L2 mix on Agentforce Revenue Management Billing — five modules covering positioning, billing architecture, usage, invoicing, and payments/collections.

## Module Status

All five modules now have **v2 body drafts grounded against the complete 262 Summer '26 Help portal capture** (838 articles across 10 RC functional areas plus the cross-domain Agentforce-for-RC agent suite).

| Module | v2 Draft | Validation Report | Status |
|:--|:--|:--|:--|
| **1 — The Agentforce Revenue Management Billing Foundation** | [`module-1-v2.md`](./module-1-v2.md) | [`module-1-v2-262-validation-report.md`](./module-1-v2-262-validation-report.md) | ✓ Substantive edits applied (Agentforce subagent names, Generate Invoices, Preview Invoices, Usage Entitlement chain, Charge Frequency vs Type, Tax Adapter naming). Voice checklist re-pass + unsourced terms (High Scale Billing, m3ter, National Satellite Service) pending Mike's input. |
| **2 — Billing Technical Architecture and Data Model Deep Dive** | [`module-2-v2.md`](./module-2-v2.md) · [editorial direction](./module-2-editorial-direction.md) · [inline diff](./module-2-inline-diff.md) | [`module-2-v2-262-validation-report.md`](./module-2-v2-262-validation-report.md) | ✓ All validation pass edits + evergreen rule applied; Google Doc updated for SME comments. |
| **3 — Usage, Rating, and Consumption Agents** | [`module-3-v2.md`](./module-3-v2.md) | [`module-3-262-lo-validation-report.md`](./module-3-262-lo-validation-report.md) | ✓ New body draft grounded against Usage Management (52), Rate Management (35), and Agentforce-for-RC (13) snapshots. Wallet Management open question for Mike. |
| **4 — Invoicing and the Invoice Line Explanation Subagent** | [`module-4-v2.md`](./module-4-v2.md) | [`modules-4-5-262-lo-validation-report.md`](./modules-4-5-262-lo-validation-report.md) | ✓ New body draft. All M4 LOs validated clean. |
| **5 — Payments, Collections, and the Billing Collections Management Subagent** | [`module-5-v2.md`](./module-5-v2.md) | [`modules-4-5-262-lo-validation-report.md`](./modules-4-5-262-lo-validation-report.md) | ✓ New body draft. 4 substantive LO corrections applied (Salesforce Payments structure, Payment Retry Rules naming, Payment Batch Run naming, Collections subagent capability names). |

Recommended review order per module: validation report (findings + open questions) → v2 draft (content as it stands). For Modules 2 and 4, the editorial direction and inline diff documents (linked above where they exist) explain *why* specific framing decisions were made.

## Cross-Module Conventions

**Source verification.** All factual claims across the five v2 drafts are grounded against the 262 Summer '26 Help portal capture in `docs/salesforce/262/help/articles/` — 838 articles, 4.3 MB, covering all 9 RC data-model domains plus the cross-domain Agentforce-for-RC suite. Citation logs live in each module's validation report. The `revenue-cloud-docs` skill documents the capture pipeline and grounding workflow.

**Evergreen language rule.** Per Mike's direction: Trailhead-facing body content avoids release-version notations (260, 262, Spring '26, Summer '26). Version-specific behaviors are documented in the validation reports, not the v2 drafts. Each v2 draft carries a "Style note" line in its header making this explicit so future editors don't reintroduce version refs.

**Bolded object names.** All five v2 drafts bold product object names (Billing Policy, Tax Engine, Subagent: Consumption Management, etc.) for technical clarity. This deviates from the Trailhead AI Review Checklist's "no bold to highlight words or phrases" guidance. If editorial decides to strip the bolding, the same change applies to all five modules for consistency.

**Voice patterns applied.** AI Review Checklist patterns applied across all v2 drafts: sentence length under 27 words, no X-not-Y comparison patterns, no modals like "might/could/may" used as hedges, no "Salesforce/Agentforce actively works on your behalf" anthropomorphism, metaphors used sparingly at cold-opens and dropped from body content.

**Subagent naming.** All five v2 drafts use **Agentforce for Revenue Management** as the parent agent name across every subagent reference (Subagent: Invoice Line Explanation, Subagent: Billing Inquiries, Subagent: Billing Collections Management, Subagent: Consumption Management). Pending Mike's confirmation per the open question in the M4+M5 validation report.

## Cross-Module Open Questions for Mike

These items are tracked across the individual validation reports. Consolidated for quick reference:

1. **Parent agent name consistency** (M4+M5 validation report Open Question 1). All v2 drafts currently use "Agentforce for Revenue Management" as the parent for every subagent. Confirm or revert.
2. **"Smart Retry" branding** (M4+M5 validation report Open Question 2). M5 v2 uses "Payment Retry Rules" (the 262 product name). If marketing wants Smart Retry as a seller-facing brand, dual-name pattern is easy to apply.
3. **Wallet Management as a standalone M3 LO** (M3 validation report). Currently folded under Unit 3 LO 3.3. Could be split out as LO 3.4.
4. **Module 1 v2 unsourced terms** (M1 v2 validation report Section 10). "High Scale Billing," "m3ter," "National Satellite Service" appear in M1 v2 but have 0 hits in the captured 262 Help. Mike's source-of-truth or drop.
5. **Module 1 v2 Order to Billing Schedule flow detail** (M1 v2 validation report). Clone-and-customize specifics aren't in the captured 262 Help. Mike to confirm whether to re-source or accept the 260-grounded content.

## Open Scoping Items for the L2 Mix

Topics that were in v1 module drafts but have no current home in the v2 module set. Need a scoping decision from Mike + the L2 authoring team before any of them get a v2 home:

- The "Big Four Flows" framing — Mike's hint suggests a different setup story involving the context service and the Order to Billing Schedule flow.
- DRO Settings — Mike: not part of billing; likely belongs in an Order Lifecycle / Fulfillment module if and when one exists.
- Pricing Setup — Mike: not billing related; belongs in a Pricing module.
- Multi-currency and Localization as a standalone topic — tangentially relevant to M2 v2 tax addresses but not called for as its own topic.
- ERP Integration / System of Execution / PLG-vs-Enterprise Bifurcation Pattern — strategic / positioning content. None of M1–M5 cover it.
- Standalone Billing APIs as a "headless commerce" topic — M2 v2 covers Standalone Billing Schedules thoroughly; the headless-commerce framing of the API surface itself is not in M1–M5.

## What's Next

- **Mike's review pass** on all five v2 drafts and the four validation reports. Open questions captured per module.
- **AI Review Checklist re-pass** on the new M1/M3/M4/M5 v2 prose after Mike's substantive edits land.
- Body-content additions for **M3** (Wallet Management LO call, Anchor/Pack/Commitment/Token Commitment product patterns from the Usage snapshot) pending Mike's go-ahead.

---

*Maintained by Brian Galdino with AI assistance.*
