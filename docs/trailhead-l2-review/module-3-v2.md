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

- Describe the key objects in the usage data model: **Transaction Usage Entitlement**, **Asset Rate Card Entry**, **Asset Rate Adjustment**, **Usage Entitlement Account**, **Usage Entitlement Bucket**, and **Usage Entitlement Entry**.
- Explain how these objects are populated at Order Product activation for usage-based products.
- Describe the binding mechanism that determines what a Usage Entitlement Bucket can draw from.

In Modules 1 and 2, you saw the core billing data model — Order, Billing Schedule Group, Billing Schedule, Invoice. Module 3 extends that model to handle a different revenue pattern: consumption-based products, where a customer pays based on what they use rather than a fixed subscription. Usage Management is the part of Agentforce Revenue Management that defines, rates, tracks, and bills these products. Before any of that machinery can run, the right records have to exist in the right shape. Unit 1 lays out those records.

| Note | Content |
|:-:|:-:|
| icon=true | **What's in a Name?** Usage Management is the umbrella area. **Consumption Management** is a sub-pillar within it — specifically the lifecycle that tracks consumption data and generates invoice-ready summaries. Both terms appear in Help docs, so it's worth knowing the relationship. |

## Define the Usage Data Model Objects

Six objects do most of the work in the usage data model. Three sit on the entitlement side, two sit on the rating side, and one binds the customer's entitlements to the products they purchased.

- **Usage Entitlement Account (UEA)** — the customer instance of a purchased usage product. Carries billing cycle details: billing frequency, billing day of month, start and end dates, the service. Created automatically after an order is activated and assetized.
- **Usage Entitlement Bucket** — a wallet that records credits and debits of a usage resource. When grants are rolled over or renewed, units are added to the bucket balance. When the customer consumes the usage resource, units are debited from the bucket balance. A UEA has one or more buckets, one per usage resource.
- **Usage Entitlement Entry** — the per-transaction record that captures each credit or debit entry for a bucket. Together, the Entries form the audit trail for what flowed in and out of the bucket.
- **Transaction Usage Entitlement (TUE)** — stores information about how grants are tracked and managed for a usage resource. Includes the associated usage grant rollover policy, usage grant refresh policy, drawdown order in which grant consumption is debited, and the binding target for the entitlement.
- **Asset Rate Card Entry** — the customer-specific rate for a usage resource on a particular asset. Rate Cards define list rates at the catalog level; Asset Rate Card Entries are the actual negotiated rates on the deal.
- **Asset Rate Adjustment** — tiered or banded adjustments layered on top of an Asset Rate Card Entry. Used for volume discounts, time-of-day pricing, or other consumption-driven adjustments.

A useful one-liner: **UEA holds the relationship. Buckets hold the balance. Entries are the audit trail. TUE governs how the grant behaves. Asset Rate Card Entry and Asset Rate Adjustment determine the rate.**

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Customers often try to skip past the data model in technical evals because the object names feel abstract. Anchor them to the wallet metaphor: the UEA is the customer's "wallet account," each bucket is a sub-wallet for one resource, each entry is a transaction line in that sub-wallet. When you frame it as a wallet rather than a schema, finance buyers see the model the way they see their own bank statements. |

## How Records Are Populated at Order Activation

The customer doesn't create most of these records manually. The system creates them as a side effect of order activation. The sequence is:

1. The seller adds a usage-based product to a quote or order. The order is activated.
2. The system **assetizes** the order — creates an Asset record for each Order Product.
3. For each usage-based Asset, the system creates a **Usage Entitlement Account** and the related **Usage Entitlement Buckets** for each resource the product grants.
4. The system creates the **Transaction Usage Entitlement** record that captures the binding policy, rollover policy, refresh policy, and drawdown order for the granted resources.
5. **Asset Rate Card Entries** and **Asset Rate Adjustments** are populated based on what was negotiated during the quote step.

The admin doesn't configure individual buckets per customer — they configure the rules, and the system creates the records when an order activates. This is one of the most important seller proof points for usage-based selling: there's no manual data entry between deal close and bill ready.

## Understand the Binding Mechanism

Binding is how usage products pool their resources together. A Transaction Usage Entitlement has a `GrantBindingTargetId` field that points at the target that owns the grant. A Usage Entitlement Account also has its own `GrantBindingTargetId`. The Bucket inherits its binding through `ParentId`.

The binding target can be one of four things:

- **An Account** — the grant is shared across every relevant asset the account owns. Buy a corporate-wide quota and every business unit draws from the same pool.
- **An Anchor Asset** — the grant is specific to a base product (the "anchor"). Add-on packs that bind to the anchor draw from the same pool.
- **A Contract** — the grant is scoped to a specific contract. Useful when one account has multiple contracts and each carries its own pool.
- **A Custom Object** — for scenarios that don't fit the above three patterns.

The `UsagePrdGrantBindingPolicy` object holds the policy itself — admins create binding policies once and apply them to multiple usage products. When the system creates a Transaction Usage Entitlement at order activation, it consults the binding policy to determine which target ID to write to `GrantBindingTargetId`.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Binding is what separates "a customer with multiple SKUs" from "a customer with a pooled allowance." When a prospect tells you they have a base subscription with add-on capacity packs, that's an Anchor Asset binding pattern. The base product is the Anchor. The packs bind to it. They all share one parent Usage Entitlement Bucket. This is a recurring pattern in telecom, infrastructure, and platform pricing. |

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
- Map the flow of usage data through the rating pipeline: Transaction Journal → **Usage Summary** → **Usage Ratable Summary** → **Liable Summary**.
- Describe how **Rating Procedures** (Default Rating Procedure or Negotiable Rating Procedure) and **Rating Discovery Procedures** consume Asset Rate Card Entries and Asset Rate Adjustments to produce Usage Ratable Summaries.
- Recognize that mediation — cleaning and normalizing raw usage data — is customer-side responsibility, not part of Revenue Cloud Billing.

Unit 1 set up the data model. Unit 2 follows the data through the rating pipeline that turns raw usage records into invoice-ready summaries. The pipeline runs as a set of scheduled flows. Each stage produces a summary record. Each summary has a defined role.

## Identify the Required Fields on a Usage Record

Before the pipeline can do anything, your usage records have to arrive in the Transaction Journal in the right shape. Each record requires five fields:

- **External ID** — a unique identifier for the usage event from the source system.
- **Timestamp** — when the consumption happened.
- **Quantity** — how many units were consumed.
- **Unit of Measure** — what the quantity represents (GB, API calls, minutes, etc.).
- **Matching Attribute** — the value the rating engine uses to identify which usage resource the record applies to.

Records missing any of these don't flow through the pipeline. The customer's data engineering team (or whatever system feeds usage events) owns getting these five fields right at ingestion time.

## Map the Pipeline

Usage data moves through four records as it gets rated and prepared for billing:

1. **Transaction Journal** — the raw usage event. One row per consumption record from the source system.
2. **Usage Summary** — the aggregated usage for a billing period or service period. Rolls up many Transaction Journal records into a single summary per resource per period.
3. **Usage Ratable Summary** — the rated version of a Usage Summary. The rating engine applies the appropriate Asset Rate Card Entry and any Asset Rate Adjustments to calculate the net unit rate and the total chargeable amount.
4. **Liable Summary** — the invoice-ready summary. Captures what Billing should actually charge for the period. The Liable Summary is what flows into the billing schedule for invoice generation.

The pipeline runs as schedule-triggered flows under the **Orchestrate Usage Management** flow with its subflows. The admin doesn't write the orchestration manually. The admin schedules the flow to run on the cadence the customer's billing cycle requires.

## Describe Rating Procedures and Rating Discovery Procedures

Two distinct procedure concepts drive the rating step:

- **Rating Procedures** — customizable, ordered stacks of rating elements that calculate the final net rate of a usage resource. Each rating element is a step in the procedure. The Help docs describe two procedure types: a **Default Rating Procedure** for straightforward volume-based pricing, and a **Negotiable Rating Procedure** for complex, usage-driven negotiations. The procedure consumes Asset Rate Card Entries and Asset Rate Adjustments to produce a Usage Ratable Summary.
- **Rating Discovery Procedures** — a separate, complementary concept. Their job is to fetch the binding objects, rate cards, rate card entries, and rate adjustments for sellable products. The Quote and Order Capture experience uses them at quote time to provide upfront visibility of rating details to the seller, and the Asset Lifecycle uses them at amendment time.

Both procedure types are implemented as `ExpressionSetDefinition` metadata. That's a useful detail for developers and admins to know — when they look in the standard object browser for a "Rating Procedure" object, they won't find one. The artifact lives in metadata, accessed through the Expression Set Definition designer.

## Mediation is Customer-Side

Many usage-based products generate raw events that need to be cleaned, normalized, and validated before they can be rated. That process is called **mediation**. Mediation is not part of Revenue Cloud Billing. It's the customer's data engineering responsibility. Revenue Cloud Billing expects clean, normalized usage records to arrive in the Transaction Journal — what happens upstream of the Journal is outside Billing's scope.

The distinction matters during scoping conversations. If a prospect describes a billing problem that's actually a mediation problem (duplicate events, missing fields, raw events in vendor-specific formats), the answer is a data pipeline upstream of Revenue Cloud, not a Revenue Cloud feature.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** When a customer asks "what about late-arriving usage?" the answer is the rating pipeline handles it because the Transaction Journal accepts records with past timestamps. The pipeline rates them against the contract that was in effect at that timestamp. This is a non-trivial differentiator against batch billing systems that drop late events on the floor. |

## Key Takeaways

Raw usage records enter the Transaction Journal with five required fields. The Orchestrate Usage Management flow drives the four-step pipeline: Transaction Journal → Usage Summary → Usage Ratable Summary → Liable Summary. Rating Procedures (Default or Negotiable, both implemented as Expression Set Definition metadata) consume Asset Rate Card Entries and Asset Rate Adjustments to produce Usage Ratable Summaries. Rating Discovery Procedures fetch the rate context that the Quote and Order Capture experience needs at quote time. Mediation — cleaning and normalizing raw usage data — happens upstream of the Transaction Journal and is the customer's responsibility.

## Resources

- [*Salesforce Help:* Consumption Management Lifecycle](https://help.salesforce.com/s/articleView?id=ind.um_cnsption_mngmnt_lifecycle.htm&type=5)
- [*Salesforce Help:* Rating Procedures](https://help.salesforce.com/s/articleView?id=ind.rm_rating_procedures.htm&type=5)
- [*Salesforce Help:* Configure Rate Pricing Calculations in Agentforce Revenue Management](https://help.salesforce.com/s/articleView?id=ind.rm_rate_management.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Map the flow of usage data through the rating pipeline.** | A usage record enters the Transaction Journal. Which summary does the rating engine produce by applying Asset Rate Card Entries and Asset Rate Adjustments? | Usage Summary / **Usage Ratable Summary** / Liable Summary / Transaction Usage Entitlement |
| **Recognize where mediation happens.** | A customer's vendor sends usage events with duplicate IDs and inconsistent timestamps. Where does the cleanup happen? | In the Transaction Journal automatically / **Upstream of Revenue Cloud Billing, in the customer's data pipeline** / In the Rating Procedure / In the Liable Summary |

---

# Unit 3: Apply the Consumption Management Subagent and Drawdown Policies

## Learning Objectives

After completing this unit, you'll be able to:

- Describe the **Subagent: Consumption Management** (under the **Agentforce for Revenue Management** agent suite) and its role in deriving overage consumption insights and generating remediation quotes.
- Describe the three Drawdown Policies (Expiring First, Granted First, Granted Last) and how Consumption Management applies them automatically to multiple Usage Entitlement Buckets.
- Describe how the **Unified Usage Dashboard** consolidates wallet balances, rates, grants, and policies into a single source of truth.
- Describe how to extend rating for high-volume scenarios using the m3ter ISV partnership.

The first two units explained what gets created and how it flows through the pipeline. Unit 3 turns to the daily operating experience — how the system applies grants when usage arrives, how the AI agent surfaces overage insights, and where to reach for help on extreme volumes.

## Use the Consumption Management Subagent

The **Subagent: Consumption Management** is one of the seven subagents that make up the **Agentforce for Revenue Management** agent suite. Its scope is intentionally narrow: it gets consumption details for accounts that have resource overages, and it generates quotes to remediate those overages. The API name is `ConsumptionManagement`, and the agent runs the `Get Usage Details` action under the hood.

The seller-facing benefit is conversational access to overage information without navigating the data model. A finance user can ask "How many assets from Acme are with overages?" or "What is the current consumption on my account?" and get a clear answer plus an offered remediation quote. The agent is available to authenticated users in Lightning Experience and requires the Agentforce Revenue Management Advanced license with the Agentforce Employee Agent add-on.

The agent works alongside two other 262 features that together form the complete overage story:

- **Usage Overage Policy** — the governance object. Defines whether overage on a usage resource is chargeable. Admins create one policy per resource.
- **Unified Usage Dashboard** — the monitoring surface. Tracks wallet balances, rates, grants, and policies in a consolidated view.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** A common technical-eval question: "How does the system tell us about overages before they become a customer support escalation?" Answer in three layers: (1) Usage Overage Policy defines what counts as chargeable overage. (2) Unified Usage Dashboard surfaces the current state. (3) Subagent: Consumption Management proactively offers a remediation quote when consumption is trending past the grant. Each layer is a distinct product capability, and customers can buy them as a stack. |

## Apply Drawdown Policies to Multiple Buckets

When a customer has multiple Usage Entitlement Buckets for the same resource — typically because they have a base plan plus add-on packs — Consumption Management has to decide which bucket to deduct from first. The **Drawdown Order** field on the associated **Product Usage Grant** record controls that decision. The field has three values:

- **Expiring First** — draws from the bucket closest to its expiration date. This is the default value.
- **Granted First** — draws from the oldest bucket, based on the earliest start date.
- **Granted Last** — draws from the newest bucket, based on the most recent start date.

These policies apply automatically. The customer doesn't configure them per bucket — they're applied based on the Product Usage Grant configuration the admin set up when defining the grant.

The Bucket structure that the drawdown policy navigates is itself a parent-child hierarchy. The **parent bucket** represents the combined total balance of a specific resource across the binding target. **Child buckets** represent the actual specific grants tied to individual grant actions — a new purchase, a grant renewal, a grant refresh, a grant rollover, or an amendment. The drawdown policy chooses among the child buckets when there's more than one option.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** Drawdown Policies are how you answer the customer question "what's the FIFO vs LIFO rule for our grants?" Expiring First is the default and the most customer-friendly — units that would otherwise expire get used first. Granted First and Granted Last are available for customers who want different accounting behavior. Mention the default explicitly: most customers don't need to think about this at all. |

## Use the Unified Usage Dashboard

The **Unified Usage Dashboard** is the seller-and-customer-facing surface that consolidates everything the pipeline produces. The dashboard runs from the Usage Management App and exposes four tabs from either an account page or an asset page:

- **Usage Details** — lists all assets bound to the account, including assets, contracts, or custom objects.
- **Grants** — shows the associated grants with rollover and refresh policy details and effective period dates.
- **Policies** — centralized list of the governing policies for each usage resource, including aggregation policies, rating frequency policies, and overage policies.
- **Wallets** — shows the digital wallets that represent parent buckets, with visual indicators for percentage consumed. Drilling into a wallet exposes the child buckets, the bucket balance, and the audit trail of credits and debits (Wallet Statement).
- **Rates** — shows the finalized winning rate for any consumption on the account or asset. The proration engine evaluates overlapping validity periods and shows the rate the rating engine actually uses.

The Wallet view also extends to Experience Cloud, so customers can track their own balances, usage, and entitlements without opening a support case. The Wallet view requires Customer Community or Partner Community licenses.

## Extend Rating for High-Volume Scenarios

The native Consumption Management capability handles most usage-based product patterns. For genuinely extreme volumes — billions of records, multi-attribute pricing, near-real-time rating — Salesforce has a strategic ISV partnership with **m3ter** to complement the native engine. When a prospect describes consumption at that scale, m3ter is the recommended partner integration.

| Note | Content |
|:-:|:-:|
| icon=true | **Seller Sidebar** The m3ter partnership is the answer to the "we have a billion events per month" question. Don't try to position the native engine for that volume — pull m3ter in early. Native Consumption Management is the answer for most usage-based products; m3ter is the answer when the scale crosses the line into specialist territory. Knowing the threshold matters in technical evals. |

## Key Takeaways

The Subagent: Consumption Management under Agentforce for Revenue Management surfaces overage insights and offers remediation quotes through a conversational interface. It works alongside the Usage Overage Policy (governance) and the Unified Usage Dashboard (monitoring surface) to form the complete overage story. The Drawdown Order field on Product Usage Grant — with values Expiring First (default), Granted First, and Granted Last — determines which child bucket the system debits when multiple buckets exist for the same resource. The Unified Usage Dashboard consolidates wallets, rates, grants, and policies into one source of truth, available to internal users in Lightning Experience and to customers in Experience Cloud. For extreme-volume scenarios, the m3ter ISV partnership extends the native rating capability.

## Resources

- [*Salesforce Help:* Subagent: Consumption Management](https://help.salesforce.com/s/articleView?id=ind.rev_agent_usage_topic_consumption_management.htm&type=5)
- [*Salesforce Help:* Buckets and Drawdowns](https://help.salesforce.com/s/articleView?id=ind.um_buckets_and_drawdowns.htm&type=5)
- [*Salesforce Help:* Unified Usage Dashboard](https://help.salesforce.com/s/articleView?id=ind.um_wallet_management.htm&type=5)
- [*Salesforce Help:* Create a Usage Overage Policy](https://help.salesforce.com/s/articleView?id=ind.um_create_usage_overage_policy.htm&type=5)

## Quiz

| Learning Objective | Question | Answers (correct answer underlined) |
|:--|:--|:--|
| **Describe the Subagent: Consumption Management.** | A finance user asks the Subagent: Consumption Management "How many assets from Acme are with overages?" Which two capabilities does the subagent provide? | Get consumption details only / Generate quotes only / **Get consumption details AND generate remediation quotes for resources with overages** / Configure Usage Overage Policies |
| **Describe Drawdown Policies.** | A customer has three Usage Entitlement Buckets for the same resource — one expiring in 30 days, one expiring in 60 days, and one expiring in 90 days. With the default Drawdown Order, which bucket does Consumption Management debit first? | The 90-day bucket / The 60-day bucket / **The 30-day bucket (Expiring First — the default)** / All three equally |

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
