# Promotion Execution (`PromotionExecution`)

> Release 264 / API v68.0. Sources: `ind.pricing_promotion_execution_element.htm`
> (stub); shipped XML: none; core source (behavior only).

Connects Global Promotions Management (GPM) with Revenue Management: executes
the applicable promotions for the transaction line items.

## When to use it

- Applying GPM promotions during pricing. [Help]
- Help defers all how-to detail to "Configure Your Pricing Procedure for Promotions in Revenue Cloud" (a separate article, not in this skill's sources). The Help article is a stub: it states the purpose and editions only, no parameters or rules [Help]..

## actionType

Core registers several promotion-related actionTypes:

| actionType | Min platform release | Note |
|---|---|---|
| `PromotionExecution` | 258 (API 65.0) | Builder "Promotion Execution"; matches the Help article name. [Dev guide] lists it as available from API 65.0 (Release 258); also in the core enum. |
| `GPMPromotionExecution` | not documented | GPM variant, same icon. Absent from the [Dev guide] actionType enum (`dev-guide-industries` ExpressionSetDefinition article); first release [inferred] 264. |
| `AdvancedPromotionExecution` | not documented | Separate component. Absent from the [Dev guide] enum; first release [inferred] 264. |
| `PromotionsDiscount` | listed in the [Dev guide] enum with no version note | Earlier promotions discount element; Builder offers it only with the custom pricing element pilot [Core]. |

Builder registry [Core]: one `actionType` per Builder element, offered by org enablement (Builder element-exposure checks).

| Builder element | Written `actionType` | Offered when |
|---|---|---|
| Promotion Execution | `PromotionExecution` | Global Promotions / Revenue Cloud integration enabled, or Pricing Lite (independent of core pricing access) |
| Advanced Promotion Execution | `AdvancedPromotionExecution` | Core pricing access and CME promotions both enabled |
| GPM Promotion Execution | `GPMPromotionExecution` | Unified Promotions (or Basic + Standalone) enabled |
| Promotions Discount | `PromotionsDiscount` | Custom pricing element pilot (exposed together with `ApexAction`) |

In a 264 org with Unified Promotions expect `GPMPromotionExecution`; confirm by retrieving a Builder-saved procedure.

## Configuration

`PromotionExecution` and `GPMPromotionExecution` have identical parameters, keyed by literal `PromotionScope` [Core]:

| Scope | Inputs (required unless noted) | Outputs |
|---|---|---|
| `Order` (header) | `HeaderId` (Text), `HeaderSubtotal` (Currency) | `OutputHeaderSubtotal` |
| anything else (line) | `Quantity` (Numeric), `InputUnitPrice` (Currency), `InputSubtotal` (Currency); optional `PricingTermCount` (Numeric, only in orgs with promotion beta features) | `NetUnitPrice`, `Subtotal` (Currency) |

GPM additionally exposes extra input tags derived from the promotion rule library. Both accept Line, Order and CrossLine scope, except that `PromotionExecution` with an RLM promotions library (`GlobalPromotionsForRLM`) must use Line (`INVALID_PROMOTION_SCOPE`, below). [Core]

`AdvancedPromotionExecution` [Core]: inputs `Quantity`, `InputUnitPrice`, `InputSubtotal`, `PricingTermCount` (all required, including `PricingTermCount`); outputs `NetUnitPrice`, `Subtotal`. It also reads context tags (selling model type, start date, pricing term unit, period boundary day/month, partial proration, subscription term, existing price-adjustment and sales-transaction-item nodes). Line scope only.

`PromotionsDiscount` [Core]: inputs are the lookup table's input columns plus required `Quantity`, `InputUnitPrice`, `DiscountType` (Text), `DiscountValue` (Numeric), `AdjustmentImpactingField` (Text), `PromotionSequence` (Numeric) and optional `PromotionDescription` (Text). No outputs are declared at design time; at run time it writes `NetUnitPrice` and `Subtotal`. Builder shows Hide in waterfall, profile filter and additional variables; no contract pricing.

The first three show no Builder lookup, contract pricing, Hide in waterfall, profile filter or additional variables. [Core] Advanced requires a promotion rule library on the procedure's context definition (see Rules and limits). Input names are context-tag names (e.g. `LineItemQuantity`, as in other shipped steps; [inferred]).

## Placement and ordering

- Not stated in Help. Price Propagation is incompatible with Promotions elements in the same procedure [Help]. Core rejects `PromotionExecution` (not `GPMPromotionExecution`; Advanced only for the Communications subtype); see [price-propagation.md](./price-propagation.md)
- Cross-element order: [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md).

## Rules and limits

Save-time rules (core rejects the procedure when saved). Exact error text is in the
table in [../procedure-anatomy-and-ordering.md](../procedure-anatomy-and-ordering.md#save-time-procedure-rules-core-enforces):

| Rule | Source |
|---|---|
| Promotion Execution (default handler) or Advanced Promotion Execution (Communications/Media/Energy strategy) and Derived Price cannot coexist. `GPMPromotionExecution` is not part of this rule, and the GPM usage subtype does not allow Derived Price anyway [inferred] | [Core] |
| After Advanced Promotion Execution only Assignment, Formula, Aggregation or List Group steps may follow | [Core] |
| The promotion rule library must exist, use the procedure's context definition and be a promotions library | [Core] |
| Price Propagation cannot be combined with promotion execution (incompatible-elements error) | [Core] |
| `PromotionScope` must be a supported value (`INVALID_PROMOTION_SCOPE`) | [Core] |

`INVALID_PROMOTION_SCOPE`: "We can't save this procedure. Specify Line as the Promotion Scope when the Rule Library usage type is set to GlobalPromotionsForRLM and try again." Fires for a non-Line scope on `PromotionExecution` with an RLM promotions library, and for any non-Line or empty scope on Advanced. [Core]

Runtime errors [Core]: Advanced supports line scope only (`Unsupported promotion scope: <scope>`) and throws `Promotion API call failed for ruleLibrary: <name>, scope: <scope>` when the call fails. `PromotionExecution` and GPM reject an unknown scope with "Invalid promotion scope: {0}" (wording seen only in test fixtures).

## Feasibility / not supported

- Promotions with Derived Price in one procedure: not supported (Promotion Execution and Advanced variant; the GPM variant is not covered by the rule). [Core]
- Header-scope promotions via Advanced Promotion Execution: not supported (line scope only). [Core]
- Promotions together with Price Propagation: not supported. [Help][Core]
- Steps other than Assignment, Formula, Aggregation or List Group after Advanced Promotion Execution: not supported. [Core]

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
| Propagation procedure misprices | Propagation plus `PromotionExecution` (or Advanced, Communications subtype) in one procedure | Do not combine [Help][Core] |
| Save fails: the rule library "either doesn't exist, its context definition isn't the same…" | Rule library missing, on another context definition, or not a promotions library | Create the library on the procedure's context definition [Core] |
| Save fails on a step after Advanced Promotion Execution | Disallowed step after Advanced | Move it before, or keep only Assignment, Formula, Aggregation, List Group after [Core] |
| Save fails: Derived Price and Promotion Execution "in the same pricing procedure" | Derived Price in the procedure | Remove one [Core] |
| `Unsupported promotion scope` at run time | Advanced used with non-line scope | Use line scope [Core] |
| `Invalid promotion scope` at run time | Unknown scope on Promotion Execution or GPM | Use Line, Order or CrossLine [Core] |
| `Promotion API call failed for ruleLibrary` | Rule-library call failed (Advanced throws; Promotion Execution logs) | Check the library and promotion setup [Core] |

## Open questions

- Placement relative to Manual Discount and the tail: live org.
- Runtime differences between the variants beyond scope handling: not read in detail.
