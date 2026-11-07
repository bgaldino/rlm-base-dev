# Promotion Execution (`PromotionExecution`)

> Release 264 / API v68.0. Sources: `ind.pricing_promotion_execution_element.htm`
> (stub); shipped XML: none; core source (behavior only).

Connects Global Promotions Management (GPM) with Revenue Management: executes
the applicable promotions for the transaction line items.

## When to use it

- Applying GPM promotions during pricing. [Help]
- Help defers all how-to detail to "Configure Your Pricing Procedure for Promotions in Revenue Cloud" (a separate article, not in this skill's sources).

## actionType

Core registers several promotion-related actionTypes:

| actionType | Min platform release | Note |
|---|---|---|
| `PromotionExecution` | 258 | Builder "Promotion Execution"; matches the Help article name. [Core] |
| `GPMPromotionExecution` | 264 | GPM variant, same icon. [Core] |
| `AdvancedPromotionExecution` | 264 | Separate component. [Core] |
| `PromotionsDiscount` | older | Earlier promotions discount element. [Core] |

Builder registry [Core]: one `actionType` per Builder element, offered by org enablement.

| Builder element | Written `actionType` | Offered when |
|---|---|---|
| Promotion Execution | `PromotionExecution` | GPM / Revenue Cloud integration enabled, or Pricing Lite |
| Advanced Promotion Execution | `AdvancedPromotionExecution` | Core pricing plus CME promotions enabled |
| GPM Promotion Execution | `GPMPromotionExecution` | Unified Promotions (or Basic + Standalone) enabled |
| Promotions Discount | `PromotionsDiscount` | Custom pricing element pilot |

In a 264 org with Unified Promotions expect `GPMPromotionExecution`; confirm by retrieving a Builder-saved procedure.

## Configuration

`PromotionExecution`, keyed by literal `PromotionScope` [Core]:

| Scope | Required inputs | Outputs |
|---|---|---|
| `Order` (header) | header id, header subtotal | header subtotal after promotions |
| anything else (line) | quantity, input unit price, input subtotal; optional pricing-term count (promotion beta orgs) | `NetUnitPrice`, `Subtotal` |

Input names are context-tag names (e.g. `LineItemQuantity`, `InputUnitPrice`, as in other shipped steps; inferred). The Builder shows no lookup, additional variables or Hide in waterfall for it. Parameters of `GPMPromotionExecution` and `AdvancedPromotionExecution` are unconfirmed: build in Builder and retrieve.

## Placement and ordering

- Not stated in Help. Price Propagation is incompatible with Promotions elements in the same procedure. [Help]; see [price-propagation.md](./price-propagation.md)
- Cross-element order: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).

## Rules and limits

None documented in the Help stub beyond the above.

## Metadata shape

```xml
<steps>
  <actionType>PromotionExecution</actionType>
  <customElement><!-- line scope: PromotionScope literal; quantity, unit price, subtotal inputs; NetUnitPrice, Subtotal outputs --></customElement>
  <name>__STEP_NAME__</name>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

## Shipped in this repo (snapshot)

None (no `PromotionExecution`, `GPMPromotionExecution` or `AdvancedPromotionExecution`
step in the shipped procedures). Discover live:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

Simulate a transaction that qualifies for a promotion and inspect the JSON
output for the discount; confirm GPM promotion setup first (outside this skill).

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| Promotion not applied | Promotion not set up or not active in GPM | Verify in GPM (inferred) |
| Propagation procedure misprices | Propagation plus Promotions in one procedure | Do not combine [Help] |

## Open questions

- Parameters of the GPM and Advanced variants; placement relative to Manual Discount and the tail: live org.
- Runtime differences between the three variants.
