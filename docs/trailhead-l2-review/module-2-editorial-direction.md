# Module 2 — Editorial Direction Summary

**Purpose:** Explain *why* the v2 rewrite is structurally different from the current draft, so reviewers can evaluate the direction before evaluating the prose.

**Companion documents:**
- [`module-2-inline-diff.md`](./module-2-inline-diff.md) — passage-by-passage changes from v1 to v2
- [`module-2-v2.md`](./module-2-v2.md) — the rewritten module

---

## Headline finding

The current Module 2 draft is largely off-topic relative to what the FY27 outline now says it should cover. Mike Aaron's revised LO column (the right-most column of the V2 Billing L2 Outline tab) re-scoped Module 2 between when the draft was written and now, and Mike's 11 inline comments on the draft confirm the same drift at the paragraph level. This isn't a voice/style edit like Module 1's was — Module 2 needs a structural rewrite around Mike's new LOs.

## What Mike's revised LOs say Module 2 should cover

Verbatim from the FY27 spreadsheet, "Mike's Revised LOs" column, row 4:

**Unit 1**
- 1.1 Describe the key objects and their purposes in the Billing Policy.
- 1.2 Explain the function of the Tax Policy and its related objects.
- 1.3 Map how the onboard Tax Rates are used to drive taxation.
- 1.4 Describe the strategy for customizing and editing Milestone Plans.

**Unit 2**
- 2.1 Understand the system's ability to Create and Amend Standalone Billing Schedules.
- 2.2 Explain how RCB works with external billers.
- 2.3 Configure the Bill Run and understand how its settings control the outcomes it produces.

## What the current draft covers instead

**Unit 1** frames a "Setup Trifecta" of Revenue Settings + DRO Settings + Pricing Setup, then drills into a Billing Policy → Treatment → Treatment Item hierarchy with a Kitchen Manager / Station Chef / Line Cook metaphor, Order-to-Billing-Schedule flow activation, Usage Entitlement Account + m3ter, and a Hybrid Models section.

**Unit 2** covers Standalone Billing APIs, the "Big Four Flows," Tax Engine Adapters, ERP integration, and the PLG/Enterprise Bifurcation Pattern.

None of those topics is wrong per se — most belong somewhere in the L2 mix — but they're not what the LOs ask Module 2 to teach.

## What Mike said in the comments, organized by issue

**Factual errors**

- Billing Treatment Item is described as "applying a specific tax rate or GL code" — Mike: "Tax is handled in the tax policy. GL is in the GL Assignment Rules." Verified against the Spring '26 Help compendium: BTI controls how the order item's total is distributed across billing schedules; tax and GL are not BTI fields.
- The Order-to-Billing-Schedule flow is framed as a "deliberate quality gate" — Mike: "You clone it because we allow you to customize it. Once you make a copy it runs by itself." Verified against the Help docs.
- One section's diagram is flagged "This diagram is wrong, see comments above."
- Header word "Revenue" should be "Billing" in at least one place. Verified: parent settings node is **Billing Settings**, not Revenue Settings.

**Scoping errors**

- DRO Settings flagged twice: "DRO is not part of billing and it does not setup the billing objects" and "These are not billing related."
- Pricing Setup: "These are not billing related."
- Milestone Billing and Dunning are merged: "These are two very different concepts and should not be merged."
- Define Hybrid Models section: "This does not make sense."
- Big Four Flows section: "This is wrong" and "Same comments as above. If you want to talk about how billing gets setup cover the context service and the flow that runs."
- Two Order-flow sections: "I dont understand" and "This is wrong" respectively.

## What this means for the rewrite

Treating the LO drift and Mike's comments together, Module 2 needs to be re-framed around the Billing Policy / Tax Policy / Tax Engine / Milestone Plans / Standalone Billing Schedules / external systems / Invoice Scheduler sequence. Specifically:

**Drop or relocate**

- The "Setup Trifecta" framing (DRO and Pricing Setup don't belong in a billing module).
- The Big Four Flows section (Mike: wrong; needs a different setup story involving the context service).
- The multi-currency / localization narrative (not in Mike's LOs).
- The ERP / PLG-vs-Enterprise / Bifurcation Pattern section (System-of-Execution topics that fit a different module).
- The Hybrid Models section as currently written.
- The Milestone+Dunning merged section.

**Add or refocus**

- A clean Unit 1 on the Billing Policy hierarchy as a configuration object — corrected so Tax lives in the Tax Policy chain and GL lives in the GL Assignment Rules.
- A Tax Policy section covering Tax Treatment, Tax Treatment Item, Tax Engine, and Tax Engine Provider.
- A section on the Revenue Standard Tax Engine and its Revenue Standard Tax Entries decision table — *this is the correct interpretation of Mike's "onboard Tax Rates" LO*. Tax Rates themselves are admin-created; the "onboard" piece is the engine and decision table.
- A Milestone Plans section covering customization (separate from Dunning), with object names corrected to **Billing Milestone Plan** and **Billing Milestone Plan Items**.
- A Unit 2 built around Standalone Billing Schedule create/amend (via the Create Standalone Billing Schedules API + StandaloneBillingContext), the external systems integration story, and Invoice Scheduler configuration.

**Keep with corrections**

- Order-to-Billing-Schedule flow activation, but reframe as "you clone it for customization; the copy runs by itself." Drop the quality-gate framing.
- The Slackbot "Make It Your Own" callout (it's a small, useful sidebar that matches the Module 1 v2 pattern).

**Park to other modules (already covered)**

- UEA / Buckets / Digital Wallet / m3ter / Hybrid Models / Mediation → Module 3.
- Dunning, Collections agent → Module 5.
- Milestone billing as an invoicing pattern → Module 4 (Module 2 covers customization; Module 4 covers application).

## Voice direction

Mirror Module 1 v2:

- Imperative-verb unit titles with concrete nouns ("Configure the Billing Policy, Tax Policy, and Milestone Plans"), not vague ones ("Learn the Core Configuration Essentials").
- Concrete object names lead the explanations; metaphors are minimal and used once for the cold-open, then dropped.
- Avoid the phrase "Salesforce / Agentforce actively works on your behalf" — Module 1 v2 cut this throughout.
- Seller Sidebars are sparse and named pivots, not generic encouragement.
- Quizzes test recall of specific objects/concepts, not abstract themes.

## Source-of-truth verification

Beyond Mike's revised LOs and inline comments, the v2 draft was verified against the Spring '26 Help compendium (`docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf`, 1,460 pages, focused on pp. 1069–1247 for Billing topics). Specific findings drove the following corrections:

- "Bill Run" → **Invoice Scheduler** (Help docs term).
- Tax Policy related-objects list updated to: Tax Treatment, Tax Treatment Item, Tax Engine, Tax Engine Provider. Tax Code is a *field*, not an object; "Tax Policy Item" doesn't exist; TaxEngineAdapter is an Apex interface.
- "Onboard Tax Rates" reframed to mean the **Revenue Standard Tax Engine** + **Revenue Standard Tax Entries** decision table (Tax Rates themselves are admin-created).
- "Standalone Billing Schedules" reworded to "Billing Schedule records produced via the Create Standalone Billing Schedules API" — the "Standalone" qualifier attaches to the API, not a separate object.
- Invoice Scheduler settings list corrected and a few platform limits added (max 30 active schedulers, max 2,000 invoice lines per invoice).
- "Exclude holidays and weekends" confirmed as already-in-260, Monthly-frequency only — *not* a 262 enhancement.
- Milestone object names corrected to **Billing Milestone Plan** and **Billing Milestone Plan Items** (with the "Billing" prefix).

---

*Prepared by Brian Galdino with AI assistance, May 7, 2026.*
