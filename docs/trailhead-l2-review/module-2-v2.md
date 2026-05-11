# Module 2: Billing Technical Architecture and Data Model Deep Dive

**Status:** v2 draft for SME review (Trailhead AI Review Checklist applied; 262 snapshot validation pass completed 2026-05-11)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team
**Source verifications:** 262 Billing Help snapshot (`docs/salesforce/262/help/articles/`, Summer '26, 171 articles), project metadata (qb-billing, qb-tax, ERD), and FY27 outline (Mike's Revised LOs column). See `module-2-v2-262-validation-report.md` for the per-claim citation log.
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

| Note | Content |
|:-:|:-:|
| icon=true | **What's in a Name?** Don't confuse **Billing Settings** (billing configuration) with **Revenue Settings** (Revenue Cloud Advanced configuration — not billing). |

## Configure the Billing Policy

The Billing Policy is the top-level object in a three-tier hierarchy that decides how a product's charges turn into invoices. The hierarchy is:

- **Billing Policy** — the parent object. Its job is to decide *which* Billing Treatment applies to a given charge. It carries a Status, a Billing Treatment Selection strategy (None, Manual, Default, or Legal Entity), and a Default Billing Treatment to fall back to. The Policy doesn't carry billing rules. It carries the *selection logic* that picks the right Treatment.
- **Billing Treatment** — a child of the Billing Policy. The Treatment is a variant of the Policy that carries feature toggles (Enable milestone billing, Change Billing Frequency, Exclude from Billing) and optionally a Legal Entity and Currency. Whether the Legal Entity is populated depends on the parent Policy's Billing Treatment Selection mode. If the Policy uses Legal Entity selection, each Treatment under it is scoped to a specific Legal Entity — that's how the same Policy applies different rules to your US entity versus your Canada entity. If the Policy uses Default or Manual selection, the Treatment can exist without any Legal Entity scope at all.
- **Billing Treatment Item** — a child of the Billing Treatment. This is where the actual billing mechanics live. The Billing Type (Advance, Arrears, or None) is here. So is the lifecycle distribution: Type (Remainder vs. Percentage), Percentage or Flat Amount, Processing Order, Sequencing, and zero-amount handling. When milestone billing is enabled on the parent Treatment, the Item also carries milestone-specific fields — Milestone Type (Event or Date), Milestone Start Date, Offset, and Offset Unit.

A Treatment can have one BTI or many. The count depends on the billing pattern. For a simple Advance or Arrears Treatment, you typically have a single BTI with Type=Remainder that captures 100% of the order item's value. For more complex patterns — milestone billing, partial billing, multi-stage distributions — you have multiple BTIs per Treatment, each with Type=Percentage or Flat Amount, that collectively distribute the value. ProcessingOrder controls which BTI fires first when multiple are involved.

A useful one-liner: **Policy is the selection strategy. Treatment is the variant with feature toggles. Treatment Item is the billing math.**

The Billing Treatment Item does **not** control tax rates. It does **not** control GL coding. Tax lives on the Tax Policy. GL lives on the GL Assignment Rules. Conflating either with the Billing Treatment Item is one of the most common configuration mistakes in the field.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers frequently confuse Billing Policy / Billing Treatment / Billing Treatment Item because the names are nearly identical. When that happens, anchor them to where rules actually live: Policy decides *which* Treatment applies, Treatment carries the scope and toggles, Treatment Item carries the billing math. If they ask about tax or GL coding, redirect — those live on the Tax Policy and the GL Assignment Rules respectively. |

### Treatment Selection Modes

A Billing Treatment can be attached to an Order Product in three modes — **Default**, **Manual**, or **Legal Entity**. Default uses the policy's default Treatment for every applicable Order Product. Legal Entity uses the Treatment whose Legal Entity matches the Order Product. Manual lets the user pick a specific Treatment per Order Product, which is useful for one-off enterprise deals where the regional default doesn't apply.

One important caveat: a user can override the policy's default Billing Treatment Selection on the Order Product while the Order is in Draft. Once the Order is activated and the Billing Schedule Group and Billing Schedules are created, the Treatment can no longer be changed.

### Set Up Milestone Billing at the BTI Level

Milestone billing is configured directly on the Billing Treatment and its BTIs. The setup is two parts.

**On the parent Billing Treatment**, set Enable milestone billing to true. This unlocks the milestone-specific fields on the child BTIs.

**On the BTIs**, create one BTI per milestone. For each:

- Set **Type** to Percentage (or Flat Amount).
- Set **Percentage** to the share of the order item's value this milestone bills.
- Set **Processing Order** to control firing sequence.
- Set **Milestone Type** to Event or Date. An Event milestone fires when someone marks it complete. A Date milestone fires automatically on a calculated date.
- For Date milestones: select **Billing Schedule Start Date** as the **Milestone Commencement Trigger** (the anchor). Then set the **Milestone Commencement Offset** and **Milestone Commencement Offset Unit** (for example, 1 Month, or 4 Months).

A common pattern is mixing types — early milestones are Date-driven (fire automatically based on calendar offsets from activation), while a final milestone is Event-driven (fires when someone marks project handoff complete). The Percentage and Flat Amount BTIs distribute the value; when they don't sum to 100%, the system auto-generates a Remainder Plan Item at runtime to absorb the gap.

What you configure here is the **template**. When an Order Product activates against this Treatment, the system uses these BTIs to generate a runtime Billing Milestone Plan with Billing Milestone Plan Items — that's the per-deal record customers see. If a specific deal needs milestones that diverge from the template, you can pre-create the Billing Milestone Plan and Plan Items manually and link them to the Order Product. The Customize and Edit Milestone Plans section covers the runtime side in detail.

## Configure the Tax Policy and Its Related Objects

Tax doesn't live on the Billing Policy. It lives on its own object called the **Tax Policy**, with its own related objects. The Tax Policy and the Billing Policy operate independently — an Order Product is assigned a Billing Policy and a Tax Policy separately, and changes to one don't ripple to the other.

The Tax Policy chain has three tiers:

- **Tax Policy** — the parent object. It groups Tax Treatments for a category of products or transactions.
- **Tax Treatment** — a child of the Tax Policy. The Tax Treatment references a Tax Engine (the engine that performs the calculation) and is what gets attached to an Order Product for taxation.
- **Tax Treatment Item** — a child of the Tax Treatment, scoped to the line level. Tax Treatment Items are conditional — they're used only when the parent Tax Treatment has Use Tax Treatment Items enabled.

The Tax Policy mirrors the Billing Policy's selection mechanics. It carries a TreatmentSelection mode (None, Manual, Default, or Legal Entity) and a Default Tax Treatment to fall back to. When the policy uses Legal Entity selection, each Tax Treatment under it is scoped to a specific Legal Entity — the same conditional pattern you saw on Billing Treatments.

Three additional objects round out the model:

- **Tax Engine** — the engine of record for tax calculation. Salesforce ships an out-of-the-box engine called the **Revenue Standard Tax Engine**. The alternative is the **Revenue Cloud Tax Extension** type, which is how partner adapters (Vertex, Avalara) and custom Apex implementations of the `TaxEngineAdapter` interface plug in.
- **Tax Engine Provider** — the configurable record that points at the Apex adapter class (the implementation of `TaxEngineAdapter`). Each Tax Engine references one Provider; each Tax Treatment references one Tax Engine.
- **Tax Rate** — the actual rate record the engine matches against. Carries jurisdiction (country and state), currency, percentage or flat amount, application basis, priority, validity dates, and legal entity. The Revenue Standard Tax Engine consults Tax Rate records through the Revenue Standard Tax Entries decision table; partner adapters consume them through whatever logic the adapter implements. The **Tax Code** is a shared string identifier that ties a Tax Rate to its consuming Tax Treatment or Tax Treatment Item — configure it on the Tax Rate and reference the same value from the Treatment side so the engine picks the correct rate at calculation time.

Note: the `TaxEngineAdapter` is an Apex interface, referenced indirectly through the Tax Engine Provider's Apex adapter — not a record.

When an Invoice Line is staged, the system pulls the Tax Treatment from the Order Product's billing context. It walks down to the Tax Engine identified on the Treatment. The output is an Invoice Tax Line that records the auditable result.

The Revenue Standard Tax Engine calculates taxes at the line level. Header-level tax capture is configurable on the Tax Engine record (UI label: **Capture Taxes at Header**; SObject field: `ShouldCaptureTaxesAtHeader`). Use it when your engine returns a single consolidated tax amount at the invoice header rather than per line — a common pattern with third-party engines like Vertex or Avalara, and a frequent customer question worth knowing.

By default, the address used for tax calculation comes from the Billing Schedule Group. This can be overridden at the Tax Engine level via the address fields on the Tax Engine record (the compound `TaxEngineAddress` field aggregates the underlying street, city, state, and postal fields). An additional invoice-line-level override is also available — useful when individual lines need a different tax address than the BSG default.

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

In the previous section you saw how milestone billing is configured at *design time* on the Billing Treatment Item. This section covers what happens at *runtime*: the **Billing Milestone Plan** and **Billing Milestone Plan Items** that the system creates when an Order Product activates.

The runtime relationship works like this. When an Order Product activates against a milestone-enabled Billing Treatment, the system creates a Billing Milestone Plan as a per-deal record bound to the resulting Billing Schedule. For each milestone BTI on the Treatment template, the system creates a corresponding Billing Milestone Plan Item. The Plan Items carry runtime-only fields the BTI templates don't — `IsMilestoneAccomplished` (the toggle that fires Event milestones), `MilestoneAmount` (the calculated dollar amount), and service period dates.

Worth flagging for developers tracing a milestone from configuration to runtime: the UI labels on both objects use "Commencement Trigger / Offset / Offset Unit," but the underlying **API field names** shift between the template and Plan Item. On `BillingTreatmentItem` the API fields are `MilestoneStartDate`, `MilestoneStartDateOffset`, and `MilestoneStartDateOffsetUnit`. The `BillingMilestonePlanItem` rebadges them as `CommencementDate`, `CommencementDateOffset`, and `CommencementDateOffsetUnit`. Same concept, different API names.

Billing Milestone Plans can be created two ways:

- **Method 1 — Auto-generated from a milestone-enabled Billing Treatment.** This is the standard path covered above. The BTI templates drive the runtime Plan and its Items at Order activation.
- **Method 2 — Manually created for a specific Order Product.** For deals that need a one-off plan diverging from the Treatment template, you create a Billing Milestone Plan and its Items directly and bind them to the Order Product. This overrides the Treatment's default.

The customization strategy hinges on whether the milestone structure repeats across deals or is unique to one contract. For a repeatable pattern — say, "25% on signing / 50% at design / 25% at go-live" — configure it once at the Billing Treatment level. Every applicable Order Product inherits it through the auto-generation path. For one-off enterprise deals with negotiated milestone schedules, override at the Order Product. Treating every deal as a one-off is a common anti-pattern that makes the catalog impossible to maintain.

Active Billing Milestone Plans are intentionally restrictive. Once a Plan is active, only the **Milestone accomplished** checkbox on its Plan Items can be updated. To edit any other field, set the Plan's status back to Draft.

Cancellation behavior matters too. When an Order is canceled, invoiced milestones stay — the customer was already billed. Future date-based items move to Canceled. Uninvoiced event-based items also move to Canceled. The system issues a credit memo for the difference automatically.

Amendments deserve their own callout. By default, milestone billing doesn't create new milestone plans or plan items for amend or renew orders. The **Support Milestone Plans for Amended Billing Schedules** setting changes that: with it enabled, Billing creates or links a milestone plan to the amendment schedule and recalculates milestone dates and amounts from the amendment start date.

> **Forward reference:** Once a Billing Milestone Plan exists, *executing* it — actually firing the milestone-driven invoice when a milestone completes — is covered in Module 4: Invoicing and Invoice Explanation Agents. This module is about defining and customizing the plan; Module 4 is about applying it.

## Activate the Order to Billing Schedule Flow

The Order to Billing Schedule flow is the standard automation that turns an activated Order's products into Billing Schedule Groups and Billing Schedules. Like all standard flow templates, it ships read-only. To use it, you save a version of the out-of-the-box flow and activate the clone. The cloned copy runs autonomously from then on—there's nothing to re-trigger or maintain at runtime.

The clone step exists for one reason: the standard template is owned and updated by Salesforce. Customers routinely need to add their own steps—extra fields, custom criteria, integration callouts—without overwriting the template Salesforce maintains. The clone is the customization surface. Once cloned, your copy is yours. The original keeps receiving platform updates without disturbing it.

The Help docs recommend a naming convention: include "Custom" in the cloned flow's name so it's obvious which version is in use. When an Order is activated, two flows fire in parallel—Order to Billing Schedule and Order to Asset. Make sure only one cloned version of each is active to avoid duplicate billing schedules.

Order activation has its own prerequisites once Billing is enabled. The Order needs a Bill to Contact, a Billing Address, and a Shipping Address before it activates cleanly.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** This is a high-frequency objection in technical evals: "Why does this require manual setup?" It doesn't require manual *operation* — the cloned flow runs by itself. It requires a one-time clone-and-customize step so you can extend the flow without losing access to platform updates. Customers usually accept this once they understand the upgrade story behind it. |

## Key Takeaways

The Billing Policy hierarchy decides which Treatment applies; the Treatment carries scope and toggles; the Treatment Item carries the billing math. The Tax Policy hierarchy works the same way — Policy, Treatment, optional Treatment Item — with a Tax Engine that references a Tax Engine Provider, which points at the Apex adapter. The Revenue Standard Tax Engine plus its Revenue Standard Tax Entries decision table is the default tax pipeline. The decision table must be refreshed every time a Tax Rate changes. Milestone billing is configured at design time on the Billing Treatment Item; the runtime Billing Milestone Plan and its Plan Items are auto-generated when an Order Product activates. The Order to Billing Schedule flow is cloned to allow customization, then runs autonomously.

## Resources

- [*Salesforce Help:* Manage Billing in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing.htm&type=5)
- [*Salesforce Help:* Define Billing Policies and Billability Rules](https://help.salesforce.com/s/articleView?id=ind.billing_policies_and_treatments.htm&type=5)
- [*Salesforce Help:* Configure Milestone Billing](https://help.salesforce.com/s/articleView?id=ind.billing_milestone_plans.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Describe the key objects and their purposes in the Billing Policy.** | Which object in the Billing Policy hierarchy can be scoped to a specific Legal Entity to support regional variations? | Billing Policy / **Billing Treatment** / Billing Treatment Item / Tax Policy |
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

One important constraint to keep in mind: when a Billing Schedule Group is already linked to an asset, downstream amendments, renewals, and cancellations must run through the Order to Billing Schedule flow or the Create Billing Schedules for Orders API — not the Standalone API. The Standalone API path is for billing schedules that don't have an asset on the other side of the relationship.

A 262 enhancement worth knowing for technical eval conversations: the Standalone API now supports **minimal, intent-based requests** for amendments, renewals, cancellations, and price/quantity/end-date changes. Billing auto-computes unit price and total price from historical transaction context or Billing Schedule Group IDs, so the caller doesn't need to re-state everything to make a single change.

Customers reach for Standalone Billing Schedules in three common scenarios:

- **Migration cutover**, when records from a legacy billing system need to land in Revenue Cloud Billing without being re-keyed as Orders.
- **External-system origination**, when an upstream system other than Salesforce CPQ originates the contract and only the billing side belongs in Salesforce.
- **One-off bills**, when a customer needs to be invoiced for something that genuinely doesn't have an underlying Order (a contract amendment fee, a one-time service charge).

Worth noting: the same API handles the order-derived path when invoked with **BillingContext** instead of StandaloneBillingContext. There isn't a hard line between "Standalone API" and "Order-derived API." It's one API with two context definitions. The context you choose tells the engine whether an Order is involved.

Amending a Standalone Billing Schedule follows the same lifecycle pattern as amending an Order-derived one — you submit an amended transaction through the API, the system reflects the change in the next Billing Period Item it produces, and the audit trail records what changed and when.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Standalone Billing Schedules are a powerful proof point in migration deals. Customers migrating from Zuora, NetSuite Billing, or a legacy CPQ often worry they'll need to re-create every contract as a Salesforce Order. The Standalone API is the answer. It gets the open contracts billing on day one. |

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

You set up an Invoice Scheduler from the App Launcher: find and select Billing Batch Schedulers, then click New Invoice Scheduler. The scheduler's configuration controls four broad areas — and each setting has a direct, predictable effect on what the run produces:

| Setting category | Specific settings | Effect on outcomes |
|:--|:--|:--|
| **When the scheduler runs** | Active toggle, Start Date, Start Time, Time Zone, End Date | Sets when the batch is allowed to run and over what window |
| **Output state** | Post invoices toggle | Controls whether output Invoices land in Posted or Draft status |
| **Cadence** | Frequency (Once / Daily / Weekly / Monthly), Exclude holidays and weekends (Daily / Weekly / Monthly) | Sets how often the scheduler fires; the holiday/weekend exclusion is available on all recurring frequencies |
| **Date logic** | Target Date and Target Date Offset; Invoice Date and Invoice Date Offset; "Calculate invoice date from run date" | Determines which billing schedules are picked up and what date the resulting Invoice carries |
| **Filter criteria** | Billing batch, Billing charge type (multi-select), Legal entity, Customer account, Currency (multi-select) | Scopes which records become Invoices in this run; the rest defer to the next run |

A note on a 262 enhancement: the **Exclude holidays and weekends** option is now available for all recurring frequencies — **Daily, Weekly, and Monthly**. Before 262 this option was restricted to Monthly scheduling. When enabled, the scheduler's next run moves to the following business day if it falls on a company holiday or a weekend. The Once frequency doesn't carry this option because there's no recurring run to defer.

The diagnostic pattern when an Invoice Scheduler produces an unexpected result almost always traces back to one of these settings — most commonly a filter that excluded records you expected to bill, a date offset that picked up the wrong window, or a frequency mismatch with the customer's Billing Profile.

Two platform limits to keep in mind when you scope a customer's volume: **a maximum of 30 active Billing Batch Schedulers** per org, and **a maximum of 2,000 invoice lines per invoice**. Customers with very high invoice-line density design their grouping rules to stay under the per-invoice line cap.

Note that **email delivery is not** an Invoice Scheduler setting. Invoice email delivery is a separate feature — Send Invoices Through Email — that takes over once the scheduler has produced and posted the invoices. That separation is intentional: it lets you generate invoices on one cadence and deliver them on another.

Adjacent to the Invoice Scheduler, the **Suspend Billing API** and **Resume Billing API** let you pause and resume billing on specific Billing Schedule Groups without canceling the underlying records. Suspend/Resume is a recurring ask in field deals where a customer needs to put a service on hold without losing the contract.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers with high-volume billing will ask whether the Invoice Scheduler can scale. Lead with the asynchronous batch architecture and the High Scale Billing capability rather than handwaving "it scales." For genuinely extreme volumes (hundreds of thousands of invoices per run), High Scale Billing is what you're selling, and it's a real differentiator against legacy on-premise billers. |

## Key Takeaways

Standalone Billing Schedules are Billing Schedule records produced via the Create Standalone Billing Schedules API and the StandaloneBillingContext context definition. They're the right tool for migrations, external-system originations, and one-off bills. Revenue Cloud Billing integrates with external systems through several APIs — Standalone Billing Schedules, Invoice Ingestion, Import External Tax Lines, Suspend/Resume Billing — plus the TaxEngineAdapter Apex interface. Customers can keep an external biller while making Revenue Cloud Billing the system of record. The Invoice Scheduler is configured by run cadence, date logic, and filter criteria. In 262, the Exclude holidays and weekends setting is available for Daily, Weekly, and Monthly recurring frequencies (an expansion from the Monthly-only behavior in 260). Email delivery is a separate feature that runs after the scheduler completes.

## Resources

- [*Salesforce Help:* Generate Invoices in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_generation.htm&type=5)
- [*Salesforce Help:* Generate Billing Schedules from External Transactions or Salesforce Objects](https://help.salesforce.com/s/articleView?id=ind.billing_schedules_standalone_api.htm&type=5)
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

*Prepared by Brian Galdino with AI assistance, May 7, 2026; re-grounded against the 262 Summer '26 Billing Help snapshot on May 11, 2026. Per-claim citation log: `docs/trailhead-l2-review/module-2-v2-262-validation-report.md`.*
