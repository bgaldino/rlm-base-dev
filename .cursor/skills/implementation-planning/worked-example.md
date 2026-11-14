# Worked Example: Invented Business

Read this to see intake, decisions, derived counts, ordering and the acceptance chain
applied once. The business and every value are invented for illustration. Nothing here is
a default; substitute the customer's own. Domain rules are not restated: each decision row
names the section that owns the options, and the choices are examples of recording, not
recommendations.

## The source (excerpt)

"Brightfield Water Systems sells a sensor kit (hub plus sensors) with professional
installation, a three-year monitoring subscription billed yearly, and a data feed priced by
monthly usage with a minimum monthly commitment. Regional managers approve discounts above a
threshold. Customers renew at the end of the term."

## Intake result

| Id | Category | Statement | Status |
|---|---|---|---|
| R1 | Catalog | Kit = one hub plus sensors | Stated; sensor count per kit missing |
| R2 | Catalog | Installation service | Stated; fulfillment and billing trigger missing |
| R3 | Selling models | Monitoring: 3-year term | Stated |
| R4 | Billing | Monitoring billed yearly | Stated; in advance or arrears missing |
| R5 | Usage | Data feed by monthly usage with a minimum commitment | Stated; unit, tiers, overage, source missing |
| R6 | Approvals | Regional managers approve above a threshold | Stated; threshold, scope, levels missing |
| R7 | Lifecycle | Renew at term end | Stated; uplift, renewal quote generation missing |
| R8 | Pricing | (none) | Missing: price basis, discount scope, currencies |
| R9 | Documents, contracts | (none) | Missing |
| R10 | Volumes | (none) | Missing |

## Questions to send (grouped by owner)

- Catalog: how many sensors per kit, fixed or chosen? Is the hub sold alone? Is a sensor
  priced, fulfilled or tracked on its own?
  ([bundles-and-cardinality.md](../product-catalog-modeling/bundles-and-cardinality.md))
- Fulfillment and billing: is installation a manual visit, a partner job or a scheduled
  task? What marks it complete? Is it billed on completion, at order, or in installments?
  ([authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md),
  [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services))
- Billing: is the yearly monitoring charge billed at the start or the end of each year?
  ([Billing policies and treatments](../billing-setup/SKILL.md#billing-policies-and-treatments))
- Usage: unit, who supplies the records, how often rated, what happens to unused
  commitment, tier breaks, overage rate. No skill gives a usage-product design guide: open.
- Approvals: threshold per line or per quote, discount on lines or on the header, percent or
  amount, one level or more? ([matrix-modeling.md](../advanced-approvals/matrix-modeling.md))
- Renewal: same price, uplift, or re-quote? Early renewal allowed?
  ([change-policy-mapping.md](../asset-lifecycle-changes/change-policy-mapping.md))
- Pricing, documents, volumes: price basis, currencies, which documents, accounts and
  quotes per month.

Suppose the answers are: 4 sensors per kit, installation is a partner visit completed by a
confirmation task (one visit per kit) billed on completion, monitoring billed in advance, usage
rated monthly in gigabytes with a minimum, approval for any quote discount above 10 percent in one
level, renewal at the same price, one currency, quote and contract documents.

## Decision log (excerpt)

| Id | Decision | Choice | Why | Options in |
|---|---|---|---|---|
| D1 | Sensor: product, attribute or component | Component of the kit, assuming a sensor is priced, fulfilled or tracked on its own; if not, the test gives an attribute on the kit | Assumption to log: R1 gives the count, 4 per kit, but not whether a sensor stands alone, which is the owner's test (separately fulfilled, assetized, renewed or invoiced, or its own price or selling model) | [Product vs attribute vs component](../product-catalog-modeling/SKILL.md#product-vs-attribute-vs-component) |
| D2 | Kit shape | Static bundle with one sensor component of quantity 4 (R1 answer); sensor quantity scaling Proportional | Fixed content, no choices. Proportional is an assumption to log: it is the default when quantity changes are off at creation | [bundles-and-cardinality.md](../product-catalog-modeling/bundles-and-cardinality.md) |
| D3 | Selling model, monitoring | Term defined, 36 months | R3 | [selling-models-and-lifecycle.md](../product-catalog-modeling/selling-models-and-lifecycle.md#choose-the-selling-model-from-the-pricing-basis) |
| D4 | Selling model, installation | One-time | A one-time charge; milestone billing sits on one-time lines | [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) |
| D5 | Billing frequency, monitoring | Annual, in advance | R4. The owner says a frequency that differs from the pricing term needs a treatment on the line, so compare the model's term unit with the yearly frequency and log the result | [Billing frequency](../billing-setup/SKILL.md#billing-frequency) |
| D6 | Assetizable | Kit, monitoring and data feed yes, installation no | Renewal acts on the subscription; usage is recorded against a usage-entitled asset ([The Pipeline](../usage-consumption/SKILL.md#the-pipeline)); installation is not renewed. Confirm with the customer | [IsAssetizable](../product-catalog-modeling/selling-models-and-lifecycle.md#isassetizable) |
| D7 | Discount scope | Line discount; approval when the quote's percent off list, 1 - (sum of line net totals / sum of line list totals), is above 10 | R6 gives the threshold only; line versus header discount and this computation are assumptions to confirm with the customer. The shipped level bands each line's own percent, not a quote percent off list, so this needs its own computation ([matrix-modeling.md](../advanced-approvals/matrix-modeling.md#2-compute-each-level-as-a-number)) | [manual-discount.md](../pricing-procedures/elements/manual-discount.md) |
| D8 | Who or what marks the installation's event milestone accomplished: a billing user or a fulfillment automation | Open: Help names no link from fulfillment steps to billing milestones | Decide with the customer, then verify live and log evidence | [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) (Marking an event milestone done), [updates-and-runtime.md](../dro-plans/updates-and-runtime.md) |
| D9 | Ramp | None: flat 3-year term at one price | R7 answer: same price; no step-ups | [Ramps](../product-catalog-modeling/selling-models-and-lifecycle.md#ramps) |
| D10 | Installation decomposition: scope, quantity behavior, step scope | Order Line Item scope; the settings that give one visit per kit are open | The customer's answer: one visit per kit. The owner says Order Line Item with `AlwaysOne` gives one technical item for a line of quantity 10, so that pair alone does not give it | [Decomposed Line Items](../dro-plans/authoring-and-deployment.md#decomposed-line-items) |
| D11 | Installation billing milestone | One event-based milestone at 100 percent, billed when the installation is marked complete | Assumption to log: R2 says billed on completion; the milestone's name, type and share are not stated | [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) (when a source names no milestones) |

## Derived counts

State the arithmetic, from the model and the decisions:

- Sensors on an order of 10 kits: one sensor component line of quantity 40 (10 x 4), per D2's
  Proportional method, where child quantity is parent quantity times child quantity (see
  [scaling](../product-catalog-modeling/bundles-and-cardinality.md#quantity-scaling-and-lifecycle)).
  Confirm it in the org.
- Fulfillment instances for the installation: suppose an order of 10 kits carries one
  installation line of quantity 10 (an assumption to log; installation could instead be one
  line per kit or a kit component). With Order Line Item scope and `AlwaysOne` that is one
  technical item, not 10; the customer wants 10 visits, so the quantity behavior and step
  scope that give 10 are part of D10 and the count stays open until a run shows it
  ([Decomposed Line Items](../dro-plans/authoring-and-deployment.md#decomposed-line-items)).
- Yearly invoices for one monitoring line: 36 months / 12 = 3. Confirm the schedule count
  in the org.

## Build order for this plan

Place the items on the [graph](build-order.md#prerequisite-graph):

1. Stage 0 and 1: enablement and permissions; fields (none needed in this example unless a
   context attribute feeds pricing).
2. Stage 1 and 2: catalog (hub, sensor, kit, installation, monitoring, data feed) and
   selling model options.
3. Stage 3 to 5: price book and entries, tables, procedure with the Manual Discount element (D7),
   activate.
4. Stage 6, in parallel: approval matrix and flow, with the D7 quote percent computed as a
   quote-level value in the approval data flow (see
   [section 2](../advanced-approvals/matrix-modeling.md#2-compute-each-level-as-a-number));
   billing policies and treatments, including the D11 milestone treatment; fulfillment
   configuration for the installation; usage resources, policies and commitment; contract
   setup.
5. Stage 7: quote and order UI, then the quote and contract document templates.
6. Stage 8 to 10: test quote, order, fulfillment, assets, invoices, usage, renew.

Open items carried into the plan: D8, D10 settings, usage-product design, tax (no owner),
invoice run and payments (no owner).

Assumptions to confirm (owner: the customer), each with every plan item that depends on it:

- D1 (sensor as a component of the kit): build step 2 (catalog), D2, chain steps 3 (Price)
  and 9 (Assets).
- D2 (one sensor component of quantity 4, Proportional scaling): build step 2 (catalog), the
  sensor count, chain steps 3 (Price), 9 (Assets) and 14 (Renew), since Proportional keeps
  the ratio on renewal.
- D6 (assetizable products): build step 2 (catalog flags), chain steps 9 (Assets), 12
  (Usage) and 14 (Renew).
- D7 (line discount; the quote percent and its computation): build step 3 (procedure),
  build step 4 (approval matrix, flow and quote percent), chain steps 3 (Price) and 6
  (Approve).
- The installation as one line of quantity 10: the fulfillment count, D8, D10, D11, chain steps
  8 (Fulfill) and 10 (Bill); activation built one milestone plan per order item in the
  owner's measured run (one org).

## Chain binding (excerpt)

| Chain step | Proves | Expected value source |
|---|---|---|
| 3 Price | R1, R3, R8 | Hand-computed totals from the customer's price list |
| 6 Approve | R6 | A quote at 9 percent routes to nobody; at 11 percent to one level, with the percent as D7 defines it |
| 8 Fulfill | R2 | Installation tasks equal one per kit, from the D10 settings |
| 10 Bill | R4, R2 | 3 yearly invoices; installation billing per D11 and D8 evidence |
| 12 Usage | R5 | Rated amount equals hand computation for one test month |
| 14 Renew | R7 | Renewal line price equals the original |

See [acceptance-chain.md](acceptance-chain.md) for how to run each step.
