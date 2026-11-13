# Child price from a bundle-root answer

> Pattern file under `elements/`, like [`commitment-term-discount.md`](commitment-term-discount.md):
> it combines existing elements (and a constraint model) rather than documenting a new one.
> Release 264 / API v68.0. Sources: dev guide `cml_using_proxy_variables_constraints.htm`
> (*Parent*), `cml_best_practice_parent_products.htm`; Help
> `ind.pricing_attribute_based_pricing_limits.htm`,
> `ind.pricing_add_the_price_adjustment_matrix_element.htm`; shipped
> `RLM_PRM_DISTI_Pricing_Procedure` and `datasets/context_plans/PartnerAccount/contexts/partner_account.json`.
> Route 1 was built and measured end to end on a fresh 264 `ent-sb0` scratch org on 2026-11-11,
> configuration rules on; routes 2 and 3 were not built.

The need: a child line's price depends on an answer given on the bundle root. Example: a kit
bundle asks for a ClimateZone on the root, and its Installation and Warranty child lines take a climate-zone
uplift. The documented routes move the answer to a place a pricing element reads: onto the child
line itself, or onto the header. Route 1 works live; routes 2 and 3 are [open](#open-questions).

## Route 1: CML copies the answer to a child attribute, then Attribute-Based Price

- **Configurator side.** `parent(<attribute>)` reads an attribute of the immediate parent type, and
  `parent(<attribute>, <level>)` an ancestor further up. Reusing the parent's variable name on the
  child is the documented way to cascade a bundle-level choice to every child; the dev guide's
  example does exactly that and notes the inherited value can affect price
  [Dev guide: `cml_using_proxy_variables_constraints.htm`, *Parent*]. For the example, the child
  type declares `string ClimateZone = parent(ClimateZone);`. Under a Product Component Group the group is an
  intermediate parent, so reach the root with `parent(ClimateZone, 1)` or dot notation from the bundle
  [Dev guide: `cml_best_practice_parent_products.htm`]; the dev guide contradicts itself here, see
  [`../../constraint-models/quantities-from-attributes.md`](../../constraint-models/quantities-from-attributes.md)
  → Scope. Live, `parent(ClimateZone)` with no level reached the root in a model that declares no
  group types ([Route 1 measured](#route-1-measured)). Authoring and deployment: [`../../constraint-models/SKILL.md`](../../constraint-models/SKILL.md).
- **Pricing side.** Make `ClimateZone` a price-impacting attribute on the child product's own
  classification, not an inherited one, and do not override it in the bundle context: the override
  stops the adjustment applying [Help: `ind.pricing_attribute_based_pricing_limits.htm`]. Then add
  an Attribute Based Adjustment per ClimateZone value on the child products. Matching, the
  whole-attribute-set rule and schedule setup are in [`attribute-based-price.md`](attribute-based-price.md);
  attribute placement in
  [`../../product-catalog-modeling/attributes-and-classifications.md`](../../product-catalog-modeling/attributes-and-classifications.md).

### Route 1 measured

Built on a Place Sales Transaction quote (`configurationMethod: Force`,
`configurationOptions.executeConfigurationRules: true` in `configurationPref`) and in the configurator UI [Measured: 2026-11-11, 264, fresh
`ent-sb0` scratch org; attribute names illustrative]:

- **Only the root carries the answer.** The request set ClimateZone on the root line alone. The model
  wrote the child's `QuoteLineItemAttribute`, and Attribute-Based Price priced the child from it. So the value is saved on the line and
  hydrated into the pricing context before that step. In the configurator UI the children took
  the root's value too (with a value that has no adjustment row, so no uplift was priced there).
- **`parent(ClimateZone)` with no level reached the root** from children that sit in a product
  component group, in a model that declares no group types. Whether a model that declares group
  types needs the level argument was not measured.
- **Top-level lines.** A top-level line held by a virtual `Quote` container relation received the
  root's answer through `parent()`; on a quote with no bundle the line kept the attribute default, and a child
  under a root outside the model kept its default [Measured: 2026-11-11, 264, scratch; one org, attribute
  illustrative]. In a build whose top-level support line sat in that container, regional deals priced to
  their expected values with the line's attribute set from the root's answer (one standalone line type, regional
  adjustment on the line's classification) [Measured: 2026-11-11, 264, scratch, one org; the run did not isolate
  that line's own price from the child lines'], so the held line is priced from the answer, not only handed it.
  A support-only quote (no bundle) kept the default. Assert it at the catalog gate; details in
  [`quantities-from-attributes.md`](../../constraint-models/quantities-from-attributes.md) (M42).
- **Catalog set-up used:** each affected child is based on a classification that carries
  the attribute directly, with a Product Attribute Definition marking it price-impacting. So
  route 1 spans the catalog, the constraint model and the pricing data: plan and load them
  together.
- **The uplift is a negative Percentage.** An Attribute Based Adjustment of type Percentage with
  a negative `AdjustmentValue` −n is accepted on insert and applied as × (100 + n)/100 (−5 gives
  × 1.05); no Override is needed. Loading notes: [`attribute-based-price.md`](attribute-based-price.md) →
  Rules and limits.
- **Order in the waterfall:** list price, then the attribute-based uplift, then the bundle-based
  and volume discounts, each on the previous net, as the shipped phase order puts them
  ([`../procedure-anatomy-and-ordering.md`](../procedure-anatomy-and-ordering.md), phase 7).
- **Editing the root answer reprices.** A Place PATCH of only the root's `QuoteLineItemAttribute`
  (rules on) re-derived the child's attribute and repriced the child lines.

## Route 2: Formula-Based Pricing reads a header tag

- A line formula reads the line's tags and the tags of its parent context nodes, header tags
  included ([`formula-based-pricing.md`](formula-based-pricing.md) → Placement, a [Core] note). The
  Help article for the element does not cover header tags [Help: `ind.pricing_formula_based_pricing.htm`, checked].
- The answer has to be a header field mapped to a `SalesTransaction` node tag, the shape the shipped
  `PartnerAccount__c` tag uses (mapped from `Quote.PartnerAccountId`)
  [Repo: `datasets/context_plans/PartnerAccount/contexts/partner_account.json`]. A custom field must
  also be mapped into the context definition before a formula can read it
  ([`formula-based-pricing.md`](formula-based-pricing.md) → Rules and limits).
- Put the formula in a List Group whose filter keeps only the affected lines
  ([`list-group-and-list-operation.md`](list-group-and-list-operation.md)), write `NetUnitPrice`,
  and guard a null header value with `ISNULL`.

## Route 3: Price Adjustment Matrix over a custom table

- The element applies adjustments from custom decision tables whose criteria can be quote details,
  customer info or product attributes, linked to quote fields
  [Help: `ind.pricing_add_the_price_adjustment_matrix_element.htm`]. Recipe registration,
  single-row matching and refresh are in [`price-adjustment-matrix.md`](price-adjustment-matrix.md). Key the table on the
  climate zone and the product, so only the affected children match.
- The shipped PRM procedure already runs a Price Adjustment Matrix per line keyed on a header tag
  (`PartnerAccount__c`) [Repo: `RLM_PRM_DISTI_Pricing_Procedure`, `partner_account.json`], so the
  climate zone can come from the header as in route 2. Keying on a line tag such as route 1's child
  attribute is marked [inferred] in that file.
- Choose this route when business users must maintain the uplifts as data.

`AttributeAdjustmentMatrix` (Builder "Attribute Adjustment Price") is **unverified** for this:
it has no Help article and was never exercised
([`attribute-adjustment-matrix.md`](attribute-adjustment-matrix.md)).

## Open questions

- **Open — needs live verification:** routes 2 and 3; neither was built. How the root answer
  reaches the header for them (a rep enters it on the quote, or automation copies it from the
  root line) is also open; nothing in the 264 snapshot documents a copy.
- An uplift through a Price Adjustment Matrix: its Percentage is a discount too (a Percentage
  above 100 may go negative, [`price-adjustment-matrix.md`](price-adjustment-matrix.md) → Rules
  and limits), so an uplift needs a negative value or an Override; whether either is accepted
  there was not checked. Attribute-Based Price accepts a negative
  Percentage (route 1 above).
- Whether any element reads the root line's attribute directly from a child line.
