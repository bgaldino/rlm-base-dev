# Concept Map — Commercial Concepts to Revenue Cloud

Read this when mapping a source with [commercial-model-planning](SKILL.md). Each row
names the feature to try first, where the repo documents it, and the usual reason for
a live check. The letter is the trigger from [knowledge-sources.md](knowledge-sources.md):
(a) silent, (b) measured differently, (c) lifecycle numbers, (d) docs disagree or a
preview. This is a starting point; the coverage sweep decides each rule for the current
release.

## Catalog

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Item with a list price and unit | `Product2` + price book entry | `revenue-cloud-data-model`, `sfdmu-data-plans` | — |
| Pricing basis: one-time / annual subscription / monthly plan | Selling models: One-Time, Term Defined (annual), Evergreen (monthly) | `pricing-setup` → `proration-and-selling-models.md` | (b) a term model under a configurable bundle |
| Package priced as the sum of its contents | Configurable bundle; component groups with min and max | `revenue-cloud-data-model`, `sfdmu-data-plans`; dev guide cardinality articles | — |
| Fixed kit | Static bundle | same | — |
| Option the rep picks, priced | Attribute with attribute-based price, or a component | `pricing-procedures` → `elements/attribute-based-price.md` | (b) attribute on the parent, price on a child |
| Not sold standalone | `IsSoldOnlyWithOtherProds` | `revenue-cloud-data-model` | — |
| Not tracked in the installed base | `IsAssetizable = false` | `revenue-cloud-data-model` | (c) its effect on amend, cancel and renew |
| Part number per configuration | Attribute set by CML from the selection | `constraint-models` | — |

## Configuration and rules

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Sizing questions | Attributes on the bundle root | `constraint-models` | — |
| Quantity derived from answers (per site, per 10 rounded up) | CML cardinality constraints; `ceil()` | `constraint-models`; dev guide: accessing quantity in CML, numerical functions, quantity and aggregation guidelines | — |
| Effort or hours estimator | Same, on service components | same | — (golden tests check each rounding step) |
| "X only with Y", "exactly one of" | CML constraints with messages | `constraint-models` | (c) enforcement on amendments, not just new sales |
| Warning that doesn't block | CML message with warning severity | `constraint-models` | — |

## Pricing

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Volume bands by quantity | Volume and tier discounts, price adjustment schedule | `pricing-procedures` → `elements/volume-and-tier-discount.md`; `pricing-setup` → `price-adjustment-schedules.md` | (c) new units only at the new band on an amendment |
| Discount when bought in a package | Bundle-based adjustment | `pricing-procedures` → `elements/bundle-based-price.md` | — |
| Regional or channel uplift | Attribute adjustment matrix, or a decision-table lookup | `pricing-procedures` → `elements/attribute-adjustment-matrix.md`, `elements/decision-table-lookups.md` | (b) the driver lives on a different line from the price |
| Order of application, rounding | Procedure element order, rounding element | `pricing-procedures` → `procedure-anatomy-and-ordering.md`, `elements/rounding-values.md` | — (golden tests check rounding once vs per step) |
| Second currency | Multicurrency price book entries | `pricing-setup`, `sfdmu-data-plans` | — |
| Annual escalator | Group ramp with uplift | `ramped-quotes`; `pricing-procedures` → `elements/price-revision-compound-uplift.md` | (b) a ramped bundle with one-time or evergreen children can't be amended when built by API (`ramped-quotes`) |
| Renewal uplift | Price revision policy | `pricing-setup` → `price-revision-policies.md` | (c) the renewal's actual value |
| Discount for a longer commitment | Price adjustment matrix or formula on term | `pricing-procedures` → `elements/price-adjustment-matrix.md`, `elements/formula-based-pricing.md` | (a) if the sweep finds no commitment-term coverage |
| Price from cost and a target margin | Formula step on a cost looked up from a decision table | `pricing-setup` → `cost-books.md`; `pricing-procedures` → `elements/formula-based-pricing.md` | — |

## Cost and margin

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Standard cost per item | Cost book entries | `pricing-setup` → `cost-books.md` | — |
| Labour rates, loaded cost | Computed during extraction into cost entries | — | — |
| Line and quote margin | Cost through a decision table; the procedure's cost-and-margin formulas | `pricing-procedures` → `elements/formula-based-pricing.md`, `elements/list-group-and-list-operation.md`; `decision-tables` | — (field visibility is checked at the build gate) |

## Billing

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Billing frequency (annual, monthly) | Billing frequency on the line, from the selling model | `pricing-setup` → `proration-and-selling-models.md`; Help: Billing | — |
| In advance vs in arrears; milestone billing | Billing policy and treatment | Help: Billing | (c) the invoice values |
| Non-standard billing as an approval trigger | Approval condition on the line's billing frequency | see Negotiation and approvals | — |

## Negotiation and approvals

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Rounds or versions of a bid | One quote per round, by the clone action | `rlm-business-apis` | — |
| Discount per product line | Manual line discounts, or a group in the line editor | `pricing-procedures` → `elements/manual-discount.md`, `elements/discount-distribution-service.md` | (b) a header discount was measured applying twice with an active procedure plan |
| Approval matrix by discount, margin, size | Advanced Approvals | `rlm-business-apis` (approvals endpoints); Help: approvals articles | (d) preview considerations and limitations; (c) cumulative levels and rejection paths |
| Line-level guards (below floor, below cost) | Approval conditions on line margin | same | same |

## Lifecycle

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Co-termed addition | Amendment | `rlm-business-apis` → `backdated-asset-lifecycle.md`; Help: co-terminate | (c) values; (b) attributes after a quantity edit on an amendment line |
| Swap one plan for another | Swap action | `rlm-business-apis` | (c) constraints on the amendment |
| Cancellation credit | Cancellation | `rlm-business-apis` → `backdated-asset-lifecycle.md` | (b)(c) credit by selling model and date |
| Renewal at a new price | Renewal with a price revision policy | `renewal-asset-creation`, `pricing-setup` | (c) the renewal's value and term |

## Runtime surface

| Source concept | Try first | Where documented | Usual live trigger |
|---|---|---|---|
| Columns the rep needs (margin, product line, uplift) | Transaction Line Editor display fields | Help: Transaction Line Editor articles; `repo-integration` → `ux-assembly-retrieve.md` | — (visibility per permission set is checked at the build gate) |
| Grouping lines | Line groups in the Transaction Line Editor | `ramped-quotes` (groups); Help | — |
