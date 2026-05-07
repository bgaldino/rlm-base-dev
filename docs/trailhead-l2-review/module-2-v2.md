# Module 2: Billing Technical Architecture and Data Model Deep Dive

**Status:** v2 draft for SME review (Trailhead AI Review Checklist applied)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team
**Source verifications:** Spring '26 Help compendium (`docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf`, pp. 1069–1247) and FY27 outline (Mike's Revised LOs column)
**Style notes for editorial:** This draft bolds product object names (Billing Policy, Tax Engine, etc.) for technical clarity. That deviates from the AI Review Checklist's "no bold to highlight words or phrases" guidance, but matches the convention established in Module 1 v2 across the L2 mix. If editorial decides to strip the bolding, the same change should be applied to Modules 1, 3, 4, and 5 for consistency.

---

**Badge Description:** Configure core billing architecture and data models to power your revenue engine.

## Suggested Unit Titles

| # | Name | Type | Word Count *(editors fill this out)* |
|:--|:--|:--|:--|
| 1 | Configure the Billing Policy, Tax Policy, and Milestone Plans | Quiz | |
| 2 | Manage Standalone Billing Schedules, External Billers, and the Invoice Scheduler | Quiz | |

## AI Usage

Did you use AI to help you write this badge content?

- [x] Yes
- [ ] No

If yes, what AI tool did you use? Gemini and Slackbot + TH Writer Gem and TH PMM Grader Gem

## Suggested Category

- **Role**: Sales Professional
- **Level**: Intermediate
- **Trailhead Products/Features**: Agentforce Revenue Management
- **Industry**: None
- **[For internal use only: Primary Product/Feature**: Agentforce Revenue Management **]**

## Supporting Documents

- [ARM Billing L2 Outline Proposal — FY27](https://docs.google.com/spreadsheets/d/1rEKPXnNWZ-X_OC5PD9XSeMnBONZsY8NnLiaQF3RAmR8/edit?gid=670679088#gid=670679088)

---

# Unit 1: Configure the Billing Policy, Tax Policy, and Milestone Plans

## Learning Objectives

After completing this unit, you'll be able to:

- Describe the key objects and their purposes in the Billing Policy.
- Explain the function of the Tax Policy and its related objects.
- Map how the Revenue Standard Tax Engine drives taxation.
- Describe the strategy for customizing and editing Milestone Plans.

In Module 1, you saw how Billing completes the Lead-to-Cash journey. You also met the headline objects in the data model: Order, Billing Schedule Group, Billing Schedule, and Invoice. Module 2 goes one layer deeper into the configuration objects that govern how those billing records behave. The **Billing Policy** decides when to invoice. The **Tax Policy** decides how each line is taxed. The **Milestone Plan** decides when a service-based charge can fire.

Together these three surfaces decide whether a Billing Schedule produces a clean, audit-ready Invoice or a manual cleanup ticket every time it runs.

| Note | Content |
|:-:|:-:|
| icon=true | **What's in a Name?** Throughout this module you'll see two configuration nodes that sound similar. **Billing Settings** (Setup → Quick Find → Billing → Billing Settings) is where the Billing Policy hierarchy and related billing-level configuration live. **Revenue Settings** is a separate area for revenue recognition. Don't confuse them. |

## Configure the Billing Policy

The Billing Policy is the top-level object in a three-tier hierarchy that governs how a product's charges turn into invoices. The hierarchy is:

- **Billing Policy** — the parent object. It sets the high-level rules for a category of products: when to invoice (advance vs. arrears), the billing frequency default, and the proration treatment.
- **Billing Treatment** — a child of the Billing Policy, scoped to a Legal Entity. The Billing Treatment is what makes the same Billing Policy behave differently for, say, your US entity versus your Canada entity, even though both inherit the same parent rules. A Billing Treatment also drives whether milestone billing is enabled for the products that use it.
- **Billing Treatment Item** — a child of the Billing Treatment, scoped to an individual charge. The Billing Treatment Item defines *how the order item's total amount is distributed into billing schedules across the order item's lifecycle*. Each treatment must have exactly one active Billing Treatment Item that covers 100% of the order item's value.

Why three tiers instead of one? Because real businesses run on a default, a regional variant, and a per-charge exception. Each tier of the hierarchy lets you express one of those without cloning the others.

The Billing Treatment Item exposes fields like Status, Processing Order, Billing Type (Advance / Arrears / None), Controller, Zero Amount Behavior, Type, Percentage, Flat Amount, and Sequencing. When milestone billing is enabled on the parent Treatment, the Item also exposes milestone-specific fields like Milestone Type, Commencement Trigger, Offset, and Offset Unit.

The Billing Treatment Item does **not** control tax rates. It does **not** control GL coding. Tax lives on the Tax Policy. GL lives on the GL Assignment Rules. Conflating either with the Billing Treatment Item is one of the most common configuration mistakes in the field.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers will frequently confuse Billing Policy / Billing Treatment / Billing Treatment Item because the names are nearly identical. Pin them down with a one-liner: *Policy is the rule. Treatment is the regional override. Item is the lifecycle distribution.* If they ask about tax or GL coding, redirect — those live in the Tax Policy and the GL Assignment Rules, not on the Billing Treatment Item. |

### The Activation Sequence

The Billing Policy hierarchy enforces a strict activation order: draft policies → draft treatments → draft items → activate items → activate treatments → activate policies. The same pattern applies to the Tax Policy hierarchy you'll see in the next section. You can't activate a parent until its children are active, and you can't deactivate a child while its parent is referencing it. This rule isn't arbitrary — it prevents you from leaving a policy active that points at incomplete treatment logic.

### Treatment Selection Modes

A Billing Treatment can be attached to an Order Product in three modes — **Default**, **Manual**, or **Legal Entity**. Default uses the policy's default Treatment for every applicable Order Product. Legal Entity uses the Treatment whose Legal Entity matches the Order Product. Manual lets the user pick a specific Treatment per Order Product, which is useful for one-off enterprise deals where the regional default doesn't apply.

## Configure the Tax Policy and Its Related Objects

Tax doesn't live on the Billing Policy. It lives on a parallel object called the **Tax Policy** and its related objects. This separation matters. A single Billing Policy applies to many products that are taxed differently by jurisdiction, product type, and customer status. Coupling tax to the billing rules makes every regional change painful. Decoupling them means you change tax logic in one place, and every Billing Policy that uses it inherits the change.

The Tax Policy chain has three tiers, parallel to the Billing Policy chain:

- **Tax Policy** — the parent object. It groups Tax Treatments for a category of products or transactions.
- **Tax Treatment** — a child of the Tax Policy. The Tax Treatment references a Tax Engine (the engine that performs the calculation) and is what gets attached to an Order Product for taxation.
- **Tax Treatment Item** — a child of the Tax Treatment, scoped to the line level.

Two additional objects round out the model:

- **Tax Engine** — the engine of record for tax calculation. Salesforce ships an out-of-the-box engine called the **Revenue Standard Tax Engine**; the alternative is the **Revenue Cloud Tax Extension** type, which is how partner adapters (Vertex, Avalara) and custom Apex implementations of the `TaxEngineAdapter` interface plug in.
- **Tax Engine Provider** — the configurable record that identifies which Tax Engine implementation a Tax Treatment is bound to.

Note that "Tax Code" is a *field* on Tax Rate, Tax Treatment, and Tax Treatment Item — not a top-level object. And the `TaxEngineAdapter` is an Apex interface, not a record.

When an Invoice Line is staged, the system pulls the Tax Treatment from the Order Product's billing context. It walks down to the Tax Engine identified on the Treatment. The output is an Invoice Tax Line that records the auditable result.

Tax addresses come from the Billing Schedule Group rather than directly from the Invoice. That's worth knowing if you're troubleshooting why a particular line ended up in the wrong jurisdiction.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a Finance lead asks "Can your tax handle our footprint?", anchor to the Revenue Standard Tax Engine before you reach for Avalara. Many global customers assume they need a third-party engine when the standard engine plus a properly configured Tax Policy already covers them. The third-party adapter is real, and necessary at extreme complexity, but it's not the default story. |

## Map How the Revenue Standard Tax Engine Drives Taxation

For customers who don't need a third-party tax engine, the platform ships with the **Revenue Standard Tax Engine** and an out-of-the-box decision table called **Revenue Standard Tax Entries**. Together they form the default taxation pipeline.

The flow looks like this:

1. The customer's Billing Schedule Group carries the jurisdictional context — the bill-to address, the legal entity, the currency.
2. The system looks up the Tax Treatment for the Order Product.
3. The Tax Treatment references the Revenue Standard Tax Engine.
4. The engine consults the Revenue Standard Tax Entries decision table.
5. The decision table reads from the **Tax Rate** records the admin has configured (jurisdiction, currency, percentage or flat amount, application basis, validity dates, legal entity).
6. The matched rate is applied and recorded as an Invoice Tax Line.

One operational detail surprises customers: **the Revenue Standard Tax Entries decision table must be refreshed every time a Tax Rate is added or modified.** The decision table is not auto-synced to the underlying records. If you add a new Tax Rate and forget to refresh, the engine won't see it. Flag this gotcha during implementation.

The Tax Rates themselves are admin-created — there is no Salesforce-managed catalog of preconfigured rates. What ships out of the box is the engine and the decision table; the rates that flow through them are yours to configure and maintain.

For customers whose tax needs exceed the Standard Tax Engine, the **Revenue Cloud Tax Extension** type lets a Tax Treatment point at a partner-provided or custom Apex `TaxEngineAdapter` implementation instead. The same downstream model applies — the result is still an Invoice Tax Line — but the calculation happens externally.

## Customize and Edit Milestone Plans

A Milestone Plan defines when a charge is allowed to bill based on the completion of named events rather than a calendar date — go-live, design sign-off, contract signing, hardware shipment. The plan itself is a container; the **Billing Milestone Plan Items** define the individual stages and the financial split (a percentage of the total, a flat amount, or a unit count).

Billing Milestone Plans can be created two ways:

- **Method 1 — Auto-generated from a milestone-enabled Billing Treatment.** Enable the "Enable milestone billing" option on the Billing Treatment. Set up Billing Treatment Item templates with the milestone-specific fields. When an applicable Order Product activates, the system generates the Billing Milestone Plan and its items automatically. The plan is linked to the resulting Billing Schedule.
- **Method 2 — Manually created at the Order Product level.** For deals that need a one-off plan, you create a Billing Milestone Plan and its items directly and bind them to the specific Order Product. This overrides the Treatment's default.

The customization strategy hinges on whether the milestone structure repeats across deals or is unique to one contract. For a repeatable pattern—say, "25% on signing / 50% at design / 25% at go-live"—configure it once at the Billing Treatment level. Every applicable Order Product inherits it. For one-off enterprise deals with negotiated milestone schedules, override at the Order Product. Treating every deal as a one-off is a common anti-pattern that makes the catalog impossible to maintain.

Active Milestone Plans are intentionally restrictive. Once a plan is active, only the **Milestone accomplished** checkbox can be updated. To edit any other field, set the plan's status back to Draft.

Cancellation behavior matters too. When an Order is canceled, invoiced milestones stay—the customer was already billed. Future date-based items move to Canceled. Uninvoiced event-based items also move to Canceled. The system issues a credit memo for the difference automatically.

> **Forward reference:** Once a Milestone Plan exists, *executing* it — actually firing the milestone-driven invoice when the milestone completes — is covered in Module 4: Invoicing and Invoice Explanation Agents. This module is about defining and customizing the plan; Module 4 is about applying it.

## Activate the Order to Billing Schedule Flow

The Order to Billing Schedule flow is the standard automation that turns an activated Order's products into Billing Schedule Groups and Billing Schedules. Like all standard flow templates, it ships read-only. To use it, you save a version of the out-of-the-box flow and activate the clone. The cloned copy runs autonomously from then on—there's nothing to re-trigger or maintain at runtime.

The clone step exists for one reason: the standard template is owned and updated by Salesforce. Customers routinely need to add their own steps—extra fields, custom criteria, integration callouts—without overwriting the template Salesforce maintains. The clone is the customization surface. Once cloned, your copy is yours. The original keeps receiving platform updates without disturbing it.

The Help docs recommend a naming convention: include "Custom" in the cloned flow's name so it's obvious which version is in use. When an Order is activated, two flows fire in parallel—Order to Billing Schedule and Order to Asset. Make sure only one cloned version of each is active to avoid duplicate billing schedules.

Order activation has its own prerequisites once Billing is enabled. The Order needs a Bill to Contact, a Billing Address, and a Shipping Address before it activates cleanly.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** This is a high-frequency objection in technical evals: "Why does this require manual setup?" The honest answer is that it doesn't require manual *operation* — the cloned flow runs by itself — it just requires a one-time clone-and-customize step so you can extend the flow without losing access to platform updates. Customers usually accept this once they understand the upgrade story behind it. |

## Key Takeaways

The Billing Policy hierarchy (Policy → Treatment → Treatment Item) governs *how* charges turn into invoices, with each tier expressing a different level of override. The Tax Policy is a parallel hierarchy (Policy → Treatment → Treatment Item), plus a Tax Engine and a Tax Engine Provider that identify the calculation path. The Revenue Standard Tax Engine plus its Revenue Standard Tax Entries decision table is the default tax pipeline; the decision table must be refreshed every time a Tax Rate changes. Billing Milestone Plans and Billing Milestone Plan Items can be auto-generated from a milestone-enabled Treatment or manually created at the Order Product level. The Order to Billing Schedule flow is cloned to allow customization, then runs autonomously.

## Resources

- [*Salesforce Help:* Manage Billing in Revenue Cloud](https://help.salesforce.com/s/articleView?id=ind.billing.htm&type=5)
- [*Salesforce Help:* Define Billing Policies and Billability Rules](https://help.salesforce.com/s/articleView?id=ind.billing_payment_terms.htm&type=5)
- [*Salesforce Help:* Configure Milestone Billing](https://help.salesforce.com/s/articleView?id=ind.billing_milestone.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Describe the key objects and their purposes in the Billing Policy.** | Which object in the Billing Policy hierarchy is scoped to a specific Legal Entity to support regional variations? | Billing Policy / **Billing Treatment** / Billing Treatment Item / Tax Policy |
| **Explain the function of the Tax Policy and its related objects.** | Where does the Tax Rate that gets applied to a billed line ultimately come from? | The Billing Treatment Item / **A Tax Treatment that references a Tax Engine, which consults Tax Rates configured by the admin** / The GL Assignment Rules / The Order Product directly |

---

# Unit 2: Manage Standalone Billing Schedules, External Billers, and the Invoice Scheduler

## Learning Objectives

After completing this unit, you'll be able to:

- Understand the system's ability to create and amend Standalone Billing Schedules.
- Explain how Revenue Cloud Billing works with external billers.
- Configure the Invoice Scheduler and understand how its settings control the outcomes it produces.

Most Billing Schedules in Revenue Cloud Billing trace back to an Order — the Order activates, the Order to Billing Schedule flow fires, and a Billing Schedule Group with one or more Billing Schedules appears under the customer. But not every billable relationship begins with a Salesforce Order. Some begin with a system migration, an external biller integration, or a one-off invoice that doesn't fit a recurring template. For those cases, you need a **Standalone Billing Schedule**.

## Create and Amend Standalone Billing Schedules

A Standalone Billing Schedule is a Billing Schedule record produced via the **Create Standalone Billing Schedules API** and the **StandaloneBillingContext** context definition. Functionally the resulting record is the same shape as any Order-derived Billing Schedule — it's still a Billing Schedule with a parent Billing Schedule Group, it produces Billing Period Items, and it respects the same Billing Policy and Tax Policy lookups. The "standalone" qualifier describes the *origination path*, not a separate object type.

The Create Standalone Billing Schedules API supports the full transaction lifecycle: original, amended, canceled, renewed, ramped, bundled, and usage-based transactions. It can ingest data directly from external systems or from any Salesforce object, which is what makes it the right tool for ingesting records that didn't originate as Salesforce Orders.

Customers reach for Standalone Billing Schedules in three common scenarios:

- **Migration cutover**, when records from a legacy billing system need to land in Revenue Cloud Billing without being re-keyed as Orders.
- **External-system origination**, when an upstream system other than Salesforce CPQ originates the contract and only the billing side belongs in Salesforce.
- **One-off bills**, when a customer needs to be invoiced for something that genuinely doesn't have an underlying Order (a contract amendment fee, a one-time service charge).

Worth noting: the same API handles the order-derived path when invoked with **BillingContext** instead of StandaloneBillingContext. There isn't a hard line between "Standalone API" and "Order-derived API." It's one API with two context definitions. The context you choose tells the engine whether an Order is involved.

Amending a Standalone Billing Schedule follows the same lifecycle pattern as amending an Order-derived one — you submit an amended transaction through the API, the system reflects the change in the next Billing Period Item it produces, and the audit trail records what changed and when.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Standalone Billing Schedules are an underrated proof point in migration deals. Customers migrating from Zuora, NetSuite Billing, or a legacy CPQ often worry they'll need to re-create every contract as a Salesforce Order. The Standalone API is the answer. It gets the open contracts billing on day one. |

## How Revenue Cloud Billing Works with External Billers

Not every customer wants Salesforce to issue the actual invoice. Some keep an external biller — Stripe, Zuora, an in-house system — for the customer-facing invoicing and payment surface, but use Revenue Cloud Billing as the source-of-truth sub-ledger that owns the contract, the rating, and the schedule. (The Help docs use the term "external systems" or "external transactions" rather than "external biller," but the concept is the same.)

Revenue Cloud Billing supports this pattern through several integration points:

- **Create Standalone Billing Schedules API** with StandaloneBillingContext — the primary path for ingesting external transactions as billing schedules. Supports original, amended, canceled, renewed, ramped, bundled, and usage transactions.
- **sObject APIs** — for direct, programmatic creation of Billing Schedule records when the Standalone API doesn't fit (for example, lower-volume or one-off ingestion).
- **Invoice Ingestion API** — creates standalone or imported invoices directly from an external system, and can also generate invoices from debit memos.
- **Import External Tax Lines** — when an external tax engine is authoritative, you set Is Taxable=false on the Tax Treatment and import tax lines via CSV (with a TaxProcessingStatus field) so the Salesforce side records the tax result without recalculating it.
- **TaxEngineAdapter Apex interface** — for live, callout-style integration with a partner or custom tax engine (Vertex, Avalara, or proprietary).
- **Suspend Billing API / Resume Billing API** — for pausing and resuming billing on a customer's schedules without canceling the underlying records.
- **Custom intracontext mapping** — the supported mechanism to pass custom fields from an external transaction or Salesforce Order through to the resulting Billing Schedule, so external attributes don't get lost on the way through the engine.

The integration story is, in plain terms: the external biller can own the customer-facing surface; Revenue Cloud Billing owns the data model. The two stay synchronized through the APIs above, with the customer keeping a single source of truth on the Salesforce side regardless of where the bill originates.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a customer says "we already have Stripe / Zuora / our own biller," position Revenue Cloud Billing as the system of record that talks to their existing biller. Most enterprises have a multi-year migration path away from a legacy biller. Making Revenue Cloud Billing the destination doesn't require day-one cutover. |

## Configure the Invoice Scheduler

The **Invoice Scheduler** (sometimes called the Invoice Batch Run or the Billing Batch Scheduler) is the configurable batch process that turns ready-to-bill Billing Schedules and Billing Period Items into actual Invoices and Invoice Lines on a defined cadence. In Module 1 v2 you saw it at a conceptual level alongside Billing Preview and Bill Now; here you configure it.

You set up an Invoice Scheduler in Setup → Quick Find → Billing Batch Schedulers → New Invoice Scheduler. The scheduler's configuration controls four broad areas — and each setting has a direct, predictable effect on what the run produces:

| Setting category | Specific settings | Effect on outcomes |
|:--|:--|:--|
| **When the scheduler runs** | Active toggle, Start Date, Start Time, Time Zone, End Date | Sets when the batch is allowed to run and over what window |
| **Output state** | Post invoices toggle | Controls whether output Invoices land in Posted or Draft status |
| **Cadence** | Frequency (Once / Daily / Weekly / Monthly), Exclude holidays and weekends (Monthly only) | Sets how often the scheduler fires; the holiday/weekend exclusion is restricted to Monthly frequency |
| **Date logic** | Target Date and Target Date Offset; Invoice Date and Invoice Date Offset; "Calculate invoice date from run date" | Determines which billing schedules are picked up and what date the resulting Invoice carries |
| **Filter criteria** | Billing batch, Billing charge type (multi-select), Legal entity, Customer account, Currency (multi-select) | Scopes which records become Invoices in this run; the rest defer to the next run |

A note on a feature that's already shipped, contrary to common assumption: **the "Exclude holidays and weekends" option is available in 260, not a 262 enhancement.** It applies only to Monthly-frequency schedulers. If you've heard a teammate describe it as upcoming, the feature has already arrived.

The diagnostic pattern when an Invoice Scheduler produces an unexpected result almost always traces back to one of these settings — most commonly a filter that excluded records you expected to bill, a date offset that picked up the wrong window, or a frequency mismatch with the customer's Billing Profile.

Two platform limits to keep in mind when you scope a customer's volume: **a maximum of 30 active Billing Batch Schedulers** per org, and **a maximum of 2,000 invoice lines per invoice**. Customers with very high invoice-line density design their grouping rules to stay under the per-invoice line cap.

Note that **email delivery is not** an Invoice Scheduler setting. Invoice email delivery is a separate feature — Send Invoices Through Email — that takes over once the scheduler has produced and posted the invoices. That separation is intentional: it lets you generate invoices on one cadence and deliver them on another.

Adjacent to the Invoice Scheduler, the **Suspend Billing API** and **Resume Billing API** let you pause and resume billing on specific Billing Schedule Groups without canceling the underlying records. Suspend/Resume is a recurring ask in field deals where a customer needs to put a service on hold without losing the contract.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers with high-volume billing will ask whether the Invoice Scheduler can scale. Lead with the asynchronous batch architecture and the High Scale Billing capability rather than handwaving "it scales." For genuinely extreme volumes (hundreds of thousands of invoices per run), High Scale Billing is what you're selling, and it's a real differentiator against legacy on-premise billers. |

## Key Takeaways

Standalone Billing Schedules are Billing Schedule records produced via the Create Standalone Billing Schedules API and the StandaloneBillingContext context definition — the right tool for migrations, external-system originations, and one-off bills. Revenue Cloud Billing integrates with external systems through several APIs (Standalone Billing Schedules, Invoice Ingestion, Import External Tax Lines, Suspend/Resume Billing) plus the TaxEngineAdapter Apex interface, letting customers keep an external biller while making Revenue Cloud Billing the system of record. The Invoice Scheduler is configured by run cadence, date logic, and filter criteria; "Exclude holidays and weekends" is a Monthly-only feature already in 260. Email delivery is a separate feature that runs after the scheduler completes.

## Resources

- [*Salesforce Help:* Generate Invoices in Revenue Cloud](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_run.htm&type=5)
- [*Salesforce Help:* Migrate External Billing Data](https://help.salesforce.com/s/articleView?id=ind.billing_migrate_external.htm&type=5)
- [*Salesforce Developer Guide:* Billing Business APIs](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/rcm_billing.htm)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Understand the system's ability to create and amend Standalone Billing Schedules.** | A customer is migrating from a legacy biller and needs to bring 5,000 active contracts into Revenue Cloud Billing without re-creating each as a Salesforce Order. Which capability supports this? | Bulk Order Import / **The Create Standalone Billing Schedules API with StandaloneBillingContext** / Order to Billing Schedule flow / Tax Engine Adapter |
| **Configure the Invoice Scheduler and understand how its settings control the outcomes it produces.** | A monthly Invoice Scheduler produced fewer Invoices than expected. Which setting is the most likely cause? | The Time Zone field / **The Filter criteria (billing batch, charge type, legal entity, customer account, currency)** / The Post invoices toggle / The Tax Policy assignment |

---

# Appendix: Open Questions and Parking Lot

Most factual questions from the v1 review have been resolved against the Spring '26 Help compendium (`docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf`). The two items that remain are positioning questions for Mike + the L2 mix authoring team, not factual questions for the Help docs.

## Remaining positioning questions

The Help docs use "external systems" and "external transactions" rather than "external biller." This v2 keeps Mike's "external billers" framing in the unit title and LO 2.2 because that's the seller-facing term, but uses both terms in the body so a learner who reads the Help docs later isn't confused. Mike, please confirm that's the right call.

The "Exclude holidays and weekends" setting is documented as already-in-260, not a 262 enhancement. The v1 draft and the FY27 outline implied it was forthcoming. If there's a *separate* 262 enhancement to scheduler date logic, please point me at it so it can be added to LO 2.3.

## Topics from the v1 draft that have no current home in Modules 1–5

These need a scoping decision from Mike + the L2 authoring team. They were in the v1 Module 2 draft, none of them are covered elsewhere in the L2 mix, and the v2 draft drops them per Mike's revised LOs.

- **The "Big Four Flows" framing.** Mike commented "This is wrong" and "Same comments as above. If you want to talk about how billing gets setup cover the context service and the flow that runs." The "context service" hint suggests there's a more accurate billing-setup story (likely involving BillingContext / StandaloneBillingContext / the Order to Billing Schedule flow) that should be authored somewhere — but it's not the four-flow framing the v1 used.
- **DRO Settings.** Mike: "DRO is not part of billing and it does not setup the billing objects." Belongs in a different module entirely (likely Order Lifecycle / Fulfillment).
- **Pricing Setup.** Mike: "These are not billing related." Belongs in a Pricing module.
- **Multi-currency and Localization** as a standalone section. The v1 draft had this; it's tangentially relevant to LO 1.2 / 1.3 (Tax addresses, Legal Entity, currency on Tax Rate) but isn't called for as its own topic by Mike's LOs.
- **ERP Integration / System of Execution / PLG-vs-Enterprise Bifurcation Pattern.** Strategic/positioning content. None of Modules 1–5 cover it.
- **Standalone Billing APIs as a "headless commerce" topic.** The v2 above covers Standalone Billing Schedules thoroughly; the headless-commerce framing of the *API surface itself* (separate from the ingestion use case) is not in Modules 1–5.

## Topics already covered elsewhere in the L2 mix that v1 had in Module 2 — confirmed routed away

For audit completeness: these v1 Module 2 topics route to other modules and are correctly absent from this v2.

- Usage Entitlement Account, Buckets, Digital Wallet, m3ter — Module 3.
- Hybrid Models, Pure Consumption — Module 3.
- Mediation pipeline (Collection, Normalization, Quality, Aggregation, Correlation, Usage Binding) — Module 3.
- Milestone billing as an *invoicing pattern* (Module 4 covers application; Module 2 covers definition/customization).
- Dunning workflows — Module 5.
- Collections and Dispute Agent — Module 5.

## Cross-module observations for the next review pass

The same v1 voice patterns that Module 1 v2 corrected ("Salesforce / Agentforce actively works on your behalf," metaphor saturation, soft-on-object-names) are present in Modules 3, 4, and 5. They will need the same review pass once Module 2 is settled. Module 4's Resources section is also still placeholder text from the Trailhead template (e.g., "Personalized Email Marketing"); the actual resources for Module 4 need to be authored.

---

*Prepared by Brian Galdino with AI assistance, May 7, 2026. Source-verified against `docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf` (Spring '26 Help compendium, 1,460 pages).*
