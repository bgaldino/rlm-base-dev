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

- Catalog: how many sensors per kit, fixed or chosen? Is the hub sold alone?
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
| D1 | Sensor: product, attribute or component | Component of the kit | R1: each sensor needs its own record if it must be counted, priced or tracked | [Product vs attribute vs component](../product-catalog-modeling/SKILL.md#product-vs-attribute-vs-component) |
| D2 | Kit shape | Static bundle with 4 sensors (R1 answer) | Fixed content, no choices | [bundles-and-cardinality.md](../product-catalog-modeling/bundles-and-cardinality.md) |
| D3 | Selling model, monitoring | Term defined, 36 months | R3 | [selling-models-and-lifecycle.md](../product-catalog-modeling/selling-models-and-lifecycle.md#choose-the-selling-model-from-the-pricing-basis) |
| D4 | Selling model, installation | One-time | A one-time charge; milestone billing sits on one-time lines | [Milestone billing for services](../billing-setup/SKILL.md#milestone-billing-for-services) |
| D5 | Billing frequency, monitoring | Annual, in advance | R4. The owner says a frequency that differs from the pricing term needs a treatment on the line, so compare the model's term unit with the yearly frequency and log the result | [Billing frequency](../billing-setup/SKILL.md#billing-frequency) |
| D6 | Assetizable | Kit and monitoring yes, installation no | Renewal acts on the subscription; installation is not renewed. Confirm with the customer | [IsAssetizable](../product-catalog-modeling/selling-models-and-lifecycle.md#isassetizable) |
| D7 | Discount scope | Line discount, approval above 10 percent of the quote | R6 gives the threshold only; line versus header discount is an assumption to confirm with the customer | [manual-discount.md](../pricing-procedures/elements/manual-discount.md) |
| D8 | Installation completion to billing trigger | Open: not established by a skill | Verify live; log evidence | [updates-and-runtime.md](../dro-plans/updates-and-runtime.md) |
| D9 | Ramp | None: flat 3-year term at one price | R7 says same price; no step-ups | [Ramps](../product-catalog-modeling/selling-models-and-lifecycle.md#ramps) |
| D10 | Fulfillment decomposition scope | Per kit | The customer's answer: one visit per kit | [authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md) |

## Derived counts

State the arithmetic, from the model and the decisions:

- Sensors on an order of 10 kits: 10 kits x 4 sensors = 40 sensor lines or quantity 40, per the
  cardinality rule the owner states (see the two kinds of
  [cardinality](../product-catalog-modeling/bundles-and-cardinality.md#two-kinds-of-cardinality)).
  Which of the two the run produces is read from the org, not assumed.
- Fulfillment instances for the installation: depends on D10 (per order, per kit, per quantity).
  With per kit, 10 kits give 10 installation tasks; if per order, one task. The decomposition scope
  is a decision, not a default
  ([authoring-and-deployment.md](../dro-plans/authoring-and-deployment.md)).
- Yearly invoices for one monitoring line: 36 months / 12 = 3. Confirm the schedule count
  in the org.

## Build order for this plan

Place the items on the [graph](build-order.md#prerequisite-graph):

1. Stage 0 and 1: enablement and permissions; fields (none needed in this example unless a
   context attribute feeds pricing).
2. Stage 1 and 2: catalog (hub, sensor, kit, installation, monitoring, data feed) and
   selling model options.
3. Stage 3 to 5: price book and entries, tables, procedure with the line discount flag,
   activate.
4. Stage 6, in parallel: approval matrix and flow; billing policies and treatments;
   fulfillment configuration for the installation; usage resources, policies and
   commitment; contract setup.
5. Stage 7: quote and order UI, then the quote and contract document templates.
6. Stage 8 to 10: test quote, order, fulfillment, assets, invoices, usage, amend, renew.

Open items carried into the plan: D8, usage-product design, tax (no owner), invoice run and
payments (no owner).

## Chain binding (excerpt)

| Chain step | Proves | Expected value source |
|---|---|---|
| 3 Price | R1, R3, R8 | Hand-computed totals from the customer's price list |
| 6 Approve | R6 | A quote at 9 percent routes to nobody; at 11 percent to one level |
| 8 Fulfill | R2 | Installation tasks equal the derived count |
| 10 Bill | R4, R2 | 3 yearly invoices; installation billing per D8 evidence |
| 12 Usage | R5 | Rated amount equals hand computation for one test month |
| 14 Renew | R7 | Renewal line price equals the original |

See [acceptance-chain.md](acceptance-chain.md) for how to run each step.
