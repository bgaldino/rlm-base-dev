# Concept Map — Commercial Concepts to Revenue Cloud

Read this when mapping a source with [commercial-model-planning](SKILL.md). Each row
names the feature to try first and the skill that covers it. It is a starting point,
not a decision. For each rule, read the domain skill, including its open items, then
decide the knowledge source with [knowledge-sources.md](knowledge-sources.md) after the
coverage sweep. A few rows note an open item that changes the choice; that note is a
pointer, not the skill's full open list.

## Catalog

| Source concept | Try first | Where documented |
|---|---|---|
| Item with a list price and unit | `Product2` + price book entry | `product-catalog-modeling`; `sfdmu-data-plans` (loading) |
| Pricing basis: one-time / committed term / until cancelled | Selling models by end date: One-Time; Term Defined for a committed term (any term unit, so 12 months billed monthly is Term Defined); Evergreen for until cancelled. Billing cadence is a separate choice (`billing-setup`) | `product-catalog-modeling` → `selling-models-and-lifecycle.md`; `pricing-setup` → `proration-and-selling-models.md` |
| Package priced as the sum of its contents | Configurable bundle; component groups with min and max. Decide the root's own selling model | `product-catalog-modeling` → `bundles-and-cardinality.md`, `selling-models-and-lifecycle.md` |
| Fixed kit | Static bundle. If any child is Term Defined or Evergreen, try a locked configurable bundle; the static kit with recurring children is open | `product-catalog-modeling` → `bundles-and-cardinality.md` |
| Option the rep picks, priced | Attribute with attribute-based price, or a component | `product-catalog-modeling` → `attributes-and-classifications.md`; `pricing-procedures` → `elements/attribute-based-price.md`; for an answer on the parent priced on a child, `elements/root-answer-child-price.md` |
| Not sold standalone | `IsSoldOnlyWithOtherProds` | `product-catalog-modeling` → `selling-models-and-lifecycle.md` |
| Not tracked in the installed base | `IsAssetizable = false` | same |
| Product lines, categories, catalogs | Catalog categories and `Family` | `product-catalog-modeling` → `catalogs-and-loading.md` |
| Part number per configuration | Attribute set by CML from the selection. No skill covers building one value from several selections; record it as a skill gap | — (`elements/root-answer-child-price.md` route 1 shows CML setting a child attribute, unmeasured) |

## Configuration and rules

| Source concept | Try first | Where documented |
|---|---|---|
| Sizing questions | Attributes on the bundle root | `constraint-models` → `quantities-from-attributes.md` |
| Quantity derived from answers (one per user, one per block of N rounded up) | CML cardinality constraints driven by `int` variables, with an integer bracket for rounding up | `constraint-models` → `quantities-from-attributes.md` (`ceil()` doesn't round inside a constraint) |
| Effort or hours estimator | Same, on service components | same |
| "X only with Y", "exactly one of" | CML constraints with messages | `constraint-models` |
| Note that doesn't block | CML message with `Info` severity. `Warning` blocks the next step until the rep acts | `constraint-models` → `quantities-from-attributes.md` |
| Rep may change a quantity the rules size | Decide which wins: rule-owned sizing, or an editable line | `constraint-models` → `quantities-from-attributes.md` |

## Pricing

| Source concept | Try first | Where documented |
|---|---|---|
| Volume bands by quantity | Volume and tier discounts, price adjustment schedule | `pricing-procedures` → `elements/volume-and-tier-discount.md`; `pricing-setup` → `price-adjustment-schedules.md` |
| Discount when bought in a package | Bundle-based adjustment | `pricing-procedures` → `elements/bundle-based-price.md` |
| Regional or channel uplift | A documented route first: CML copies the root answer to a price-impacting child attribute plus an attribute-based price; formula-based pricing on a header value; or a price adjustment matrix over a lookup table. All three are documented but unmeasured (open); the attribute adjustment matrix is unverified. Each route needs different catalog and model pieces (the first, a price-impacting attribute on the children's classification and a CML line): list them per route (SKILL step 6) | `pricing-procedures` → `elements/root-answer-child-price.md` |
| Order of application, rounding | Procedure element order, rounding element | `pricing-procedures` → `procedure-anatomy-and-ordering.md`, `elements/rounding-values.md` |
| Second currency | Multicurrency price book entries, and per-currency rows for every adjustment that matches on currency (volume tiers, bundle-based adjustments) as well as cost entries | `pricing-setup`, `sfdmu-data-plans` |
| Annual escalator | Group ramp with uplift. An API-built group-ramped bundle with a one-time or evergreen child failed to amend (`asset-lifecycle-changes` Quick Rule 8) | `ramped-quotes`; `pricing-procedures` → `elements/price-revision-compound-uplift.md` |
| Renewal uplift | Price revision policy. Renewal uplifts apply only to term-defined selling models (Help: `ind.qocal_renewal_price_uplifts`), so an Evergreen line takes none | `pricing-setup` → `price-revision-policies.md`; `asset-lifecycle-changes` |
| Discount for a longer commitment | List filter on term plus a formula step on Term Defined lines | `pricing-procedures` → `elements/commitment-term-discount.md` |
| A policy the source marks approved but not yet applied in its calculator | Build it behind a quote-level switch the procedure reads; run the source's goldens with it off and the policy's own examples with it on. Ask whether two such policies stack, and for each policy's effective date | `pricing-procedures` → `elements/root-answer-child-price.md` (route 2: map the header field into the context, then read it in a formula; documented but unmeasured). A list filter on a header tag is unverified |
| Price from cost and a target margin | Formula step on a cost looked up from a decision table | `pricing-setup` → `cost-books.md`, `scenarios/cost-and-margin.md`; `pricing-procedures` → `elements/formula-based-pricing.md` |

## Cost and margin

| Source concept | Try first | Where documented |
|---|---|---|
| Standard cost per item | Cost book entries | `pricing-setup` → `cost-books.md`, `scenarios/cost-and-margin.md` |
| Labour rates, loaded cost | Computed during extraction into cost entries | `pricing-setup` → `scenarios/cost-and-margin.md` (modeling costs from a source) |
| Line and quote margin | The shipped cost-and-margin wiring, plus a roll-up for the quote total | `pricing-setup` → `scenarios/cost-and-margin.md` |
| Contract value that counts until-cancelled lines over a fixed term | A computed value of its own; a quote total counts an Evergreen line for the Pricing Setup default term count (or, when that is blank, from the line's start and end dates), not the source's term `[inferred]` in that scenario. The default counts have no API: read them in Setup at P0 | `pricing-setup` → `proration-and-selling-models.md`, `scenarios/cost-and-margin.md` |
| A fee or commission computed from the deal's revenue | A computed value (a field or a formula), not a price adjustment. Check which deals it applies to | — |
| Items resold at or near cost | Priced near cost by design; decide how margin and below-cost guards and discounts treat them | `pricing-setup` → `scenarios/cost-and-margin.md`; `advanced-approvals` → `matrix-modeling.md` |

## Billing

| Source concept | Try first | Where documented |
|---|---|---|
| Billing frequency (annual, monthly) | `BillingFrequency` set on every Term Defined and Evergreen line placed through the API (a Term Defined line without one was refused). A cadence different from the pricing term needs a treatment that allows it | `billing-setup` |
| In advance vs in arrears; milestone billing | Billing policy and treatment. Milestones the source doesn't name are a decision for its owner, not invented | `billing-setup` |
| Payment terms | `Order.PaymentTermId` for invoicing; the shipped approval reads a custom quote picklist, and nothing copies one to the other. Decide how they meet | `billing-setup`; `advanced-approvals` |
| Non-standard billing as an approval trigger | A quote-level value computed from the lines' billing frequency (in the approval data flow, or a roll-up count of non-standard lines) that the approval condition tests | `advanced-approvals` → `matrix-modeling.md` |

## Negotiation and approvals

| Source concept | Try first | Where documented |
|---|---|---|
| Rounds or versions of a bid | One quote per round, by deep clone; the winning round becomes the order | `quote-negotiation-rounds` |
| An internal what-if round that must never be presented | A marker on the quote plus a guard on presenting and ordering it | `quote-negotiation-rounds` |
| Discount per product line | Manual line discounts. A line-editor group discount is open: unmeasured inside a bundle, and Propagation ships off. Not a header discount: it was measured applying twice with an active procedure plan and `skipOrgSttPricing` on | `pricing-procedures` → `elements/manual-discount.md`, `elements/price-propagation.md`; `transaction-line-editor` → `runtime-behavior.md` |
| Approval matrix by discount, margin, size | Advanced Approvals: one level per dimension, the maximum drives a cumulative chain. State what "discount" is measured against (list, or a standard price after programs) | `advanced-approvals` → `matrix-modeling.md` |
| Line-level guards (below floor, below cost) | A count of breaking lines as an approval condition, with a marker so a round's bulk discount and an individual override can be told apart; name what sets the marker on each path | `advanced-approvals` → `matrix-modeling.md` |
| "Resubmit from the start" after a rejection | Smart Approval off on that chain's steps, or accepted as a difference | `advanced-approvals` → `matrix-modeling.md`, `limitations.md` |

## Lifecycle

| Source concept | Try first | Where documented |
|---|---|---|
| Co-termed addition | Amendment of the top-level asset. On a bundle sized from root answers, decide how "add N" maps onto the root | `asset-lifecycle-changes` → `change-policy-mapping.md`; `rlm-business-apis` → `backdated-asset-lifecycle.md` |
| Swap one plan for another | Swap action | `asset-lifecycle-changes` |
| Cancellation credit | Cancellation | `asset-lifecycle-changes` → `change-policy-mapping.md` |
| Renewal at a new price | Renewal with a price revision policy | `asset-lifecycle-changes`, `renewal-asset-creation`, `pricing-setup` |
| Proving a change end to end | Reprice, order, activate, check the asset | `asset-lifecycle-changes` → `verification.md` |

## Runtime surface

| Source concept | Try first | Where documented |
|---|---|---|
| Columns the rep needs (margin, product line, uplift) | Line editor display columns | `transaction-line-editor` → `page-configuration.md` |
| Grouping lines | Line groups in the line editor | `transaction-line-editor`; `ramped-quotes` (groups) |
| Header actions (reprice, ramp schedule, header adjustment) | Line editor action buttons | `transaction-line-editor` |
