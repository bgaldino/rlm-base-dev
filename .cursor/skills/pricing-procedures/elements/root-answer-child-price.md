# Child price from a bundle-root answer

> Pattern file under `elements/`, like [`commitment-term-discount.md`](commitment-term-discount.md):
> it combines existing elements (and a constraint model) rather than documenting a new one.
> Release 264 / API v68.0. Sources: dev guide `cml_using_proxy_variables_constraints.htm`
> (*Parent*), `cml_best_practice_parent_products.htm`; Help
> `ind.pricing_attribute_based_pricing_limits.htm`,
> `ind.pricing_add_the_price_adjustment_matrix_element.htm`; shipped
> `RLM_PRM_DISTI_Pricing_Procedure` and `datasets/context_plans/PartnerAccount/contexts/partner_account.json`.
> Nothing in this file was built or measured.

The need: a child line's price depends on an answer given on the bundle root. Example: a suite
bundle asks for a Region on the root, and its Software and Support child lines take a regional
uplift. The documented routes move the answer to a place a pricing element reads: onto the child
line itself, or onto the header. Which route works live is [open](#open-questions).

## Route 1: CML copies the answer to a child attribute, then Attribute-Based Price

- **Configurator side.** `parent(<attribute>)` reads an attribute of the immediate parent type, and
  `parent(<attribute>, <level>)` an ancestor further up. Reusing the parent's variable name on the
  child is the documented way to cascade a bundle-level choice to every child; the dev guide's
  example does exactly that and notes the inherited value can affect price
  [Dev guide: `cml_using_proxy_variables_constraints.htm`, *Parent*]. For the example, the child
  type declares `string Region = parent(Region);`. Under a Product Component Group the group is an
  intermediate parent, so reach the root with `parent(Region, 1)` or dot notation from the bundle
  [Dev guide: `cml_best_practice_parent_products.htm`]; the dev guide contradicts itself here, see
  [`../../constraint-models/quantities-from-attributes.md`](../../constraint-models/quantities-from-attributes.md)
  → Scope. Authoring and deployment: [`../../constraint-models/SKILL.md`](../../constraint-models/SKILL.md).
- **Pricing side.** Make `Region` a price-impacting attribute on the child product's own
  classification, not an inherited one, and do not override it in the bundle context: the override
  stops the adjustment applying [Help: `ind.pricing_attribute_based_pricing_limits.htm`]. Then add
  an Attribute Based Adjustment per region value on the child products. Matching, the
  whole-attribute-set rule and schedule setup are in [`attribute-based-price.md`](attribute-based-price.md);
  attribute placement in
  [`../../product-catalog-modeling/attributes-and-classifications.md`](../../product-catalog-modeling/attributes-and-classifications.md).

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
  region and the product, so only the affected children match.
- The shipped PRM procedure already runs a Price Adjustment Matrix per line keyed on a header tag
  (`PartnerAccount__c`) [Repo: `RLM_PRM_DISTI_Pricing_Procedure`, `partner_account.json`], so the
  region can come from the header as in route 2. Keying on a line tag such as route 1's child
  attribute is marked [inferred] in that file.
- Choose this route when business users must maintain the uplifts as data.

`AttributeAdjustmentMatrix` (Builder "Attribute Adjustment Price") is **unverified** for this:
it has no Help article and was never exercised
([`attribute-adjustment-matrix.md`](attribute-adjustment-matrix.md)).

## Open questions

- **Open — needs live verification:** which route works live. None was built or measured.
- Route 1: whether a value the constraint model sets on a child attribute is saved on the line and
  hydrated into the pricing context before Attribute-Based Price runs.
- Routes 2 and 3: how the root answer reaches the header (a rep enters it on the quote, or
  automation copies it from the root line); nothing in the 264 snapshot documents a copy.
- An uplift with Attribute-Based Price or a Price Adjustment Matrix: Percentage multiplies by
  (100 − v)/100 ([`attribute-based-price.md`](attribute-based-price.md) → Rules and limits), so an
  uplift needs a negative value or an Override; whether either is accepted for this was not checked.
- Whether any element reads the root line's attribute directly from a child line.
