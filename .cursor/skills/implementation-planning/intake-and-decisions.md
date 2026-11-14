# Intake and Decision Log

Read this when extracting requirements from a source document, asking the customer what
the source omits, or recording the choices a plan rests on. It points to owners; it does
not define the options. Read the linked section before choosing.

## Intake categories

For each category: extract what the source states, quote or cite where, and if the source
is silent ask the questions. Mark each item stated, inferred or missing. An answer to a
question belongs in the decision log if it chooses between options.

| Category | Ask when the source is silent | Owner |
|---|---|---|
| Catalog and bundles | What is sold as its own line, and what is a choice inside a line? Which items are only sold with another? Which bundles are fixed and which configurable? Any compatibility rules between choices? How many products, levels, and categories? | [product-catalog-modeling](../product-catalog-modeling/SKILL.md), [bundles-and-cardinality.md](../product-catalog-modeling/bundles-and-cardinality.md), [constraint-models](../constraint-models/SKILL.md) |
| Selling models and terms | How does each charge recur: once, for a fixed term, until cancelled? What terms and term units? Is proration wanted? Auto-renew or manual? | [selling-models-and-lifecycle.md](../product-catalog-modeling/selling-models-and-lifecycle.md#choose-the-selling-model-from-the-pricing-basis), [proration-and-selling-models.md](../pricing-setup/proration-and-selling-models.md) |
| Pricing and discounts | What is the price basis (list, tiered, per attribute, per bundle, cost-plus)? Do prices differ by segment, region or currency? Who may discount, how much, and on the header or on lines? Are there promotions? Do prices change over a term? | [pricing-setup](../pricing-setup/SKILL.md), [pricing-procedures](../pricing-procedures/SKILL.md), [price-adjustment-schedules.md](../pricing-setup/price-adjustment-schedules.md), [price-revision-policies.md](../pricing-setup/price-revision-policies.md) |
| Usage and rating | What is metered, in what unit, and from which source? How often is usage rated and billed? Are there commitments, prepaid packs, tiers or overage, and how do they interact? What happens to unused commitment? | [usage-consumption](../usage-consumption/SKILL.md), [usage domain objects](../revenue-cloud-data-model/domains/usage.md) |
| Approvals | Who approves what, by which criteria (amount, discount, term, product)? Serial or parallel? Do levels accumulate? Does an approver delegate, and can the submitter recall? Who is notified? | [advanced-approvals](../advanced-approvals/SKILL.md), [matrix-modeling.md](../advanced-approvals/matrix-modeling.md) |
| Quoting rounds | Are there several priced versions of one deal? Is one internal-only? Which round becomes the order? Does each round need approval? | [quote-negotiation-rounds](../quote-negotiation-rounds/SKILL.md) |
| Multi-year and ramps | Does price change by period within one deal? By fixed step, percentage or negotiated amount? Is the ramp per line or per group of lines? How does a ramped deal renew? | [ramped-quotes](../ramped-quotes/SKILL.md), [Ramps](../product-catalog-modeling/selling-models-and-lifecycle.md#ramps) |
| Ordering and fulfillment | What happens after an order is placed? Which items need provisioning, shipment, installation or a manual task? In what order and with what dependencies? What marks each item complete? Does completion trigger anything else? | [dro-plans](../dro-plans/SKILL.md), [authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md) |
| Assets and lifecycle changes | What must be tracked after the sale? Which changes are allowed (add or remove quantity, swap, cancel, renew) and under what policy (co-term, credit, uplift)? Can changes be backdated? | [asset-lifecycle-changes](../asset-lifecycle-changes/SKILL.md), [Questions to settle in the plan](../asset-lifecycle-changes/change-policy-mapping.md#questions-to-settle-in-the-plan) |
| Billing and invoicing | How often is each line billed, in advance or in arrears? Are there milestones, and what triggers them? Payment terms? Invoice grouping, legal entities, tax? Credit or refund handling? | [billing-setup](../billing-setup/SKILL.md), [Billing frequency](../billing-setup/SKILL.md#billing-frequency), [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) |
| Contracts | Is a contract created, from what, and when in the flow? Which clauses and templates? Does the contract term drive the asset term or renewal? | [salesforce-contracts](../salesforce-contracts/SKILL.md) |
| Documents | Which documents are produced (quote, order form, contract, invoice) and from which record? Languages? Approval before sending? | [document-generation](../document-generation/SKILL.md), [odt-authoring](../odt-authoring/SKILL.md) |
| Data volumes, currencies, regions | How many products, accounts, lines per quote, orders and usage records per period? Which currencies and regions? Any exceptionally large transactions? Migrating existing data? | [sfdmu-data-plans](../sfdmu-data-plans/SKILL.md), [revenue-cloud-data-model](../revenue-cloud-data-model/SKILL.md), [pricing-wiring](../pricing-wiring/SKILL.md#wrong-currency-price-returned-multicurrency-orgs) |
| Users and channels | Who creates quotes (direct sales, partners, self service)? Which UI? Which integrations call the APIs? | [transaction-line-editor](../transaction-line-editor/SKILL.md), [rlm-business-apis](../rlm-business-apis/SKILL.md), [mcp-integration](../mcp-integration/SKILL.md) |
| Environments | Which orgs, release, editions? Who deploys, and how are changes promoted? | [revenue-cloud-docs](../revenue-cloud-docs/SKILL.md), [repo-integration](../repo-integration/SKILL.md) |

If the source states a requirement in another category's words (for example "bill the
install when it is done" is both fulfillment and billing), record it once and cross-link
both categories.

No skill owns tax, collections, invoice runs and payments beyond treatments, or the design
of a usage product (rating frequency, aggregation, tiers) as a decision guide. Record the
requirement, mark it open, and look in the Help snapshot through
[revenue-cloud-docs](../revenue-cloud-docs/SKILL.md).

## Decision log

Record one row per decision in the plan: id, the decision, the options considered, the
choice, why, the requirement ids it serves, who confirmed it, and what it constrains
downstream. The table lists decisions that commonly need a row and where the options are
explained. Add rows the source forces.

| Decision | Options live in | What it constrains |
|---|---|---|
| Product vs attribute vs component | [Product vs attribute vs component](../product-catalog-modeling/SKILL.md#product-vs-attribute-vs-component) | Price book entries, selling models, assets, fulfillment lines, categories |
| Simple vs bundle type (immutable once created) | [Quick Rules](../product-catalog-modeling/SKILL.md#quick-rules) | Rebuild cost if wrong |
| Static vs configurable bundle; group shape and cardinality | [bundles-and-cardinality.md](../product-catalog-modeling/bundles-and-cardinality.md) | Configurator, constraint rules, line count per bundle |
| Constraint model needed, or cardinality and classification suffice | [constraint-models](../constraint-models/SKILL.md) `[inferred]` | Authoring and deployment work |
| Selling model per charge | [selling-models-and-lifecycle.md](../product-catalog-modeling/selling-models-and-lifecycle.md#choose-the-selling-model-from-the-pricing-basis) | Price book entries, billing frequency, renewals, credits |
| Assetizable or not | [IsAssetizable](../product-catalog-modeling/selling-models-and-lifecycle.md#isassetizable) | Whether amend, renew and cancel can act on the sale |
| Sold only with another product | [IsSoldOnlyWithOtherProds](../product-catalog-modeling/selling-models-and-lifecycle.md#issoldonlywithotherprods) | Category placement, quoting |
| Tiered price on a quote line vs tiered rate on usage | [Tiers](../pricing-setup/price-adjustment-schedules.md#tiers-volume), [volume-and-tier-discount.md](../pricing-procedures/elements/volume-and-tier-discount.md); usage side not covered as a decision guide: open | Pricing procedure elements, usage records |
| Header vs line discount | [manual-discount.md](../pricing-procedures/elements/manual-discount.md), [discount-distribution-service.md](../pricing-procedures/elements/discount-distribution-service.md), [Discounts per round, per line](../quote-negotiation-rounds/SKILL.md#discounts-per-round-per-line) | Procedure layout, line editor display, approvals |
| Price changes over a term (revision policy, schedule) | [price-revision-policies.md](../pricing-setup/price-revision-policies.md), [price-adjustment-schedules.md](../pricing-setup/price-adjustment-schedules.md) | Procedure elements, renewals |
| Ramp type: line ramp, group ramp, longer term, separate renewals | [ramped-quotes](../ramped-quotes/SKILL.md), [Ramps](../product-catalog-modeling/selling-models-and-lifecycle.md#ramps) | Quote build, bundle shape, early renewal |
| Context attributes that feed pricing | [context-service](../context-service/SKILL.md), [Context Definitions and Context Plans](../pricing-wiring/SKILL.md#d-context-definitions-and-context-plans) | Fields, mappings, procedure variables |
| Approval shape: matrix levels, serial or parallel, per-round | [matrix-modeling.md](../advanced-approvals/matrix-modeling.md), [Approvals per round](../quote-negotiation-rounds/SKILL.md#approvals-per-round) | Pricing flags, flows, notifications |
| Which round becomes the order | [Final round to order](../quote-negotiation-rounds/SKILL.md#final-round-to-order) | Opportunity sync, order creation |
| Fulfillment decomposition: scope (Account, Order, Bundle, Order Line Item), quantity behavior, step scope | [Decomposed Line Items](../dro-plans/authoring-and-deployment.md#decomposed-line-items) | Fulfillment line count per order, step count |
| Fulfillment step types, dependencies, completion signal | [authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md), [updates-and-runtime.md](../dro-plans/updates-and-runtime.md) | Order completion, billing triggers |
| Billing frequency vs selling-model term | [Billing frequency](../billing-setup/SKILL.md#billing-frequency) | Billing treatment needs, line placement |
| In advance or in arrears; treatments | [Billing policies and treatments](../billing-setup/SKILL.md#billing-policies-and-treatments) | Schedules, invoices |
| One-time charge billed periodically, or in milestones | [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) | Selling model, treatment |
| Milestone trigger from fulfillment | Who or what marks an event milestone: [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) (Marking an event milestone done); the link from fulfillment is open, verify live and log the evidence | Billing schedule dates |
| Payment terms and where they live | [Payment terms](../billing-setup/SKILL.md#payment-terms) | Approvals, invoices |
| Amendment policy: co-term, credit, re-band | [change-policy-mapping.md](../asset-lifecycle-changes/change-policy-mapping.md) | Asset actions, invoice values |
| Renewal: uplift, term, quote generation | [asset-lifecycle-changes](../asset-lifecycle-changes/SKILL.md), [renewal-asset-creation](../renewal-asset-creation/SKILL.md) | Pricing, ramps |
| Usage product: commitment, pack, overage, rating frequency | [usage-consumption](../usage-consumption/SKILL.md); design guidance not written: open | Policies, assets, rating |
| Contract timing and what it drives | [salesforce-contracts](../salesforce-contracts/SKILL.md) | Terms, renewals, documents |
| Document set and engine | [document-generation](../document-generation/SKILL.md) | Templates, data mappers |
| Load mechanism: UI, API, or data plan | [sfdmu-data-plans](../sfdmu-data-plans/SKILL.md), [rlm-business-apis](../rlm-business-apis/SKILL.md) | Repeatability, idempotency |
| Currency and region handling | [pricing-wiring](../pricing-wiring/SKILL.md#wrong-currency-price-returned-multicurrency-orgs) | Price book entries, lookups |

### Row template

```
D-07  Decision:    <what is being decided>
      Options:     <A, B, C, each with the section that explains it>
      Choice:      <the choice>
      Why:         <the customer's requirement id and the rule that selects it>
      Confirmed:   <who, when> | assumption, owner <name>
      Evidence:    <Help / inferred / traced / measured / open, as the owner tags it>
      Constrains:  <downstream decisions and build items>
```

A choice whose evidence is "open" or "measured on one org" needs a verification item in the
acceptance chain.
