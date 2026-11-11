# Attribute Adjustment Matrix (`AttributeAdjustmentMatrix`)

> Release 264 / API v68.0. Sources: dev guide `meta_expressionsetdefinition.htm`
> (actionType enum list only); core source (behavior only). Not in the Help corpus,
> not shipped in this repo, not exercised on a live org.

A Builder element that adjusts the unit price from per-product attribute rules held in
a separate matrix store. Builder name is "Attribute Adjustment Price". It is **not**
[price-adjustment-matrix.md](./price-adjustment-matrix.md) (bring-your-own decision
table) and **not** [attribute-based-price.md](./attribute-based-price.md)
(`AttributeDiscount`, Attribute Based Adjustment records plus a decision table). [Core]

## Status
- Real, selectable element: registered in the Builder element list and in the
  Revenue Cloud pricing usage type's allowed-element set. [Core]
- Minimum version marker on the enum value is 260. [Core] The marker is a release
  number; whether it equals a specific API version was not checked [inferred].
- The dev guide lists `AttributeAdjustmentMatrix` among valid `actionType` values
  with no version note and no description. [Dev guide]
- No Help article describes the element or its authoring UI (searched the 264 Help
  corpus for "attribute adjustment matrix"; only Attribute Based Adjustment articles
  match, and those document `AttributeDiscount`). [Help]
- Product, Product Classification and Price Adjustment Schedule record pages carry an
  "Attribute Adjustment Matrix" tab. [Core] The tab's authoring behavior and any org
  setting or pilot gating it was not found; treat the element as undocumented and
  verify on the target org before relying on it. [inferred]

## Configuration (Builder element settings)
| Setting | Value | Source |
|---|---|---|
| Lookup table | disabled (no decision table) | [Core] |
| Contract pricing | disabled | [Core] |
| Output Resolution | disabled (no strategy, no Use As List) | [Core] |
| Hide Waterfall | available | [Core] |
| Profile filter | shown | [Core] |
| Additional variables | enabled | [Core] |
| Where-condition, added-parameter, group-by and profile counts | platform default limits | [Core] |

## Formal parameters
| Parameter | Type | Flags (true,true = required input) | Notes |
|---|---|---|---|
| `Product2Id` | Text | true,true | Builder label "Product" |
| `PriceAdjustmentSchedule` | Text | true,true | Schedule Id; appended to the lookup key as `_<id>` when present |
| `ProductSellingModelId` | Text | true,true | |
| `ProductBasedOn` | Text | true,true | Product classification Id, fallback key |
| `Quantity` | Numeric | true,true | |
| `InputUnitPrice` | Currency | true,true | |
| `AttributeName` | Text | false,true | Multi-valued |
| `AttributeValue` | Text | false,true | Multi-valued; paired by position with `AttributeName` |
| `EffectiveFrom`, `EffectiveTo` | DateTime | false,true | |
| one per matrix input column | per column | per column | Added from the matrix definition; also the extra rule-tree inputs |

All [Core]. Reading the two flags as (required, input) is [inferred]. Outputs are
`NetUnitPrice` and `Subtotal`. [Core]

## What it reads and writes
1. Collects product reference ids for the lines, reads matrices of the attribute
   adjustment type for them in bulk, builds one rule tree per product reference. [Core]
2. Per line: key = `Product2Id` (+ `_` + schedule id); falls back to the
   `ProductBasedOn` key. No match means the line is skipped and counted as having no
   matrix; no product id or classification id means the line is skipped with a warning. [Core]
3. Rule inputs come from tags named like the rule columns; range columns use the base
   name. A missing or blank tag is replaced by a sentinel so it cannot match. Attribute
   name/value tags are paired into extra inputs only if their counts are equal. [Core]
4. Matched rules are sorted by priority then sequence; only rules at the lowest
   priority value are applied, in sequence order, each on the previous result. [Core]
5. Writes `NetUnitPrice` and `Subtotal` (= quantity x new unit price) only when a
   `Quantity` tag exists; skips the line if `InputUnitPrice` is null. [Core]
6. Adds one entry per applied rule to the waterfall: original price, adjusted price,
   adjustment type and value, rule conditions, rule sequence, priority. [Core]

Adjustment types (case-insensitive): Override (value is the price), Amount (price
minus value), Percentage (price x (100 - value) / 100), MarkupAmount (price plus
value), MarkupPercentage (price x (100 + value) / 100). A rule with a blank type or
value stops the loop for that line (earlier rules stay applied). [Core]

## Placement
Follows the generic rules in [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md): after Pricing Setting and the list price, before DDS and the aggregates. It writes `NetUnitPrice` from `InputUnitPrice`, so stage `InputUnitPrice` first. No element-specific ordering check was found [Core][inferred].

## Metadata shape
None to copy: nothing ships here and no Builder-saved step has been captured. Build it from a live org's export (`export_expression_set_overlay.py`) rather than from the parameter table above, and add the captured step here. [inferred]

## Runtime errors
| Code | User-facing message | When |
|---|---|---|
| `DUPLICATE_RULE_FOUND` | "Duplicate rules found with same Priority and Sequence" | Two matched rules share priority and sequence at the lowest priority value; line not priced by this step. [Core] |
| `INVALID_INPUT` | "The adjustment type for this line item must be set to Override." | Unrecognised adjustment type. The message text is reused from the label Manual Discount and Bundle-Based Price raise for a null input unit price; here the trigger is the type, not the price [Core]. |

Failures reading the matrix store or building a rule tree are logged, not surfaced;
the affected lines are simply unadjusted. [Core]

## Save-time rules
None found for this element beyond the generic element settings above. [inferred]
(Searched the element's metadata definition and Builder configuration; no
element-specific validation message.)

## Not shipped here
No shipped expression set in `force-app/`, `unpackaged/post_procedureplans/` or
`unpackaged/post_prm_pricing/` uses `AttributeAdjustmentMatrix` (repo-wide search). [Repo]

## Verify
Simulate with attribute name/value tags hydrated; inspect the waterfall for the
attribute adjustment entries. If nothing applies, check the product (or classification)
has a matrix for the schedule and that `AttributeName`/`AttributeValue` counts match.
