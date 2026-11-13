# Concept Map — Commercial Concepts to Revenue Cloud

Read this when mapping a source with [implementation-planning](SKILL.md). Each row
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
| Not sold standalone | `IsSoldOnlyWithOtherProds`. The only refusal measured is at category assignment: Place, order and activation accepted the product alone, so a quote that must never sell it alone needs its own check | `product-catalog-modeling` → `selling-models-and-lifecycle.md` |
| Not tracked in the installed base | `IsAssetizable = false` on a standalone product or a bundle root (the root's value applies to every child). Under an assetizable root a non-assetizable child still becomes an asset, so a child that must stay out of the installed base becomes a separate line | same (`IsAssetizable`) |
| Product lines, categories, catalogs | Catalog categories and `Family` | `product-catalog-modeling` → `catalogs-and-loading.md` |
| Part number per configuration | Attribute set by CML from the selection. No skill covers building one value from several selections; record it as a skill gap | — (`elements/root-answer-child-price.md` route 1 shows CML setting a child attribute, unmeasured) |

## Configuration and rules

| Source concept | Try first | Where documented |
|---|---|---|
| Sizing questions | Attributes on the bundle root | `constraint-models` → `quantities-from-attributes.md` |
| Quantity derived from answers (one per user, one per block of N rounded up) | CML cardinality constraints driven by `int` variables, with an integer bracket for rounding up | `constraint-models` → `quantities-from-attributes.md` (`ceil()` doesn't round inside a constraint) |
| Effort or hours estimator | Same, on service components | same |
| "X only with Y", "exactly one of" | CML constraints with messages. Before holding an "exactly one of" choice as a component group, check the source's changes: a later change that splits units across the choices can't run under a one-of group (prediction-checks.md check 5) | `constraint-models`; `product-catalog-modeling` Quick Rule 3 |
| Note that doesn't block | CML message with `Info` severity. `Warning` blocks the next step until the rep acts | `constraint-models` → `quantities-from-attributes.md` |
| Rep may change a quantity the rules size | Decide which wins: rule-owned sizing, or an editable line | `constraint-models` → `quantities-from-attributes.md` |

## Pricing

| Source concept | Try first | Where documented |
|---|---|---|
| Volume bands by quantity | Volume and tier discounts, price adjustment schedule | `pricing-procedures` → `elements/volume-and-tier-discount.md`; `pricing-setup` → `price-adjustment-schedules.md` |
| Discount when bought in a package | Bundle-based adjustment | `pricing-procedures` → `elements/bundle-based-price.md` |
| Regional or channel uplift | A documented route first: CML copies the root answer to a price-impacting child attribute plus an attribute-based price; formula-based pricing on a header value; or a price adjustment matrix over a lookup table. The first was built and measured end to end on a fresh scratch org; the other two are documented but unmeasured (open), and the attribute adjustment matrix is unverified. Each route needs different catalog and model pieces (the first, a price-impacting attribute on the children's classification and a CML line): list them per route (SKILL step 6) | `pricing-procedures` → `elements/root-answer-child-price.md` |
| Order of application, rounding | Procedure element order, rounding element | `pricing-procedures` → `procedure-anatomy-and-ordering.md`, `elements/rounding-values.md` |
| Second currency | Multicurrency price book entries, and per-currency rows for every adjustment that matches on currency (volume tiers, bundle-based adjustments) as well as cost entries. Where the source costs items in one currency only, decide converted cost entries or no margin in the other: a line without a cost entry shows no margin, not zero margin. An approval threshold stated in one currency needs a decision for quotes in the other | `pricing-setup` (→ `scenarios/cost-and-margin.md` for missing costs), `sfdmu-data-plans` |
| Annual escalator | Group ramp with uplift. On a mixed bundle decide which lines escalate: in a UI-built Compound ramp (Standard and API-built not measured), the segment uplift reaches every ramp-stamped line (`UnitPriceUplift` 0 exempts one; a line without a `RampIdentifier` took no uplift, one org, so check whether any line still needs exempting), a UI-built bundle ramp puts every child in every segment and quotes a one-time child once per segment, and a compound uplift isn't rounded to the cent, so if the source rounds, round after it. If the plan amends or cancels such a ramp, note that an API-built group-ramped bundle with a one-time or evergreen child failed to amend, and in one shape to cancel (`asset-lifecycle-changes` Quick Rule 8; `ramped-quotes` → `bundle-children-lifecycle.md`) | `ramped-quotes` → `bundle-children-lifecycle.md`, `ui-group-ramp.md`; `pricing-procedures` → `elements/price-revision-compound-uplift.md` |
| Renewal uplift | Price revision policy. Renewal uplifts apply only to term-defined selling models (Help: `ind.qocal_renewal_price_uplifts`), so an Evergreen line takes none. A policy and uplift set on the new-sale lines reached the renewal | `pricing-setup` → `price-revision-policies.md`; `asset-lifecycle-changes` → `change-policy-mapping.md` |
| Discount for a longer commitment | List filter on term plus a formula step on Term Defined lines. If the discount must also apply inside a group ramp, note that segment lines of a UI-built ramp carried a term of 1 (state the term for every way the plan creates ramp lines: [prediction-checks.md](prediction-checks.md) check 12), so the filter needs the file's criterion 14 (`ItemRampIdentifier` IsNotNull), ORed with the term criteria as in the file's filter logic. That criterion admits every ramp segment line whatever the ramp's length (inferred from the filter), so if the discount depends on the commitment's length, record how a short ramp is kept out as a decision | `pricing-procedures` → `elements/commitment-term-discount.md` |
| A policy the source marks approved but not yet applied in its calculator | Build it behind a quote-level switch the procedure reads; run the source's goldens with it off and the policy's own examples with it on. A policy that changes the quote's structure (an escalator built as a ramp) isn't a procedure branch: the source's goldens run without that structure and the policy's own examples with it, so it needs no switch of its own. Ask whether the policies stack, whether one switch can serve every policy the procedure applies, and for each policy's effective date | `pricing-procedures` → `elements/commitment-term-discount.md` (a header checkbox mapped into the context as a `SalesTransaction` tag, read by a list filter: measured; a header-only Place PATCH didn't reprice the lines, Reprice All did). A formula reading the header field (`elements/root-answer-child-price.md`, route 2) is documented but unmeasured |
| Price from cost and a target margin | Formula step on a cost looked up from a decision table | `pricing-setup` → `cost-books.md`, `scenarios/cost-and-margin.md`; `pricing-procedures` → `elements/formula-based-pricing.md` |

## Cost and margin

| Source concept | Try first | Where documented |
|---|---|---|
| Standard cost per item | Cost book entries | `pricing-setup` → `cost-books.md`, `scenarios/cost-and-margin.md` |
| Labour rates, loaded cost | Computed during extraction into cost entries | `pricing-setup` → `scenarios/cost-and-margin.md` (modeling costs from a source) |
| Line and quote margin | The shipped cost-and-margin wiring, plus a roll-up for the quote total | `pricing-setup` → `scenarios/cost-and-margin.md` |
| Contract value that counts until-cancelled lines over a fixed term | A computed value of its own, gated on every quote structure the plan builds: ramp segments, amendments, renewals (prediction-checks.md check 8); a quote total counts an Evergreen line without an end date for one period, not the source's term (measured in `scenarios/full-term-value.md`). The shipped procedure's `EvergreenPricingTermCountConstant` sets 1, which matches the fresh-org Setup default; check both (`proration-and-selling-models.md` → Default term counts). Don't raise that count to get a full-term figure; it changes every Evergreen price. Read the default counts in Setup at P0 (no API is known; template P0) | `pricing-setup` → `scenarios/full-term-value.md`, `proration-and-selling-models.md`, `scenarios/cost-and-margin.md` |
| A fee or commission computed from the deal's revenue | A computed value (a field or a formula), not a price adjustment. Check which deals it applies to. Over one product line only, check the field that selects the lines is in the pricing context: the sales transaction context has no product Family | `pricing-setup` → `scenarios/full-term-value.md` |
| Items resold at or near cost | Priced near cost by design; decide how margin and below-cost guards and discounts treat them | `pricing-setup` → `scenarios/cost-and-margin.md`; `advanced-approvals` → `matrix-modeling.md` |

## Billing

| Source concept | Try first | Where documented |
|---|---|---|
| Billing frequency (annual, monthly) | `BillingFrequency` set on every Term Defined and Evergreen line placed through the API (a Term Defined line without one was refused). A cadence different from the pricing term needs a treatment that allows it | `billing-setup` |
| In advance vs in arrears; milestone billing | Billing policy and treatment. Milestones the source doesn't name are a decision for its owner, not invented. Decide how amendments bill too: a quantity increase on a milestone-billed service is measured in `billing-setup`, but a service the amendment adds is open there, so record it as an open decision | `billing-setup` (amendments) |
| Payment terms | `Order.PaymentTermId` for invoicing; the shipped approval reads a custom quote picklist, and nothing copies one to the other. Decide how they meet | `billing-setup`; `advanced-approvals` |
| Non-standard billing as an approval trigger | A quote-level value computed from the lines' billing frequency (in the approval data flow, or a roll-up count of non-standard lines) that the approval condition tests | `advanced-approvals` → `matrix-modeling.md` |

## Negotiation and approvals

| Source concept | Try first | Where documented |
|---|---|---|
| Rounds or versions of a bid | One quote per round, by deep clone; the winning round becomes the order | `quote-negotiation-rounds` |
| An internal what-if round that must never be presented | A marker on the quote plus a guard on presenting and ordering it | `quote-negotiation-rounds` |
| Discount per product line | Manual line discounts. A line-editor group discount is open: unmeasured inside a bundle, and Propagation ships off. Not a header discount: it was measured applying twice with an active procedure plan and `skipOrgSttPricing` on | `pricing-procedures` → `elements/manual-discount.md`, `elements/price-propagation.md`; `transaction-line-editor` → `runtime-behavior.md` |
| Approval matrix by discount, margin, size | Advanced Approvals: one level per dimension, the maximum drives a cumulative chain. State what "discount" is measured against (list, or a standard price after programs). Give every quote-level dimension a basis on amendments, not only deal size (prediction-checks.md check 8) | `advanced-approvals` → `matrix-modeling.md` (deal size only) |
| Line-level guards (below floor, below cost) | A count of breaking lines as an approval condition, with a marker so a round's bulk discount and an individual override can be told apart; name what sets the marker on each path. A line the round leaves undiscounted by design (resold at cost, priced to a target margin) needs, if the override test compares a line's discount with the round's marker, a marker equal to its own discount or a flag that keeps it out of the test (as `matrix-modeling.md` does for pass-through lines); otherwise it reads as an override `[inferred]` | `advanced-approvals` → `matrix-modeling.md` |
| "Resubmit from the start" after a rejection | Smart Approval off on that chain's steps, or accepted as a difference | `advanced-approvals` → `matrix-modeling.md`, `limitations.md` |

## Lifecycle

| Source concept | Try first | Where documented |
|---|---|---|
| Co-termed addition | Amendment of the top-level asset. On a bundle sized from root answers, decide how "add N" maps onto the root. Added units on a `LastTransaction` asset took the last net price and didn't re-band; re-banding needed a procedure overlay (**Build (custom)**). Partial periods prorate by day | `asset-lifecycle-changes` → `change-policy-mapping.md`; `pricing-setup` → `proration-and-selling-models.md`; for a backdated replay only, `rlm-business-apis` → `backdated-asset-lifecycle.md` |
| Swap one plan for another | Swap action | `asset-lifecycle-changes` |
| Cancellation credit | Cancellation | `asset-lifecycle-changes` → `change-policy-mapping.md` |
| Renewal at a new price | Renewal with a price revision policy. On a last-transaction pricing source each lot renewed from its own last price (conditions in `asset-lifecycle-changes` Quick Rule 4), and a multi-year renewal needs `renewalEndDate` (a 3-year new-sale line still left a 1-year renewal term) | `asset-lifecycle-changes` (Quick Rule 4, `change-policy-mapping.md`); `pricing-setup` → `price-revision-policies.md`; `renewal-asset-creation` for renewal test data only |
| Proving a change end to end | Reprice, order, activate, check the asset | `asset-lifecycle-changes` → `verification.md` |

## Runtime surface

| Source concept | Try first | Where documented |
|---|---|---|
| Columns the rep needs (margin, product line, uplift) | Line editor display columns | `transaction-line-editor` → `page-configuration.md` |
| Grouping lines | Line groups in the line editor | `transaction-line-editor`; `ramped-quotes` (groups) |
| Header actions (reprice, ramp schedule, header adjustment) | Line editor action buttons | `transaction-line-editor` |
