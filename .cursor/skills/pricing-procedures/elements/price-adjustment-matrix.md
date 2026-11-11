# Price Adjustment Matrix (`PriceAdjustmentMatrix`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_the_price_adjustment_matrix_element.htm`,
> `ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm`,
> `ind.pricing_modify_price_adjustment_matrices.htm`,
> `ind.pricing_example_apply_discounts_sequentially_for_a_product.htm`,
> `ind.pricing_procedure_output_resolution.htm`,
> `ind.pricing_understand_your_resolution_variables.htm`,
> `ind.pricing_create_a_procedure_output_resolution_record.htm`; shipped XML:
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
| Adjustment type/value column | `AdjustmentTypeField`, `AdjustmentValueField` | Parameter | Yes | Constants naming the DT result columns (`Constant_AdjustmentType_<table>_PAM`). [Repo] |
| Result column mapping | DT result column name (e.g. `RLM_Discount_Rate__c`) | Parameter (output) | Optional | Shipped writes the matched rate to `PartnerDiscountPercent` (partner) or `RLM_Transient_Distributor_Discount_Percent__c` (distributor). [Repo] |
| Quantity, Input Unit Price | `Quantity`, `InputUnitPrice` | Parameter | Yes | |
| Output: net unit price | `NetUnitPrice` | Parameter (output) | Yes | |
| Enable Output Resolution | `IsOutputResolutionEnabled` | Literal | No | Shipped `false`. [Repo][Help] |
| Resolution Strategy | `ResolutionStrategy` | Parameter | When resolution on | Text, names the Procedure Output Resolution constant; Help: the strategy is a previously saved Procedure Output Resolution record. Present only when `IsOutputResolutionEnabled` is true. [Help][inferred from Repo; core confirms write-back of both tags only] |
| Use As List | `UseAsList` | Parameter | When resolution on | The input variable (tag) whose values identify the rows to resolve; the matching decision-table column must be unique-valued. [Help] |
| Contract enabled | `IsContractEnabled` | Literal | Yes | `false`. |
| Boilerplate | `HideWaterfall`, `IsRealTime`, `sectionCount`, `selectedFunction` | Literal | Yes | |

## Placement and ordering
- Shipped in the PRM procedure right after Pricing Setting (1), the two List Price
  steps (2, 3) and Derived Price (4): the distributor group at top-level seq 5, then
  `NormalizeDistributorDiscountPercent` (6), then the partner group (7), all before the
  standard discount chain, each in its own ListGroup under an `AdvancedListFilter`. They
  compute a rate into a variable that later assignment groups
  (`AssignDistributorUnitPrice`, `AssignPartnerUnitPrice`) apply. [Repo]
- Sequential stacking and waterfall: see
  [volume-and-tier-discount.md](./volume-and-tier-discount.md#placement-and-ordering).
- The table must be registered on the pricing recipe's Price Adjustment Matrix tab
  with rule variables mapped, or the element has nothing to read. [Help]

## Rules and limits
- Setup order: custom decision table (Pricing usage, Advanced) -> activate -> map in
  Pricing Recipes > Price Adjustment Matrix > Modify (`AdjustmentValue`,
  `AdjustmentType`) -> add element. [Help]
- Recipe mapping step: Modify > select the decision table(s) > set default output mapping if needed > pick a pricing component type > map the table's rule variables. Map `AdjustmentValue` and `AdjustmentType` to the table's result columns (Help example: source object Price Adjustment Tier, results `TierValue`, `AdjustmentType`). Input rule variables in Help are example-specific. [Help: `ind.pricing_modify_price_adjustment_matrices.htm`]
- Percentage values as whole numbers (10 not 0.10). [Help]
- Several adjustments on one line (Help sequential example): add a custom lookup field from the adjustment object to the transaction object (for example Price Adjustment Tier to Quote Line Item), a context node for the adjustment object with its mapping, and map those tags to the procedure variables; the decision table needs a unique-valued column (for example the tier name, mapped to a generic tag such as `Contributor`) used as "Use As List". [Help]
- Resolution Variables "Candidate Priority" and "Final Price Sequence" exist only for List Price and Price Tracking, not here; Resolution Strategy and Use As List apply here. [Help]
- Each input combination must resolve to one row unless Output Resolution is enabled;
  multi-row needs a unique-valued column for "Use As List" and a Procedure Output
  Resolution record (`SEQUENCE(<col>)` or `STACK`). [Help][Core]
- [Core] Empty matches are filtered. More than one row with resolution on but no
  strategy errors `RESOLUTION_STRATEGY_NOT_VALID`; more than one row with resolution
  off errors `DUPLICATE_VALUE_FOUND_IN_LOOKUP`. `AdjustmentTypeField` /
  `AdjustmentValueField` hold either a result column name (row value used) or a literal
  (the literal itself is used as the type or value).
- [Core] With resolution on, a named strategy must exist, be active and belong to the
  Price Adjustment Matrix pricing element, else `RESOLUTION_STRATEGY_NOT_ACTIVE`. A
  single matching row with a blank strategy is priced as a normal single match.
- [Core] SEQUENCE sort columns must exist in the first matched row
  (`RESOLUTION_FORMULA_ERROR` otherwise); sort is ascending, nulls first, by the
  column's data type. Resolution is evaluated per line over that line's matched rows [inferred].
- [Core] Rows with a blank type or null value are skipped. [inferred] No clamping or
  rounding was found: an oversized Amount or a Percentage above 100 may go negative.
- Input variable names in the Help example are example-specific. [Help]
- Resolution function must be `SEQUENCE` or `STACK`; a malformed formula (STACK with
  more than one token, SEQUENCE with one or fewer) errors `RESOLUTION_FORMULA_ERROR`. [Core]
- STACK takes each row's percentage off the original input price and sums the discounts;
  an Override row under STACK is an error (`INVALID_INPUT`, override adjustment error);
  STACK with a null input price is `RESOLUTION_FORMULA_ERROR`. SEQUENCE applies rows in
  sorted order, each to the previous result, so Override is allowed. [Core]
- Type matching is case-insensitive for Override, Amount and Percentage (and their
  adjustment-enum equivalents); under STACK an unrecognised type errors `INVALID_INPUT`.
  [Core] See also [manual-discount.md](./manual-discount.md) [inferred, same strings].

### Feasibility / not supported
| Question | Answer |
|---|---|
| Key the matrix on a line custom field? | Yes: map the field to a context tag and wire it to a table input column; the table needs a matching column. [inferred] |
| Several matching rows on one line? | Only with Output Resolution (SEQUENCE or STACK). [Core] |
| Override combined with STACK? | Not supported (`INVALID_INPUT`); use SEQUENCE. [Core] |
| Use on a rate or usage procedure? | Rating uses a separate Rate Adjustment Matrix, which rejects several matching rows (`MULTIPLE_OUTPUT_NOT_SUPPORTED_FOR_RATE_ADJUSTMENT_MATRIX`). [Core] |
| Resolution strategy on Volume, Tier, Attribute or Bundle? | Not available; only here, List Price and Price Tracking. [Help] |

## Metadata shape
```xml
<steps>
  <actionType>PriceAdjustmentMatrix</actionType>
  <customElement>
    <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>RLM_Channel_Program_Level_Partner</value></parameters>
    <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_RLM_CHANNEL_PROGRAM_LEVEL_PARTNER__</value></parameters>
    <parameters><input>true</input><name>PartnerId</name><output>false</output><type>Parameter</type><value>PartnerAccount__c</value></parameters>
    <parameters><input>true</input><name>AdjustmentTypeField</name><output>false</output><type>Parameter</type><value>Constant_AdjustmentType_RLM_Channel_Program_Level_Partner_PAM</value></parameters>
    <parameters><input>true</input><name>AdjustmentValueField</name><output>false</output><type>Parameter</type><value>Constant_AdjustmentValue_RLM_Channel_Program_Level_Partner_PAM</value></parameters>
    <parameters><input>true</input><name>IsOutputResolutionEnabled</name><output>false</output><type>Literal</type><value>false</value></parameters>
    <!-- plus Quantity, InputUnitPrice, LookUpName, IsContractEnabled=false,
         HideWaterfall, sectionCount, selectedFunction, IsRealTime -->
    <parameters><input>false</input><name>RLM_Discount_Rate__c</name><output>true</output><type>Parameter</type><value>PartnerDiscountPercent</value></parameters>
    <parameters><input>false</input><name>NetUnitPrice</name><output>true</output><type>Parameter</type><value>NetUnitPrice</value></parameters>
  </customElement>
  <stepType>BusinessKnowledgeModel</stepType>
</steps>
```
Names and values are the shipped partner step's; the distributor step differs only in
`PartnerId` (`RLM_Distributor_Account__c`) and the rate output
(`RLM_Transient_Distributor_Discount_Percent__c`). `__LOOKUPID_*__` resolves at deploy. [Repo]

## Shipped in this repo (snapshot)
| Procedure | Step group | What it does |
|---|---|---|
| RLM_PRM_DISTI_Pricing_Procedure | `GetDistributorProgramDiscount` (seq 5) > `LookupDistributorProgramDiscount` (seq 2) | Distributor program discount into transient distributor discount var |
| RLM_PRM_DISTI_Pricing_Procedure | `GetPartnerProgramDiscount` (seq 7) > `LookupPartnerProgramDiscount` (seq 2) | Partner program discount (`PartnerDiscountPercent`) |

Snapshot only. Discover: `python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify
Simulate with the input tags set (e.g. partner account); inspect the output variable
and waterfall. Refresh the custom decision table first (`../../decision-tables/SKILL.md`).

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| Nothing applied | Table not mapped in recipe, inactive, or stale | Map/activate/refresh |
| `DUPLICATE_VALUE_FOUND_IN_LOOKUP` | Multiple matches, no resolution | Tighten keys or enable resolution |
| `RESOLUTION_STRATEGY_NOT_VALID` | Resolution on, strategy blank, several rows | Set strategy constant |
| `RESOLUTION_STRATEGY_NOT_ACTIVE` | Strategy missing, inactive, or not a Price Adjustment Matrix strategy | Activate or fix the record [Core] |
| `RESOLUTION_FORMULA_ERROR` | Bad STACK/SEQUENCE formula, unknown sort column, or STACK with null price | Fix formula [Core] |
| 10 treated as 0.1% | Whole-number rule misunderstood | Use 10 for 10% |

## Related element
- None open. A separate element, `AttributeAdjustmentMatrix`, exists (no lookup table,
  no resolution strategy; per-product matrices). See
  [attribute-adjustment-matrix.md](./attribute-adjustment-matrix.md). [Core]
