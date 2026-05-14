# Module 7 v2 — Validation Report

**Module:** Strategic Selling, Discovery, and Competitive Readiness
**Validated against:** 262 Summer '26 Salesforce Help portal capture (Billing area) for product-capability claims; public sources for competitive facts; PMM flag list for commercial claims.
**Date:** 2026-05-14
**Outcome:** Module 7 is largely sales methodology — personas, discovery, objection handling, ROI — which isn't groundable against the Help portal. The v2 work focused on stripping version notations, handling time-sensitive commercial claims, fixing one cross-module inconsistency, and applying the AI Review Checklist. The body content was sound and is preserved.

## What is and isn't groundable

The Help portal documents *product behavior*, not commercial terms, partner-SKU lifecycles, competitive positioning, or customer reference metrics. Module 7 is built mostly from the latter. So validation here splits three ways: product-capability claims (groundable), competitive facts (web-verifiable), and commercial claims (PMM-only).

## Product-capability claims — consistent with the snapshot

These claims in Module 7 align with capabilities already grounded in the Module 1–5 v2 work:

| Claim | Cross-reference |
|---|---|
| Avalara / Vertex pre-built tax integrations | Grounded in Module 1 v2 + Module 2 v2 (Tax Engine Adapter) |
| Billing collections automation — Get Dunning Strategy, Send Dunning Email | Grounded in Module 5 v2 (Subagent: Billing Collections Management) |
| Billing inquiries via the service agent | Grounded in Module 1 v2 + Module 4 v2 |
| Automated refund orchestration (invocable action) | Consistent with Module 5 v2 scope |
| Billing frequency changes (higher to lower on new sale orders) | Grounded in Module 1 v2 ("billing frequency changes at the BSG level") |
| Expanded payment methods — Apple Pay, Google Pay, SEPA Debit, BACS Debit, Klarna, Afterpay | Consistent with Module 5 v2 (digital wallets, BNPL, SEPA, BACS) |
| m3ter partnership for high-scale, multi-dimensional usage | Grounded in Module 3 v2 + Module 5 v2 |
| Order to Billing Schedule flow bridges sales and finance | Grounded in Modules 1 and 2 v2 |

No product-capability claim in Module 7 contradicts the snapshot.

## Competitive claim — web-verified

**Stripe's acquisition of Metronome.**
- **v1 claim:** "Metronome was acquired by Stripe in late 2025."
- **Finding:** Confirmed via public reporting. Stripe announced a definitive agreement to acquire Metronome (reported at roughly $1B); the acquisition **completed in January 2026**. "Late 2025" reflects the announcement, not the close.
- **v2 fix:** The acquisition is stated as a fact without a date stamp ("Stripe's acquisition of Metronome blurs the B2B/B2C identity further"), which is both accurate and evergreen.
- Sources: Stripe newsroom ("Stripe completes Metronome acquisition"); Payments Dive; PYMNTS.com.

## Commercial claims — flagged for PMM (cannot self-verify)

These four can't be checked against any product documentation and need PMM sign-off before publication:

1. **Conga DocGen SKU lifecycle** — v1: Conga's free CPQ/Billing DocGen SKUs are "end-of-renewal as of March 2026." v2 keeps the strategic point (treat it as a migration forcing function) but removes the hard date and adds an inline "confirm with PMM" note.
2. **Document generation and Revenue Events** — v1: "as of February 2026," document generation no longer consumes Revenue Events for Revenue Cloud Advanced or Revenue Cloud Billing. v2 keeps the substance, drops the date, flags for PMM.
3. **CPQ/CPQ+ migration to Salesforce DocGen "at $0"** — a pricing claim. Flagged for PMM.
4. **Customer reference metrics** — Lightspeed (55→3 clicks), Shiftlogic (~1 hr → 3 min), Datavant, FlexRack (54 spreadsheets / $3.66M), Genius Sports (0%→80% / 25% same-day). These read as reference-program numbers; PMM/reference team to confirm they're cleared for external Trailhead use and current.

## Other v2 changes

| v1 issue | v2 fix |
|---|---|
| "The Spring '26 release brings this to life…" — hard version notation | Removed; GA capabilities now presented without a release stamp, per the evergreen rule |
| Unit 1 callout described "Consumption Management" as the *broader* framework | **Cross-module inconsistency.** Module 3 v2 (grounded against the snapshot) establishes that **Usage Management** is the umbrella area and **Consumption Management** is the lifecycle within it. v2 aligns Module 7's callout to that framing |
| Agent names used freely ("Agentforce Collections Agent," "Agentforce Agents," etc.) | Added the agent-naming hold notice carried by Modules 1, 3, 4, 5; softened to "billing agents" in body prose pending Annie + Mike alignment |
| Grammar error in the "Billing Inquiries via Service Agent" bullet ("rep. getting instant answers") | Cleaned up |
| Suggested Unit Titles table had a blank 4th row | Trimmed to the three real units |
| Status block missing (v1 was a bare draft) | Added the standard v2 status block matching Modules 1–6 |

## Net assessment

Module 7's methodology content is solid and needed little rewriting. The risk in this module isn't product accuracy — it's the time-sensitive commercial claims and reference metrics, which are now consolidated in the module appendix and this report for PMM to clear. Ready for Mike's SME review in parallel with PMM's commercial-claims pass.
