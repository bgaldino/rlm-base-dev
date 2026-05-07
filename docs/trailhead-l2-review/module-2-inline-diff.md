# Module 2 — Inline Diff (v1 → v2)

**Purpose:** Map every section of the current Module 2 draft to a verdict (REMOVE/PARK, REWRITE, FIX, or KEEP) and a brief reason. Each entry is keyed by section header so reviewers can locate the passage in the v1 Google Doc.

**Companion documents:**
- [`module-2-editorial-direction.md`](./module-2-editorial-direction.md) — pattern-level summary of the rewrite direction
- [`module-2-v2.md`](./module-2-v2.md) — the rewritten module

---

## Front matter

| v1 element | Verdict | Reason |
|:--|:--|:--|
| Badge title | KEEP | "Billing Technical Architecture and Data Model Deep Dive" still works |
| Badge description | KEEP | "Configure core billing architecture and data models to power your revenue engine" — fine as-is |
| Suggested Unit Titles ("Learn the Core Configuration Essentials" / "Dive into Advanced Platform Capabilities") | REWRITE | Too vague. v2: "Configure the Billing Policy, Tax Policy, and Milestone Plans" / "Manage Standalone Billing Schedules, External Billers, and the Invoice Scheduler" — imperative + concrete |
| AI Usage / Suggested Category | KEEP | No changes |

---

## Unit 1 — section-by-section

### Unit 1 Learning Objectives (current 5 LOs)

REWRITE — replace with Mike's 4 LOs from the FY27 outline. The current draft's LOs (Setup Trifecta / Order-to-BS flow / UEA + m3ter / Hybrid Models / Milestone+Dunning) don't survive the LO change.

### Opening narrative ("mise en place")

KEEP with cuts. The kitchen metaphor is a fine cold-open but is currently overused — by the end of the unit, every section reaches for a kitchen analog. Module 1 v2's discipline: pick one metaphor, use it once for the cold-open, then drop it.

### "In the era of the Agentic Enterprise, your billing configuration is your mise en place..."

REMOVE. The phrase "Agentforce actively works on your behalf to execute revenue workflows" is exactly what Module 1 v2 cut. Replace with a literal sentence about why a clean configuration matters.

### "Use Slackbot to Personalize Your Learning" callout

KEEP. Useful sidebar; matches the Module 1 v2 pattern of one callout per section.

### "The Setup Trifecta" (Revenue Settings + DRO Settings + Pricing Setup)

PARK the entire framing. Mike: "DRO is not part of billing and it does not setup the billing objects." Mike (separately): "These are not billing related." The Trifecta is a lift that doesn't belong in a billing module. v2 replaces it with the Billing Settings configuration node only.

### "Revenue Settings: The Revenue Logic Hierarchy" (Billing Policy / Treatment / Treatment Item)

REWRITE. The hierarchy is correct as a teaching object, but two factual errors must be fixed and the parent node name must change.

- FIX: "This hierarchy is configured under Revenue Settings—the main brain of the platform." → Configured under **Billing Settings** (verified against Help docs, p. 1069).
- FIX: "Billing Treatment Item: This is the Line Cook. It handles the most granular details, such as applying a specific tax rate or GL code to a single line item." → Mike: "This is incorrect. Tax is handled in the tax policy. GL is in the GL Assignment Rules." v2 replaces with: BTI defines how the order item's total amount is distributed into billing schedules across the order item's lifecycle. Real fields: Status, Processing Order, Billing Type, Controller, Zero Amount Behavior, Type, Percentage, Flat Amount, Sequencing — plus milestone-specific fields when enabled.
- FIX: Diagram callout "[Alt text: Revenue logic hierarchy displayed.]" — Mike: "This diagram is wrong, see comments above." v2 omits the diagram until corrected and renamed to "Billing Policy hierarchy."
- ADD in v2: The activation sequence (draft policies → draft treatments → draft items → activate items → activate treatments → activate policies). The three Treatment Selection modes (Default, Manual, Legal Entity).

### "DRO Settings: Prepping the Ingredients"

PARK. Mike: "DRO is not part of billing and it does not setup the billing objects." Drop entirely; not in Module 2 v2.

### "Pricing Setup: The Menu and Costs"

PARK. Mike: "These are not billing related." Drop entirely; not in Module 2 v2.

### "Activate the Order to Billing Schedule Flow"

REWRITE. Mike: "This is wrong. You clone it because we allow you to customize it. Once you make a copy it runs by itself."

- FIX: Drop the "deliberate quality gate" framing.
- FIX: Drop the "PLG and enterprise-led sales motions" hook (belongs in the parked ERP/Bifurcation discussion).
- ADD in v2: Best practice from Help docs — include "Custom" in the cloned flow's name. Note that two flows fire in parallel on Order activation (Order to Billing Schedule + Order to Asset). Order activation prerequisites with Billing on: Bill to Contact, Billing Address, Shipping Address.

### "Manage the Usage Rating Engine" (UEA, Buckets, Digital Wallets, m3ter)

PARK to Module 3 (already covered there). Drop from Module 2.

### "Define Hybrid Models and Legal Entity Differentiation"

PARK. Mike: "This does not make sense." Hybrid Models material is in Module 3; Legal Entity material is folded into the v2 Billing Treatment section.

### "Protect Cash Flow with Milestones and Dunning"

REWRITE / SPLIT. Mike: "These are two very different concepts and should not be merged."

- v2 keeps a Milestone Plans section in Unit 1 (LO 1.4). Object names corrected to **Billing Milestone Plan** and **Billing Milestone Plan Items** (with the "Billing" prefix). Two creation paths confirmed: auto-generated from a milestone-enabled Billing Treatment, or manually created at the Order Product. Cancellation behavior added (invoiced milestones stay; uninvoiced event-based items go to Canceled; credit memo for the difference).
- Dunning Workflows go to Module 5 (already covered there). Drop from Module 2.

### NEW SECTIONS in v2 Unit 1

- **"Configure the Tax Policy and Its Related Objects"** — covers Tax Policy → Tax Treatment → Tax Treatment Item, plus Tax Engine and Tax Engine Provider. Notes that Tax Code is a field (not an object) and TaxEngineAdapter is an Apex interface (not a record). Maps to Mike's LO 1.2.
- **"Map How the Revenue Standard Tax Engine Drives Taxation"** — replaces the v1's missing LO 1.3 section. Covers the **Revenue Standard Tax Engine** + **Revenue Standard Tax Entries** decision table as the OOTB tax pipeline; clarifies that Tax Rates themselves are admin-created, not preconfigured by Salesforce; flags that the decision table must be refreshed every time a Tax Rate changes. Maps to Mike's LO 1.3.

### Unit 1 Quiz

REWRITE. Both v1 questions test parked content (UEA Digital Wallet, Hybrid Models). v2 quiz tests Billing Policy hierarchy and Tax Policy / Tax Engine.

---

## Unit 2 — section-by-section

### Unit 2 Learning Objectives (current 4 LOs)

REWRITE — replace with Mike's 3 LOs. The current draft's LOs (Standalone Billing APIs as headless commerce / Big Four Flows / Tax Engine Adapters vs. ERP / System of Execution + Bifurcation) don't survive the LO change.

### "Connect with Advanced Platform Capabilities" / "Master Headless Billing with Standalone APIs"

PARK. The v1 framing is about *headless commerce APIs*, but Mike's LO 2.1 is about **Standalone Billing Schedules** — the schedule object created without a parent Order. These are related but different topics.

- v2 replaces with "Create and Amend Standalone Billing Schedules" — focused on the Create Standalone Billing Schedules API and StandaloneBillingContext context definition.
- The headless-commerce framing of the API surface as its own topic is parked; not in Modules 1–5.

### "Pre-requisite: The Big Four Flows"

PARK. Mike: "Same comments as above. If you want to talk about how billing gets setup cover the context service and the flow that runs." The Big Four Flows framing isn't in the Help docs and Mike points at a different setup story (likely BillingContext / StandaloneBillingContext + Order to Billing Schedule flow). v2 omits the framing; the more accurate setup story is woven into the Standalone Billing Schedules section.

### "Scale Globally: Multi-Currency, Localization, and Tax Engine Adapters"

PARK. Multi-currency / localization isn't in Mike's LOs for Module 2. Tax Engine Adapters are folded into the v2 Tax Policy section (Unit 1 LO 1.2) where they belong (Revenue Cloud Tax Extension type → TaxEngineAdapter Apex interface).

### "Integrate with Downstream ERPs" + "The Bifurcation Pattern (PLG vs. Enterprise)"

PARK both. System-of-Execution and Bifurcation aren't called for by the new LOs. Not in Modules 1–5; need a scoping decision before they get a home.

### NEW SECTIONS in v2 Unit 2

- **"Create and Amend Standalone Billing Schedules"** — defines them as Billing Schedule records produced via the Create Standalone Billing Schedules API + StandaloneBillingContext. Three use cases: migration cutover, external-system origination, one-off bills. Notes that the same API serves Order-derived flows when invoked with BillingContext. Maps to Mike's LO 2.1.
- **"How Revenue Cloud Billing Works with External Billers"** — catalog of supported integration patterns: Standalone Billing Schedules API, sObject APIs, Invoice Ingestion API, Import External Tax Lines (CSV), TaxEngineAdapter Apex interface, Suspend/Resume Billing APIs, Custom intracontext mapping. Notes that the Help docs use "external systems" rather than "external biller." Maps to Mike's LO 2.2.
- **"Configure the Invoice Scheduler"** — renames "Bill Run" to **Invoice Scheduler** (the Help docs term). Real settings list: Active toggle / Start Date / Time Zone / End Date / Post invoices toggle / Frequency / Exclude holidays and weekends (Monthly only — *already in 260, not a 262 enhancement*) / Target Date + Offset / Invoice Date + Offset / Filter criteria (billing batch, charge type, legal entity, customer account, currency). Email delivery is *not* a scheduler setting (separate Send Invoices Through Email feature). Adds platform limits: max 30 active Billing Batch Schedulers, max 2,000 invoice lines per invoice. Maps to Mike's LO 2.3.

### Unit 2 Quiz

REWRITE. Both v1 questions test parked content (Big Four Flows, PLG/Enterprise Bifurcation). v2 quiz tests Standalone Billing Schedules and Invoice Scheduler filter criteria.

---

## Resources

REWRITE. v1 Resources are placeholders ("[Trailhead] Billing Management with Revenue Cloud — Internal login required" and bare "[Salesforce Help]" links without article IDs). v2 cites real Help articles with verified IDs:

- `ind.billing.htm` — Manage Billing in Revenue Cloud
- `ind.billing_payment_terms.htm` — Define Billing Policies and Billability Rules
- `ind.billing_milestone.htm` — Configure Milestone Billing
- `ind.billing_invoice_run.htm` — Generate Invoices in Revenue Cloud
- `ind.billing_migrate_external.htm` — Migrate External Billing Data

---

## Summary statistics

| Category | Count |
|:--|:--|
| Sections KEPT | 1 (Slackbot callout) |
| Sections REWRITTEN with corrections | 4 |
| Sections PARKED (routed elsewhere or to scoping) | 7 |
| NEW sections added in v2 | 5 |
| Specific factual fixes | 7 |

---

*Prepared by Brian Galdino with AI assistance, May 7, 2026.*
