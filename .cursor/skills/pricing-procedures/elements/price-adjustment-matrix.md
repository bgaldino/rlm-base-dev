# Price Adjustment Matrix (`PriceAdjustmentMatrix`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_the_price_adjustment_matrix_element.htm`,
> `ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm`,
> `ind.pricing_modify_price_adjustment_matrices.htm`,
> `ind.pricing_example_apply_discounts_sequentially_for_a_product.htm`; shipped XML:
> RLM_PRM_DISTI_Pricing_Procedure only; core source (behavior only).

Applies an adjustment from any custom advanced decision table (custom or standard
source object) mapped into the pricing recipe. The generic, bring-your-own-table
discount element.

## When to use it
- Contextual pricing beyond volume/attribute/bundle: customer, partner program,
  quote fields. [Help]
- Prefer the dedicated elements when they fit:
  [volume-and-tier-discount.md](./volume-and-tier-discount.md),
  [attribute-based-price.md](./attribute-based-price.md),
  [bundle-based-price.md](./bundle-based-price.md).
- Shipped only for partner and distributor program discounts in this repo. [Repo]

## Configuration
| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName`, `LookUpApiName`, `LookUpId` | Literal | Yes | Custom DT, e.g. `RLM_Channel_Program_Level_Partner`. [Repo] |
| Input rule variables | one parameter per DT input column | Parameter | Per table | Shipped: `PartnerId` mapped to `PartnerAccount__c` / `RLM_Distributor_Account__c`. Names are the DT column names. [Repo] |
| Adjustment type/value column | `AdjustmentTypeField`, `AdjustmentValueField` | Parameter | Yes | Constants naming the DT result columns (`Constant_AdjustmentType_<table>`). [Repo] |
| Result column mapping | DT result column name (e.g. `RLM_Discount_Rate__c`) | Parameter (output) | Optional | Shipped writes the matched rate to `PartnerDiscountPercent`. [Repo] |
| Quantity, Input Unit Price | `Quantity`, `InputUnitPrice` | Parameter | Yes | |
| Output: net unit price | `NetUnitPrice` | Parameter (output) | Yes | |
| Enable Output Resolution | `IsOutputResolutionEnabled` | Literal | No | Shipped `false`. [Repo][Help] |
| Resolution Strategy | `ResolutionStrategy` | Parameter | When resolution on | Text, names the Procedure Output Resolution constant. Present only when `IsOutputResolutionEnabled` is true. [Core] |
| Use As List | `UseAsList` | Parameter | When resolution on | Names the unique-valued list column. [Core] |
| Contract enabled | `IsContractEnabled` | Literal | Yes | `false`. |
| Boilerplate | `HideWaterfall`, `IsRealTime`, `sectionCount`, `selectedFunction` | Literal | Yes | |

## Placement and ordering
- Shipped as the first steps of the PRM procedure (seq 5 and 7 of the top level),
  before the standard discount chain, each in its own ListGroup under an
  `AdvancedListFilter`. They compute a rate into a variable that later assignment
  groups (`AssignDistributorUnitPrice`, `AssignPartnerUnitPrice`) apply. [Repo]
- Sequential stacking and waterfall: see
  [volume-and-tier-discount.md](./volume-and-tier-discount.md#placement-and-ordering).
- The table must be registered on the pricing recipe's Price Adjustment Matrix tab
  with rule variables mapped, or the element has nothing to read. [Help]

## Rules and limits
- Setup order: custom decision table (Pricing usage, Advanced) -> activate -> map in
  Pricing Recipes > Price Adjustment Matrix > Modify (`AdjustmentValue`,
  `AdjustmentType`) -> add element. [Help]
- Percentage values as whole numbers (10 not 0.10). [Help]
- Each input combination must resolve to one row unless Output Resolution is enabled;
  multi-row needs a unique-valued column for "Use As List" and a Procedure Output
  Resolution record (`SEQUENCE(<col>)` or `STACK`). [Help][Core]
- [Core] Empty matches are filtered. More than one row with resolution on but no
  strategy errors `RESOLUTION_STRATEGY_NOT_VALID`; more than one row with resolution
  off errors `DUPLICATE_VALUE_FOUND_IN_LOOKUP`. Type/value may be a column name or
  a literal.
- Input variable names in the Help example are example-specific. [Help]
- Resolution function must be `SEQUENCE` or `STACK`; a malformed formula (STACK with
  more than one token, SEQUENCE with one or fewer) errors `RESOLUTION_FORMULA_ERROR`. [Core]
- STACK takes each row's percentage off the original input price and sums the discounts;
  an Override row under STACK is an error (`INVALID_INPUT`, override adjustment error);
  STACK with a null input price is `RESOLUTION_FORMULA_ERROR`. SEQUENCE applies rows in
  sorted order, each to the previous result, so Override is allowed. [Core]
- Accepted type strings are the same as Manual Discount
  ([manual-discount.md](./manual-discount.md)). [Core]

## Metadata shape
```xml
<steps>
  <actionType>PriceAdjustmentMatrix</actionType>
  <customElement>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>RLM_Channel_Program_Level_Partner</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_RLM_CHANNEL_PROGRAM_LEVEL_PARTNER__</value></parameters>
    <parameters><input>true</input><name>PartnerId</name><output>false</output><type>Parameter</type><value>PartnerAccount__c</value></parameters>
    <parameters><input>true</input><name>AdjustmentTypeField</name><output>false</output><type>Parameter</type><value>Constant_AdjustmentType_RLM_Channel_Program_Level_Partner</value></parameters>
    <parameters><input>true</input><name>AdjustmentValueField</name><output>false</output><type>Parameter</type><value>Constant_AdjustmentValue_RLM_Channel_Program_Level_Partner</value></parameters>
    <parameters><input>true</input><name>IsOutputResolutionEnabled</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <!-- plus Quantity, InputUnitPrice, IsContractEnabled=false, HideWaterfall,
         sectionCount, selectedFunction, IsRealTime -->
    <parameters><input>false</input><name>RLM_Discount_Rate__c</name><output>true</output><type>Parameter</type><value>PartnerDiscountPercent</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Constant names above are abbreviated in the inventory (truncated); read the real step
XML for the full names. `__LOOKUPID_*__` resolves at deploy. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step group | What it does |
|---|---|---|
| RLM_PRM_DISTI_Pricing_Procedure | `GetDistributorProgramDiscount` (seq 5) | Distributor program discount into transient distributor discount var |
| RLM_PRM_DISTI_Pricing_Procedure | `GetPartnerProgramDiscount` (seq 7) | Partner program discount (`PartnerDiscountPercent`) |

Snapshot only. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
Simulate with the input tags set (e.g. partner account); inspect the output variable
and waterfall. Refresh the custom decision table first (`../../decision-tables/SKILL.md`).

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| Nothing applied | Table not mapped in recipe, inactive, or stale | Map/activate/refresh |
| `DUPLICATE_VALUE_FOUND_IN_LOOKUP` | Multiple matches, no resolution | Tighten keys or enable resolution |
| `RESOLUTION_STRATEGY_NOT_VALID` | Resolution on, strategy blank | Set strategy constant |
| 10 treated as 0.1% | Whole-number rule misunderstood | Use 10 for 10% |

## Open questions
- Core also has a sibling attribute-matrix model; not covered here.
