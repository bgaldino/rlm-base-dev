# Concept Map — Commercial Concepts to Revenue Cloud

Read this when mapping a source with [commercial-model-planning](SKILL.md). Each row
names the feature to try first, the skill that covers it, and what is commonly still
open for it. This is a starting point, not a decision: for each rule, decide the
knowledge source with [knowledge-sources.md](knowledge-sources.md) after the coverage
sweep, and read the domain skill's own open-items list for what is still unmeasured.

## Catalog

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Item with a list price and unit | `Product2` + price book entry | `product-catalog-modeling`; `sfdmu-data-plans` (loading) | — |
| Pricing basis: one-time / annual subscription / monthly plan | Selling models: One-Time, Term Defined (annual), Evergreen (monthly) | `product-catalog-modeling` → `selling-models-and-lifecycle.md`; `pricing-setup` → `proration-and-selling-models.md` | how a bundle with mixed selling models co-terminates and renews (`asset-lifecycle-changes`) |
| Package priced as the sum of its contents | Configurable bundle; component groups with min and max. Decide the root's own selling model | `product-catalog-modeling` → `bundles-and-cardinality.md`, `selling-models-and-lifecycle.md` | how the root's selling model renews its children (`asset-lifecycle-changes`) |
| Fixed kit | Static bundle | same | — |
| Option the rep picks, priced | Attribute with attribute-based price, or a component | `product-catalog-modeling` → `attributes-and-classifications.md`; `pricing-procedures` → `elements/attribute-based-price.md`; for an answer on the parent priced on a child, `elements/root-answer-child-price.md` | whether a CML-set value is saved on the line and reaches pricing |
| Not sold standalone | `IsSoldOnlyWithOtherProds` | `product-catalog-modeling` → `selling-models-and-lifecycle.md` | what enforces it at run time |
| Not tracked in the installed base | `IsAssetizable = false` | same | its effect on amend, cancel and renew |
| Product lines, categories, catalogs | Catalog categories and `Family` | `product-catalog-modeling` → `catalogs-and-loading.md` | — |
| Part number per configuration | Attribute set by CML from the selection | `constraint-models`; `pricing-procedures` → `elements/root-answer-child-price.md` (route 1) | whether a CML-set attribute value is saved on the line |

## Configuration and rules

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Sizing questions | Attributes on the bundle root | `constraint-models` → `quantities-from-attributes.md` | — |
| Quantity derived from answers (per site, per 10 rounded up) | CML cardinality constraints driven by `int` variables, with an integer bracket for rounding up | `constraint-models` → `quantities-from-attributes.md` (`ceil()` doesn't round inside a constraint) | — |
| Effort or hours estimator | Same, on service components | same | — (golden tests check each rounding step) |
| "X only with Y", "exactly one of" | CML constraints with messages | `constraint-models` | enforcement on amendments, not just new sales |
| Note that doesn't block | CML message with `Info` severity. `Warning` blocks the next step until the rep acts | `constraint-models` → `quantities-from-attributes.md` | what `Info` shows in each surface |
| Rep may change a quantity the rules size | Decide which wins: rule-owned sizing, or an editable line | `constraint-models` → `quantities-from-attributes.md` | whether the rep can edit a constraint-sized line (the sources qualify each other) |

## Pricing

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Volume bands by quantity | Volume and tier discounts, price adjustment schedule | `pricing-procedures` → `elements/volume-and-tier-discount.md`; `pricing-setup` → `price-adjustment-schedules.md` | new units only at the new band on an amendment (`asset-lifecycle-changes`) |
| Discount when bought in a package | Bundle-based adjustment | `pricing-procedures` → `elements/bundle-based-price.md` | — |
| Regional or channel uplift | A documented route first: CML copies the root answer to a price-impacting child attribute plus an attribute-based price; formula-based pricing on a header value; or a price adjustment matrix over a lookup table. The attribute adjustment matrix is unverified | `pricing-procedures` → `elements/root-answer-child-price.md` | which route works live when the driver lives on a different line from the price |
| Order of application, rounding | Procedure element order, rounding element | `pricing-procedures` → `procedure-anatomy-and-ordering.md`, `elements/rounding-values.md` | — (golden tests check rounding once vs per step) |
| Second currency | Multicurrency price book entries | `pricing-setup`, `sfdmu-data-plans` | — |
| Annual escalator | Group ramp with uplift | `ramped-quotes`; `pricing-procedures` → `elements/price-revision-compound-uplift.md` | a ramped bundle with one-time or evergreen children failed to amend when built by API (`ramped-quotes`) |
| Renewal uplift | Price revision policy | `pricing-setup` → `price-revision-policies.md`; `asset-lifecycle-changes` | the renewal's actual value |
| Discount for a longer commitment | List filter on term plus a formula step on Term Defined lines | `pricing-procedures` → `elements/commitment-term-discount.md` | whether an amendment or renewal applies it a second time |
| A policy approved but not yet in the source's calculator ("Proposed") | Build it behind a quote-level switch the procedure filters on; run the source's goldens with it off and the policy's own examples with it on. Ask whether two such policies stack | `pricing-procedures` (filters) | — |
| Price from cost and a target margin | Formula step on a cost looked up from a decision table | `pricing-setup` → `cost-books.md`, `scenarios/cost-and-margin.md`; `pricing-procedures` → `elements/formula-based-pricing.md` | — |

## Cost and margin

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Standard cost per item | Cost book entries | `pricing-setup` → `cost-books.md`, `scenarios/cost-and-margin.md` | — |
| Labour rates, loaded cost | Computed during extraction into cost entries | `pricing-setup` → `scenarios/cost-and-margin.md` (modeling costs from a source) | — |
| Line and quote margin | The shipped cost-and-margin wiring, plus a roll-up for the quote total | `pricing-setup` → `scenarios/cost-and-margin.md` | margin on multi-period subscription lines |
| Full commitment value, with monthly lines counted "for comparison" | A computed value of its own; a quote total counts an Evergreen line for the Pricing Setup default term count (or, when that is blank, from the line's start and end dates), not the source's term `[inferred]` in that scenario | `pricing-setup` → `proration-and-selling-models.md`, `scenarios/cost-and-margin.md` | — |
| Partner or referral fee taken from net revenue | A computed value (a field or a formula), not a price adjustment. Check whether it applies on a direct deal | — | — |
| Pass-through items (travel, expenses) | Priced near cost by design; decide how margin and below-cost guards treat them | `pricing-setup` → `scenarios/cost-and-margin.md`; `advanced-approvals` → `matrix-modeling.md` | — |

## Billing

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Billing frequency (annual, monthly) | `BillingFrequency` set on every Term Defined and Evergreen line; it isn't derived from the selling model. A cadence different from the pricing term needs a treatment that allows it | `billing-setup` | — |
| In advance vs in arrears; milestone billing | Billing policy and treatment. Milestones the source doesn't name are a decision for its owner, not invented | `billing-setup` | the invoice values |
| Payment terms | `Order.PaymentTermId` for invoicing; the shipped approval reads a custom quote picklist, and nothing copies one to the other. Decide how they meet | `billing-setup`; `advanced-approvals` | the term on the first invoice (`billing-setup` infers it; not yet run) |
| Non-standard billing as an approval trigger | Approval condition on the line's billing frequency | see Negotiation and approvals | — |

## Negotiation and approvals

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Rounds or versions of a bid | One quote per round, by deep clone; the winning round becomes the order | `quote-negotiation-rounds` | — |
| An internal what-if round that must never be presented | A marker on the quote plus a guard on presenting and ordering it | `quote-negotiation-rounds` | — |
| Discount per product line | Manual line discounts, or a group in the line editor | `pricing-procedures` → `elements/manual-discount.md`, `elements/discount-distribution-service.md`; `transaction-line-editor` → `runtime-behavior.md` | whether a group or bulk-edit discount reaches bundle child lines; the group route also needs a group discount field on the page (`transaction-line-editor` → `runtime-behavior.md`). Don't use a header discount instead: it was measured applying twice with an active procedure plan and `skipOrgSttPricing` on |
| Approval matrix by discount, margin, size | Advanced Approvals: one level per dimension, the maximum drives a cumulative chain. State what "discount" is measured against (list, or a standard price after programs) | `advanced-approvals` → `matrix-modeling.md` | the Preview tool's gaps; prove with a real submission (`advanced-approvals` → `limitations.md`) |
| Line-level guards (below floor, below cost) | A count of breaking lines as an approval condition, with a marker so a round's bulk discount and an individual override can be told apart | `advanced-approvals` → `matrix-modeling.md` | same |
| "Resubmit from the start" after a rejection | Smart Approval off on that chain's steps, or accepted as a difference | `advanced-approvals` → `matrix-modeling.md`, `limitations.md` | — |

## Lifecycle

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Co-termed addition | Amendment of the top-level asset. On a bundle sized from root answers, decide how "add N" maps onto the root | `asset-lifecycle-changes` → `change-policy-mapping.md`; `rlm-business-apis` → `backdated-asset-lifecycle.md` | values; attributes after a UI quantity edit on an amendment line |
| Swap one plan for another | Swap action | `asset-lifecycle-changes` | constraints on the amendment |
| Cancellation credit | Cancellation | `asset-lifecycle-changes` → `change-policy-mapping.md` | credit by selling model and date |
| Renewal at a new price | Renewal with a price revision policy | `asset-lifecycle-changes`, `renewal-asset-creation`, `pricing-setup` | the renewal's value and term |
| Proving a change end to end | Reprice, order, activate, check the asset | `asset-lifecycle-changes` → `verification.md` | — |

## Runtime surface

| Source concept | Try first | Where documented | Commonly open |
|---|---|---|---|
| Columns the rep needs (margin, product line, uplift) | Line editor display columns | `transaction-line-editor` → `page-configuration.md` | — (visibility per permission set is checked at the build gate) |
| Grouping lines | Line groups in the line editor | `transaction-line-editor`; `ramped-quotes` (groups) | — |
| Header actions (reprice, ramp schedule, header adjustment) | Line editor action buttons | `transaction-line-editor` | the action-button setup and limits disagree across the docs |
