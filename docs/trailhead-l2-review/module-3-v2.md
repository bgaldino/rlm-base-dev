# Module 3: Usage, Rating, and Consumption Agents

**Status:** v2 draft for SME review (Trailhead AI Review Checklist applied; grounded against the 262 Summer '26 Help portal capture covering Usage Management, Rate Management, and the Agentforce for Revenue Management agent suite)
**Reviewers:** Michael Aaron (SME), Trailhead editorial team
**Source verifications:** Salesforce Help portal (Usage Management area `ind.um_*`, Rate Management area `ind.rm_*`, Agents area `ind.rev_agent_*`), project metadata (`.sfdx/tools/sobjects/standardObjects/`), and the ARM Billing L2 Outline (Mike's revised LOs). See `module-3-262-lo-validation-report.md` for the per-claim citation log.
**Style note:** This module describes the latest, generally-available capabilities. It deliberately avoids release-version notations (260, 262, Spring '26, Summer '26) so the content stays evergreen.
**Style notes for editorial:** This draft bolds product object names (Usage Entitlement Bucket, Rating Procedure, etc.) for technical clarity. That deviates from the AI Review Checklist's "no bold to highlight words or phrases" guidance, but matches the convention established across Modules 1, 2, 4, and 5 of the L2 mix.

---

**Badge Description:** Map the usage data model, navigate the rating pipeline, and apply the Consumption Management subagent to bill consumption-based products at scale.

## Suggested Unit Titles

| # | Name | Type | Word Count *(editors fill this out)* |
|:--|:--|:--|:--|
| 1 | Map the Usage Data Model | Quiz | |
| 2 | Navigate the Usage Rating Pipeline | Quiz | |
| 3 | Apply the Consumption Management Subagent and Drawdown Policies | Quiz | |

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

# Unit 1: Map the Usage Data Model

## Learning Objectives

After completing this unit, you'll be able to:

- Identify the headline objects in the usage data model and the role each one plays.
- Explain how the usage data model is populated automatically at order activation for usage-based products.
- Map how the binding mechanism determines what a usage entitlement bucket can draw from.

In Modules 1 and 2, you saw the core billing data model — Order, Billing Schedule Group, Billing Schedule, Invoice. Module 3 extends that model to handle a different revenue pattern: consumption-based products, where a customer pays based on what they use rather than a fixed subscription. Usage Management is the part of Agentforce Revenue Management that defines, rates, tracks, and bills these products. Before any of that machinery can run, the right records have to exist in the right shape. Unit 1 lays out those records.

| Note | Content |
|:-:|:-:|
| icon=true | **What's in a Name?** Usage Management is the umbrella area. **Consumption Management** is a sub-pillar within it — specifically the lifecycle that tracks consumption data and generates invoice-ready summaries. Both terms appear in Help docs, so it's worth knowing the relationship. |

## Define the Usage Data Model Objects

Six objects do most of the work in the usage data model. Three sit on the entitlement side, two sit on the rating side, and one binds the customer's entitlements to the products they purchased.

- **Usage Entitlement Account (UEA)** — think of this as a credit card in the customer's wallet. Each UEA carries a balance, gets credited with new grants, charged for consumption, and refunded when adjustments apply. The UEA carries the billing cycle details (frequency, billing day of month, start and end dates, the service it's tied to) and is created automatically after an order is activated and assetized.
- **Usage Entitlement Bucket** — the balance on the card. When grants are rolled over or renewed, units are added to the bucket. When the customer consumes the usage resource, units are debited from it. A UEA has one or more buckets, one per usage resource.
- **Usage Entitlement Entry** — a transaction line on the statement. Each entry captures one credit or debit against a bucket, and together the entries form the audit trail for what flowed in and out.
- **Transaction Usage Entitlement (TUE)** — stores information about how grants are tracked and managed for a usage resource. Includes the associated usage grant rollover policy, usage grant refresh policy, drawdown order in which grant consumption is debited, and the binding target for the entitlement.
- **Asset Rate Card Entry** — the customer-specific rate for a usage resource on a particular asset. Rate Cards define list rates at the catalog level; Asset Rate Card Entries are the actual negotiated rates on the deal.
- **Asset Rate Adjustment** — tiered or banded adjustments layered on top of an Asset Rate Card Entry. Used for volume discounts, time-of-day pricing, or other consumption-driven adjustments.

A useful one-liner: **UEA holds the relationship. Buckets hold the balance. Entries are the audit trail. TUE governs how the grant behaves. Asset Rate Card Entry and Asset Rate Adjustment determine the rate.**

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers often try to skip past the data model in technical evals because the object names feel abstract. Anchor them to the credit-card-in-wallet metaphor: the customer's wallet holds one or more UEAs (each a credit card), each bucket is the balance on the card for one resource, and each entry is a transaction line on the statement. When you frame it the way finance buyers already see their own credit-card statements, the schema clicks. |

## How Records Are Populated at Order Activation

The customer doesn't create most of these records manually. The system creates them as a side effect of order activation. The sequence is:

1. An order with a usage-based product is activated.
2. The system **assetizes** the order — creates an Asset record for each Order Product.
3. For each usage-based Asset, the system creates a **Usage Entitlement Account** and the related **Usage Entitlement Buckets** for each usage resource the product grants.
4. The system creates the **Transaction Usage Entitlement** record that captures the binding policy, rollover policy, refresh policy, and drawdown order for the granted resources.
5. **Asset Rate Card Entries** and **Asset Rate Adjustments** are populated based on what was negotiated during the quote step.

The admin doesn't configure individual buckets per customer — they configure the rules, and the system creates the records when an order activates. This is one of the most important seller proof points for usage-based selling: there's no manual data entry between deal close and bill ready.

## Understand the Binding Mechanism

Binding is how usage products pool their resources together. A Transaction Usage Entitlement has a `GrantBindingTargetId` field that points at the target that owns the grant. A Usage Entitlement Account also has its own `GrantBindingTargetId`. The Bucket inherits its binding through `ParentId`.

The binding target for both anchor and add-on usage products can be one of four things:

- **An Account** — the grant is shared across every relevant asset the account owns. Buy a corporate-wide quota and every business unit draws from the same pool.
- **An Asset** — the grant is specific to a base product (the "anchor"). Add-on packs that bind to the anchor add to the same pool.
- **A Contract** — the grant is scoped to a specific contract. Useful when one account has multiple contracts and each carries its own pool.
- **A Custom Object** — for scenarios that don't fit the above three patterns.

The `UsagePrdGrantBindingPolicy` object holds the policy itself — admins create binding policies once and apply them to multiple usage products. When the system creates a Transaction Usage Entitlement at order activation, it consults the binding policy to determine which target ID to write to `GrantBindingTargetId`.

**Unit of Measure (UOM) and UOM Class** are what let multiple usage resources land on the same binding target. UOM is the unit a resource is counted in (GB, minutes, API calls). UOM Class groups compatible units together — for example, a **Data** UOM Class can hold MB, GB, and TB, and a **Time** UOM Class can hold seconds, minutes, and hours. When two usage resources share a UOM Class, the binding mechanism can pool them on the same Usage Entitlement Bucket. That's how a customer's data overage pack and the base data plan end up depleting from the same balance even when one is priced per GB and the other per TB — they share the Data UOM Class, so they share the wallet.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Binding is what separates "a customer with multiple SKUs" from "a customer with a pooled allowance." When a prospect tells you they have a pooled usage use case, that's a binding pattern. The base product is the Anchor. The packs bind to it. They all share one parent Usage Entitlement Bucket. This is a recurring pattern in telecom, infrastructure, and platform pricing. |

## Key Takeaways

The usage data model has six headline objects: Usage Entitlement Account, Bucket, and Entry on the entitlement side; Transaction Usage Entitlement governing how the grant behaves; Asset Rate Card Entry and Asset Rate Adjustment on the rating side. The system creates these records automatically when a usage-based order activates. Binding determines what a bucket can draw from — the `GrantBindingTargetId` on Transaction Usage Entitlement and Usage Entitlement Account points at an account, an anchor asset, a contract, or a custom object, governed by a Usage Product Grant Binding Policy.

## Resources

- [*Salesforce Help:* Manage and Track Usage-Based Products in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management.htm&type=5)
- [*Salesforce Help:* Consumption Management Records](https://help.salesforce.com/s/articleView?id=ind.um_key_objects_in_consumption_management.htm&type=5)
- [*Salesforce Help:* Buckets and Drawdowns](https://help.salesforce.com/s/articleView?id=ind.um_buckets_and_drawdowns.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Describe the key objects in the usage data model.** | A customer consumes 200 GB of data from a usage-based plan. Which object records that debit transaction? | Usage Entitlement Account / Usage Entitlement Bucket / **Usage Entitlement Entry** / Transaction Usage Entitlement |
| **Describe the binding mechanism.** | A customer has a base plan (anchor) and three add-on capacity packs. They want all four products to draw from one shared pool of units. What binding target supports this pattern? | Account / **Anchor Asset** / Contract / Custom Object |

---

# Unit 2: Navigate the Usage Rating Pipeline

## Learning Objectives

After completing this unit, you'll be able to:

- Identify the required fields on a usage record entering the Transaction Journal.
- Map the flow of usage data through the rating pipeline.
- Describe how a Rating Procedure executes against a Usage Summary to produce a net rate.

> **Note on mediation:** The body section "Mediation is Customer-Side" remains in this unit to mark the boundary clearly for sellers in technical evals — but per Mike's direction, mediation no longer carries a dedicated learning objective. Module 3 doesn't list a learning outcome for something the system explicitly doesn't do; the body callout handles the framing.

Unit 1 set up the data model. Unit 2 follows the data through the rating pipeline that turns raw usage records into invoice-ready summaries. The pipeline runs as a set of scheduled flows. Each stage produces a summary record. Each summary has a defined role.

## Identify the Required Fields on a Usage Record

Before the pipeline can do anything, your usage records have to arrive in the Transaction Journal in the right shape. Each record requires nine fields:

- **Account** — the customer account the usage event applies to.
- **Activity Date** — when the consumption was recorded.
- **Status** — the processing status of the record (typically *New* on ingestion).
- **Quantity** — how many units were consumed.
- **Start Date** — when the consumption window begins.
- **End Date** — when the consumption window ends.
- **Reference Record** — the source asset, subscription, or external object the usage rolls up against.
- **Usage Resource** — the resource the consumption depletes (data, minutes, API calls, etc.).
- **Quantity Unit** — the unit the quantity is measured in (GB, minutes, calls, etc.).

Records missing any of these don't flow through the pipeline. The customer's data engineering team (or whatever system feeds usage events) owns getting these nine fields right at ingestion time.

## Map the Pipeline

Usage data moves through four records as it gets rated and prepared for billing:

1. **Transaction Journal** — the raw usage event. One row per consumption record from the source system.
2. **Usage Summary** — rolls up many Transaction Journal records into a single Usage Summary per summarization period (Daily, Monthly).
3. **Usage Ratable Summary** — the rated version of a Usage Summary. The rating engine applies the appropriate Asset Rate Card Entry and any Asset Rate Adjustments to calculate the net unit rate and the total chargeable amount.
4. **Liable Summary** — the invoice-ready summary. Captures what Billing should actually charge for the period. The Liable Summary is what flows into the billing schedule for invoice generation.

The pipeline runs as schedule-triggered flows under the **Orchestrate Usage Management** flow with its subflows. The admin doesn't write the orchestration manually — they configure *when it runs*. The **Rating Frequency Policy** sets the cadence (monthly or daily, matched to the customer's billing cycle), and the admin can also trigger the flow on demand at any time.

## Describe How Rating Procedures Calculate the Net Rate

A **Rating Procedure** is the ordered stack of rules that turns a Usage Summary into a Usage Ratable Summary. Each procedure is a sequence of **rating elements**, and each element performs one lookup or calculation against the rate context.

Procedures are fully configurable by the user. Here's how the standard procedure executes on a single Usage Summary:

1. The procedure receives the Usage Summary along with the rate context — the customer's **Asset Rate Card Entry** and any applicable **Asset Rate Adjustments**.
2. The first rating element looks up the base rate from the Asset Rate Card Entry. This is the per-unit price the customer agreed to.
3. The next element applies any Asset Rate Adjustments — tiered pricing, volume discounts, time-of-day modifiers, anything contracted on the deal.
4. Each subsequent element refines the rate by consulting the lookup table the element is bound to.
5. The final element emits the **net rate** — the per-unit price after all adjustments — and multiplies by the consumed quantity to produce the chargeable amount.

The result lands on the Usage Ratable Summary as the rated equivalent of the input Usage Summary. The Rating Procedure itself is implemented as `ExpressionSetDefinition` metadata, designed in the Expression Set Definition designer. When an admin looks in the standard object browser for a "Rating Procedure" object, they won't find one — the artifact is metadata, not data.

## Mediation is Customer-Side

Many usage-based products generate raw events that need to be cleaned, normalized, and validated before they can be rated. That process is called **mediation**. Mediation is not part of Revenue Cloud Billing. It's the customer's data engineering responsibility. Revenue Cloud Billing expects clean, normalized usage records to arrive in the Transaction Journal — what happens upstream of the Journal is outside Billing's scope.

The distinction matters during scoping conversations. If a prospect describes a billing problem that's actually a mediation problem (duplicate events, missing fields, raw events in vendor-specific formats), the answer is a data pipeline upstream of Revenue Cloud, not a Revenue Cloud feature.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a customer asks "what about late-arriving usage?" the answer is the rating pipeline handles it because the Transaction Journal accepts records with past timestamps. The pipeline rates them against the contract that was in effect at that timestamp. This is a non-trivial differentiator against batch billing systems that drop late events on the floor. |

## Key Takeaways

Raw usage records enter the Transaction Journal with nine required fields. The Orchestrate Usage Management flow drives the four-step pipeline — Transaction Journal → Usage Summary → Usage Ratable Summary → Liable Summary — on the cadence set by the Rating Frequency Policy. A Rating Procedure is an ordered stack of rating elements (implemented as Expression Set Definition metadata) that consumes Asset Rate Card Entries and Asset Rate Adjustments, evaluates them in sequence, and emits the net rate that lands on the Usage Ratable Summary. Mediation — cleaning and normalizing raw usage data — happens upstream of the Transaction Journal and is the customer's responsibility.

## Resources

- [*Salesforce Help:* Consumption Management Lifecycle](https://help.salesforce.com/s/articleView?id=ind.um_cnsption_mngmnt_lifecycle.htm&type=5)
- [*Salesforce Help:* Rating Procedures](https://help.salesforce.com/s/articleView?id=ind.rm_rating_procedures.htm&type=5)
- [*Salesforce Help:* Configure Rate Pricing Calculations in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.rm_rate_management.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Describe how a Rating Procedure executes.** | A Rating Procedure receives a Usage Summary along with the customer's Asset Rate Card Entry and Asset Rate Adjustments. Which record does the procedure produce as it emits the net rate? | Usage Summary / **Usage Ratable Summary** / Liable Summary / Transaction Usage Entitlement |
| **Recognize where mediation happens.** | A customer's vendor sends usage events with duplicate IDs and inconsistent timestamps. Where does the cleanup happen? | In the Transaction Journal automatically / **Upstream of Revenue Cloud Billing, in the customer's data pipeline** / In the Rating Procedure / In the Liable Summary |

---

# Unit 3: Apply the Consumption Management Subagent and Drawdown Policies

## Learning Objectives

After completing this unit, you'll be able to:

- Apply the usage-management subagent to derive overage consumption insights and remediate them with generated quotes.
- Apply Drawdown Policies and Rollover Policies to govern how usage entitlement buckets are consumed and renewed.
- Use the Unified Usage Dashboard to consolidate wallet balances, rates, grants, and policies into a single source of truth.
- Extend rating with third-party engines for high-volume scenarios.

> **Agent naming note:** The body content below refers to the **Subagent: Consumption Management** (per the current Help portal naming under "Agentforce for Revenue Management"). Pending an Annie + Mike alignment on subagent vs. "Billing Agent" vocabulary, names may be revised. Content stays the same.

The first two units explained what gets created and how it flows through the pipeline. Unit 3 turns to the daily operating experience — how the system applies grants when usage arrives, how the AI agent surfaces overage insights, and where to reach for help on extreme volumes.

## Use the Consumption Management Subagent

The **Subagent: Consumption Management** is one of the seven subagents that make up the **Agentforce for Revenue Management** agent suite. Its scope is intentionally narrow: it gets consumption details for accounts that have resource overages, and it generates quotes to remediate those overages. The API name is `ConsumptionManagement`, and the agent runs the `Get Usage Details` action under the hood.

The seller-facing benefit is conversational access to overage information without navigating the data model. A finance user can ask "How many assets from Acme are with overages?" or "What is the current consumption on my account?" and get a clear answer plus an offered remediation quote. The agent is available to authenticated users in Lightning Experience and requires the Agentforce Revenue Management Advanced license with the Agentforce Employee Agent add-on.

The agent works alongside two other features that together form the complete overage story:

- **Usage Overage Policy** — the governance object. Defines whether overage on a usage resource is chargeable. Admins create one policy per resource.
- **Unified Usage Dashboard** — the monitoring surface. Shows the resources accessible to the customer, how much is included, how much is left, and the drill-down into the actual debits and credits per resource.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** A common technical-eval question: "How does the system tell us about overages before they become a customer support escalation?" Answer in three layers: (1) Usage Overage Policy defines what counts as chargeable overage. (2) the Unified Usage Dashboard surfaces the current state for both seller and customer. (3) Subagent: Consumption Management proactively offers a remediation quote when consumption is trending past the grant. Each layer is a distinct product capability, and customers can buy them as a stack. |

## Apply Drawdown Policies and Rollover Policies

You might think that the rating story resets each billing period — that's not the case. As you would expect, the grant of new usage resource capacity and the rollover of remaining resources from one period to the next happen automatically. Two policy types govern this behavior, both attached to the **Transaction Usage Entitlement** record at order activation and applied automatically by Consumption Management.

**Drawdown Policy** controls which **grant** gets debited when a customer consumes a resource that has multiple grants available. When a customer has both a base plan and add-on packs, Consumption Management chooses among the active grants based on the **Drawdown Order** field on the associated **Product Usage Grant** record. The field has three values:

- **Expiring First** — draws from the grant closest to its expiration date. This is the default value.
- **Granted First** — draws from the oldest grant, based on the earliest start date.
- **Granted Last** — draws from the newest grant, based on the most recent start date.

**Rollover Policy** controls what happens to unused units when a billing period ends. Some customers carry unused units forward into the next period (the units roll over). Others reset to zero each period (the units expire). The rollover policy on the Transaction Usage Entitlement record sets this behavior at the per-grant level, so the same customer can have different rollover rules for different resources — usage minutes might roll, data overage might reset.

The Bucket itself tracks two complementary balances: an **overall balance** (everything available to the customer for that resource across the binding target) and an **in-period balance** (what's available for the current billing period). Grant actions — a new purchase, a renewal, a refresh, a rollover, or an amendment — appear as **Usage Entitlement Entries** in the bucket, crediting the balances when capacity arrives and debiting them when the customer consumes. The Drawdown Policy chooses which grant entry to debit when more than one is available.

Together, Drawdown and Rollover answer two distinct customer questions:

- *"When I consume a unit, which grant gets debited first?"* — Drawdown Policy.
- *"When my billing period ends, do unused units carry forward?"* — Rollover Policy.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Drawdown and Rollover are how you answer two adjacent customer questions in one motion. Drawdown is FIFO-vs-LIFO for a given consumption event — Expiring First (the default) uses the grant closest to expiration first. Rollover is what happens at period end — units carry forward or expire. Lead with Expiring First as the default and Rollover Policy as the period-end answer; most customers don't need to think about either after the initial configuration. |

## Use the Unified Usage Dashboard

The **Unified Usage Dashboard** is the seller-and-customer-facing surface for consumption. It shows the resources accessible to the customer, how much is included, how much is left, and lets the customer drill into each resource to see the actual debits and credits being made. The dashboard runs from the Usage Management App and exposes its content through tabs accessible from either an account page or an asset page:

- **Usage Details** — lists all assets bound to the account, including assets, contracts, or custom objects.
- **Grants** — shows the associated grants with rollover and refresh policy details and effective period dates.
- **Policies** — centralized list of the governing policies for each usage resource, including aggregation policies, rating frequency policies, and overage policies.
- **Wallets** — shows balances per resource with visual indicators for percentage consumed. Drilling into a resource exposes the bucket's overall and in-period balances and the audit trail of Usage Entitlement Entries (the Wallet Statement).
- **Rates** — shows the finalized winning rate for any consumption on the account or asset. The proration engine evaluates overlapping validity periods and shows the rate the rating engine actually uses.

The Wallet view also extends to Experience Cloud, so customers can track their own balances, usage, and entitlements without opening a support case. The Wallet view requires Customer Community or Partner Community licenses.

## Extend Rating for High-Volume Scenarios

The native Consumption Management capability handles most usage-based product patterns. For genuinely extreme volumes — billions of records, multi-attribute pricing, near-real-time rating — Salesforce has a strategic ISV partnership with **m3ter** to complement the native engine. When a prospect describes consumption at that scale, m3ter is the recommended partner integration.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** The m3ter partnership is the answer to the "we have a billion events per month" question. Don't try to position the native engine for that volume — pull m3ter in early. Native Consumption Management is the answer for most usage-based products; m3ter is the answer when the scale crosses the line into specialist territory. Knowing the threshold matters in technical evals. |

## Key Takeaways

The Subagent: Consumption Management under Agentforce for Revenue Management surfaces overage insights and offers remediation quotes through a conversational interface. It works alongside the Usage Overage Policy (governance) and the Unified Usage Dashboard (monitoring surface) to form the complete overage story. The **Drawdown Order** field on Product Usage Grant — with values Expiring First (default), Granted First, and Granted Last — determines which grant the system debits when multiple grants exist for the same resource. The **Rollover Policy** on Transaction Usage Entitlement decides whether unused units carry into the next billing period or expire. The Unified Usage Dashboard consolidates wallet balances, rates, grants, and policies into one source of truth, available to internal users in Lightning Experience and to customers in Experience Cloud. For extreme-volume scenarios, the m3ter ISV partnership extends the native rating capability.

## Resources

- [*Salesforce Help:* Subagent: Consumption Management](https://help.salesforce.com/s/articleView?id=ind.rev_agent_usage_topic_consumption_management.htm&type=5)
- [*Salesforce Help:* Buckets and Drawdowns](https://help.salesforce.com/s/articleView?id=ind.um_buckets_and_drawdowns.htm&type=5)
- [*Salesforce Help:* Unified Usage Dashboard](https://help.salesforce.com/s/articleView?id=ind.um_wallet_management.htm&type=5)
- [*Salesforce Help:* Create a Usage Overage Policy](https://help.salesforce.com/s/articleView?id=ind.um_create_usage_overage_policy.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Describe the Subagent: Consumption Management.** | A finance user asks the Subagent: Consumption Management "How many assets from Acme are with overages?" Which two capabilities does the subagent provide? | Get consumption details only / Generate quotes only / **Get consumption details AND generate remediation quotes for resources with overages** / Configure Usage Overage Policies |
| **Describe Drawdown Policies.** | A customer has three active grants for the same resource — one expiring in 30 days, one expiring in 60 days, and one expiring in 90 days. With the default Drawdown Order, which grant does Consumption Management debit first? | The 90-day grant / The 60-day grant / **The 30-day grant (Expiring First — the default)** / All three equally |

---

# Appendix: Open Questions and Parking Lot

## Open question for Mike

**Wallet Management as a standalone LO.** The Help portal documents Wallet Management as a sub-pillar of Usage Management with its own dedicated Help area (the Unified Usage Dashboard). This v2 draft folds it into Unit 3 as a body section under the umbrella LO 3.3. If Mike wants Wallet Management to land as its own LO (call it 3.4) — separating "consolidated view + Experience Cloud surface" from "Drawdown Policies + Consumption Management subagent" — it's a one-paragraph split. Mike, your call.

## Topics deliberately routed elsewhere

For audit completeness:

- **Pure Consumption vs. Hybrid revenue models.** v1 had this as an LO. Mike's direction: ambient context, not a learning outcome. The Hybrid / Pure framing can appear in prose without becoming an LO.
- **Configure Digital Wallets.** v1 had this. Mike: "You don't configure these, they create automatically." Reframed as the wallet metaphor in Unit 1 (Bucket = wallet) and the Wallet view in Unit 3 (the consolidated UI surface), not as a configuration LO.

## Cross-module observations

The Subagent: Consumption Management referenced in Unit 3 LO 3.1 is one of seven subagents in the **Agentforce for Revenue Management** suite. The other six surface in Modules 1, 4, and 5 — Subagent: Invoice Line Explanation and Subagent: Billing Inquiries (Module 1 v2 + Module 4), Subagent: Billing Collections Management (Module 5), Subagent: Product Selection and Subagent: Product Description Generation (PCM, not in this L2 mix), and Subagent: Quote Management (Transaction Management, not in this L2 mix). Keeping the subagent naming consistent across Modules 1, 3, 4, and 5 is important for learner coherence.

---

*Prepared by Brian Galdino with AI assistance; grounded against the latest Salesforce Help portal (Usage Management area, Rate Management area, Agentforce for Revenue Management area). Per-claim citation log: `docs/trailhead-l2-review/module-3-262-lo-validation-report.md`. The Trailhead-facing draft deliberately avoids release-version notations to stay evergreen.*
