# Trailhead L2 — Agentforce Revenue Management Billing Review

Review artifacts for the FY27 Trailhead L2 mix on Agentforce Revenue Management Billing.

## Module 2 — v2 Review (May 2026)

| Document | Purpose |
|:--|:--|
| [`module-2-editorial-direction.md`](./module-2-editorial-direction.md) | Pattern-level summary of *why* Module 2 needs a structural rewrite |
| [`module-2-inline-diff.md`](./module-2-inline-diff.md) | Section-by-section diff from the v1 draft to the v2 |
| [`module-2-v2.md`](./module-2-v2.md) | Full rewritten Module 2 ready for Mike's review |

**Recommended review order:** editorial direction → inline diff → v2 draft. The editorial direction explains the framing decisions; the inline diff shows how those decisions translate to specific passage-level changes; the v2 draft is the final product.

**Source verification:** All factual claims in the v2 draft are verified against the Spring '26 Help compendium (`docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf`, 1,460 pages, focused on pp. 1069–1247 for Billing topics) and Mike Aaron's revised LOs in the FY27 outline spreadsheet.

**Style verification:** The v2 has been passed through the Trailhead AI Review Checklist (sentence length, comparison patterns, modals, generic phrases, audience voice). One deliberate deviation: the v2 bolds product object names for technical clarity, matching Module 1 v2's convention across the L2 mix. If editorial decides to strip the bolding, the same change applies to all five modules for consistency.

## Open scoping items for the L2 mix

These topics were in the v1 Module 2 draft, are not covered by Modules 1–5 in the current L2 mix, and need a scoping decision before they get a home:

- The "Big Four Flows" framing (Mike's hint suggests a different setup story involving the context service and the flow that runs)
- DRO Settings (Mike: not part of billing — likely belongs in an Order Lifecycle / Fulfillment module)
- Pricing Setup (Mike: not billing related — likely belongs in a Pricing module)
- Multi-currency and Localization as a standalone topic
- ERP Integration / System of Execution / PLG-vs-Enterprise Bifurcation Pattern
- Standalone Billing APIs as a "headless commerce" topic (the API as a topic in itself, separate from its ingestion use case in Module 2 v2)

## Cross-module observations

The same v1 voice patterns Module 1 v2 corrected ("Salesforce / Agentforce actively works on your behalf," metaphor saturation, soft-on-object-names) are present in the v1 drafts of Modules 3, 4, and 5. They will need the same review pass once Module 2 is settled. Module 4's Resources section is also still placeholder text from the Trailhead template.

---

*Maintained by Brian Galdino with AI assistance.*
