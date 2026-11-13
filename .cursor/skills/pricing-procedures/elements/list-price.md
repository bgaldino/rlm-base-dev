# List Price (`ListPrice`)

> Release 264 / API v68.0. Sources: `ind.pricing_add_list_price_element.htm`,
> `ind.pricing_contract_based_pricing.htm`, `ind.pricing_calculate_contract_based_pricing.htm`,
> `ind.pricing_create_or_use_predefined_lookup_tables.htm`, `ind.pricing_pricing_recipes.htm`,
> `ind.pricing_get_ready_to_calculate_the_derived_price.htm`; shipped XML:
> `RLM_DefaultPricingProcedure`, `RLM_PRM_DISTI_Pricing_Procedure`,
> `RLM_Revenue_Management_Recalc_Procedure`, `RLM_ProductDiscoveryPricingProcedure`.
> Parameter names, lookup resolution and error text cross-checked against core [Core].

Fetches a base price from a decision table (price book entries, contract pricing
entries, cost book entries) and writes it to List Price / Subtotal output variables.
It is the starting point for discounts and adjustments. Price books and entries: [`../../pricing-setup/price-books.md`](../../pricing-setup/price-books.md);
cost books (Help calls them tracking-only): [`../../pricing-setup/cost-books.md`](../../pricing-setup/cost-books.md).

## When to use it

- Base price from a price book: Price Book Entries (or V2) table. [Help]
- Contract-negotiated price: Contract Pricing Entries table with contract-based pricing on. [Help]
- Cost lookup (margin): a custom table, e.g. Cost Book Entries, writing to a cost variable. [Repo]
- Derived-pricing procedures must use Price Book Entries **V2** (or your custom table). [Help]
- Generic lookups with no price semantics: use [decision table lookups](./decision-table-lookups.md).

## Configuration

| Builder field | Parameter name | Type | Required | Notes |
|---|---|---|---|---|
| Lookup table | `LookUpName` | Literal | Yes | Display name, e.g. `Price Book Entries V2` [Repo] |
| Lookup table API name | `LookUpApiName` | Literal | Yes | Decision table DeveloperName [Repo] |
| Lookup table id | `LookUpId` | Literal | Optional | Record id or `__LOOKUPID_*__` placeholder; see below. [Core] When `LookUpApiName` is set and `LookUpId` does not load, core resolves the id from the API name |
| List price column | `ListPriceField` | Parameter (Text) | Optional [Core] | Constant-style variable naming the table's price column, e.g. `Constant_UnitPrice_Price_Book_Entry_Decision_Table_v2_LP` [Repo] |
| Input rule: Product | `Product2Id` / `ProductId` / `ItemId` | Parameter | Yes | Name varies by table/procedure [Repo]; Help label "Product" |
| Input rule: Price Book | `Pricebook2Id` | Parameter | Price book tables | Variable `PriceBooks` or `PricebookId` [Repo] |
| Input rule: Selling model | `ProductSellingModelId` | Parameter | Yes | |
| Input rule: Selling model type | `SellingModelType` | Parameter | Contract table | [Help, Repo] |
| Input rule: Start / End date | `StartDate`, `EndDate` | Parameter | Contract table | Variables `PricingDate` / `EffectiveFrom` [Repo] |
| Input rule: Contract | `ContractId` | Parameter | Contract table | `ItemContract` or `ItemPricingContract` [Repo, Help] |
| Input rule: Currency | `CurrencyIsoCode` | Parameter | Multicurrency: yes | See Troubleshooting |
| Quantity | `Quantity` | Parameter (Numeric) | Yes [Core] | `LineItemQuantity` [Help] |
| Use contract-based pricing | `IsContractEnabled` | Literal | Yes | `true` for contract table, else `false` [Repo, Help] |
| Hide waterfall | `HideWaterfall` | Literal | Shipped | `false` |
| Output resolution | `IsOutputResolutionEnabled` | Literal | Shipped | `false` |
| Output: List Price | `ListPrice` | Parameter (output) | Yes | `ListPrice`, or `NetUnitPrice`/`ItemContractPrice`/`ItemUnitCost__std` per use [Repo, Help] |
| Output: Subtotal | `Subtotal` | Parameter (output) | Optional | `ItemNetTotalPrice` / `SubTotal` [Help, Repo] |
| Output: Contract Pricing | `IsContracted` | Parameter (output) | Contract table | Boolean flag [Help, Repo] |
| Output rule: Discount Type / Value | `DiscountType`, `DiscountValue` | Parameter (output) | Contract table | `ItemContractDiscountType/Value` [Help, Repo] |
| Housekeeping | `sectionCount`=`0`, `selectedFunction`=`Get`, `IsRealTime`=`false` | Literal | Shipped | [Repo] |

[Core] Formal inputs are the table's **input columns** (dynamic, from the decision table or matrix) plus `Quantity` and `ListPriceField`. Outputs are the table's **output columns**, any `section-N-output` entries, `ListPrice` (required; the generic unit-price output is replaced by it for this element), `Subtotal` (optional), and `IsContracted` (added only when `IsContractEnabled=true`). When the multiple-output flag is set, an optional Numeric `FinalPriceSequence` input is added [Core]. `ResolutionStrategy` (required), `CandidatePriority`, `UseAsList` and a write-back JSON for extra outputs are [inferred]; their registration was not re-found. Shipped procedures leave `IsOutputResolutionEnabled` `false`. [Repo]

### No matching row and duplicate rows [Core]

| Rows returned | Resolution off | Resolution on |
|---|---|---|
| 0 | Prior `ListPrice` and `Subtotal` untouched; `IsContracted` set false | Disputed: Help says the line stops with a configuration error (no zero, no skip); the core path read showed nothing to resolve. Verify on the target org |
| 1 | `IsContracted` set true; `ListPrice` from the `ListPriceField` column (default column `UnitPrice`; a null column value writes nothing); `Subtotal` = ListPrice x Quantity | Resolved the same way |
| More than 1 | Error `DUPLICATE_VALUE_FOUND_IN_LOOKUP` ("Duplicate entries found while looking up {0}") | Not an error: the resolution strategy picks the final row(s) by candidate priority / final price sequence; `UseAsList` keeps all |

Resolution errors: `RESOLUTION_STRATEGY_NOT_VALID` ("This procedure output resolution is unavailable. Specify an active and valid procedure output resolution for the pricing element {0}."), `RESOLUTION_FORMULA_ERROR` ("Specify a valid formula function for the {0} element."), `RESOLUTION_STRATEGY_NOT_ACTIVE`, `RESOLUTION_INVALID_SEQUENCE`, `RESOLUTION_CACHE_MISS`, `RESOLUTION_STRATEGY_WRITE_BACK_ERROR`. Any other lookup failure surfaces as `UNEXPECTED_ERROR_DURING_LOOKUP` ("Unexpected error occurred while looking up {0}"). [Core]

The Builder's "Lookup Table Details" maps table columns to variables; metadata
stores only variable names, so the table column is implied by the table plus the
variable binding (inferred). `IsDerived` appears as an output on some steps. [Repo]

## Placement and ordering

- After [Pricing Setting](./pricing-setting.md) (and Map Line Item if used). Everything that discounts or adjusts must come after it.
- If the table returns no match, the element keeps whatever List Price and Subtotal earlier elements set; it does not zero them [Help]. With output resolution on, Help instead says the line stops pricing (see the table above).
- Contract flow: contract List Price step, then a List Group filtered on `IsContracted = true` holding Manual Discount and Stop Pricing. [Help]
- Shipped default procedure runs a cost-book `ListPrice` after the price-book one, and re-runs `ListPrice` inside ListGroups for contract-dated and undated lines. [Repo]
- Ordering across elements: [procedure anatomy and ordering](../procedure-anatomy-and-ordering.md).

## Rules and limits

- [Core] If `LookUpApiName` is set but neither `LookUpId` nor the name resolves: `Exception in pricing element. Lookup API name: <name>, but LookUpId is null.`
- Save-time validation fails with `Ensure that the lookup table in the ListPrice step is valid and try again.` [Core] Core checks the step's lookup id against the active recipe table mappings for the procedure's usage subtype (grouped by element type). The error fires when (a) the lookup id cannot be resolved, (b) the element type has no recipe-mapped table at all (inner text: "The pricing element type isn't valid. Use elements that are associated with lookup tables and try again."), or (c) the step's table is not among those mapped for the element type. The check is skipped during package install. So a missing recipe mapping for ListPrice is a confirmed cause. See [pricing-wiring sections A and B](../../pricing-wiring/SKILL.md).
- Save-time hierarchy check applies to the tags `Product2Id`, `ProductSellingModelId`, `Id`, `IsDerived`, `Quantity`, `Subtotal`, `ListPrice` (they must share the line item's hierarchy). [Core]
- Pricing recipes bundle the predefined tables (Price Book Entries, Contract Pricing Entries, etc.); sync or create via recipe. [Help: `ind.pricing_pricing_recipes.htm`, `ind.pricing_create_or_use_predefined_lookup_tables.htm`]
- `LookUpApiName` vs `LookUpId`: prefer `LookUpApiName`; add `__LOOKUPID_*__` only when needed and never both casually; never commit real record ids. Full rules: [pricing-wiring section B](../../pricing-wiring/SKILL.md). The Default and PRM procedures ship `__LOOKUPID_*__` placeholders, replaced at deploy; the Recalc procedure (`unpackaged/post_procedureplans`) ships literal source-org `LookUpId` values that no transform replaces, and the discovery List Price step has no `LookUpId`. [Repo]
- Contract pricing needs: products linked to an activated contract with Contract Item Prices, then **refresh** the Contract Pricing Entries decision table. [Help] Refresh/freshness: [decision-tables](../../decision-tables/SKILL.md).
- Contract-based pricing takes a boolean Contract Pricing output (`IsContracted`) to gate later discounts. [Help]
- Derived pricing: derived product list price must be 0 on its price book entry; source product carries a real price. [Help]

## Metadata shape

```xml
<steps>
    <actionType>ListPrice</actionType>
    <customElement>
        <parameters><input>true</input><name>Product2Id</name><output>false</output><type>Parameter</type><value>Product</value></parameters>
        <parameters><input>true</input><name>Pricebook2Id</name><output>false</output><type>Parameter</type><value>PriceBooks</value></parameters>
        <parameters><input>true</input><name>ProductSellingModelId</name><output>false</output><type>Parameter</type><value>ProductSellingModel</value></parameters>
        <parameters><input>true</input><name>Quantity</name><output>false</output><type>Parameter</type><value>LineItemQuantity</value></parameters>
        <parameters><input>true</input><name>CurrencyIsoCode</name><output>false</output><type>Parameter</type><value>CurrencyIsoCode</value></parameters>
        <parameters><input>true</input><name>ListPriceField</name><output>false</output><type>Parameter</type><value>Constant_UnitPrice_Price_Book_Entry_Decision_Table_v2_LP</value></parameters>
        <parameters><input>true</input><name>LookUpName</name><output>false</output><type>Literal</type><value>Price Book Entries V2</value></parameters>
        <parameters><input>true</input><name>LookUpApiName</name><output>false</output><type>Literal</type><value>Price_Book_Entry_Decision_Table_v2</value></parameters>
        <parameters><input>true</input><name>LookUpId</name><output>false</output><type>Literal</type><value>__LOOKUPID_PRICE_BOOK_ENTRY_DECISION_TABLE_V2__</value></parameters>
        <parameters><input>true</input><name>IsContractEnabled</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>true</input><name>HideWaterfall</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>true</input><name>IsOutputResolutionEnabled</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>true</input><name>sectionCount</name><output>false</output><type>Literal</type><value>0</value></parameters>
        <parameters><input>true</input><name>selectedFunction</name><output>false</output><type>Literal</type><value>Get</value></parameters>
        <parameters><input>true</input><name>IsRealTime</name><output>false</output><type>Literal</type><value>false</value></parameters>
        <parameters><input>false</input><name>ListPrice</name><output>true</output><type>Parameter</type><value>ListPrice</value></parameters>
    </customElement>
    <label>Get base prices from price book</label>
    <name>Getbasepricesfrompricebook</name>
    <stepType>BusinessKnowledgeModel</stepType>
</steps>
```

Contract variant: set `IsContractEnabled=true`, `ContractId`, `ItemId`,
`SellingModelType`, `StartDate`, `EndDate`, the Contract Pricing Entries table, and
outputs `ListPrice`, `IsContracted`, `DiscountType`, `DiscountValue`. [Repo]
Live orgs may carry hard-coded `LookUpId` record ids from Builder saves; repo source uses placeholders, except the Recalc procedure (literal ids; see above).

## Shipped in this repo (snapshot)

Complete: 10 `ListPrice` steps in 4 procedures (no other shipped file has one). [Repo]
PBE v2 = `Price_Book_Entry_Decision_Table_v2`; Contract = `Contract_Pricing_Entries_Decision_Table`;
Cost = `RLM_CostBookEntries`. Seq is within the parent (or top level).

| Procedure | Step | Seq | Parent | Table | Contract | List price output |
|---|---|---|---|---|---|---|
| RLM_DefaultPricingProcedure | `AssignItemContractPricetoListPrice` | 2 | `Setlistpriceforlineswithcontractpricing` | Contract | true (`ItemPricingContract`) | `ItemContractPrice` |
| RLM_DefaultPricingProcedure | `AssignedFromPricingContractforundatedlines` | 2 | `Setlistpriceforundatedlineswithcontractpricing` | Contract | true (`ItemPricingContract`) | `ItemContractPrice` |
| RLM_DefaultPricingProcedure | `Getbasepricesfrompricebook` | 5 | top level | PBE v2 | false | `ListPrice` |
| RLM_DefaultPricingProcedure | `Getunitcostfromcostbook` | 6 | top level | Cost | false | `ItemUnitCost__std` |
| RLM_PRM_DISTI_Pricing_Procedure | `GetCostsfromCostBook` | 2 | top level | Cost | false | `ItemUnitCost__std` |
| RLM_PRM_DISTI_Pricing_Procedure | `AssignItemContractPricetoListPrice` | 2 | `Setlistpriceforlineswithcontractpricing` | Contract | true (`ItemContract`) | `ItemContractPrice` |
| RLM_PRM_DISTI_Pricing_Procedure | `Getbasepricesfrompricebook` | 3 | top level | PBE v2 | false | `ListPrice` |
| RLM_Revenue_Management_Recalc_Procedure | `AssignItemContractPricetoListPrice` | 2 | `Setlistpriceforlineswithcontractpricing` | Contract | true (`ItemContract`) | `ItemContractPrice` |
| RLM_Revenue_Management_Recalc_Procedure | `Getbasepricesfrompricebook` | 2 | top level | PBE v2 | false | `ListPrice` |
| RLM_ProductDiscoveryPricingProcedure | `PriceBookEntries` | 2 | top level | PBE v2 | false | `UnitPrice` |

`RLM_Price_Distribution_Procedure` has no `ListPrice` step. Snapshot. Discover with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

- Simulate: waterfall shows the list price; with contract pricing, shows the contracted price and any follow-on discount. [Help]
- Query the table's source (e.g. `PricebookEntry`, `ContractItemPrice`) to confirm the expected row; check the decision table is Fresh.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| `Ensure that the lookup table in the ListPrice step is valid and try again.` (save/activation time) | Lookup id unresolvable, no recipe-mapped table for ListPrice, or the table is not one of the mapped tables [Core] | Map the table in the recipe (pricing-wiring sections A and B); fix `LookUpApiName`/`LookUpId` |
| `DUPLICATE_VALUE_FOUND_IN_LOOKUP` at runtime | More than one row matched and output resolution is off | Make inputs unique, or enable output resolution |
| `Exception in pricing element. Lookup API name: <name>, but LookUpId is null.` | `LookUpId` does not load and `LookUpApiName` is not found as a decision table / matrix in the org | Fix `LookUpApiName`; deploy the table first |
| Plausible but wrong-currency price | `CurrencyIsoCode` not an input on the step: several currency rows for the product give a duplicate-value error (single output) or a priority pick that can be another currency's row (output resolution on) [Platform behaviour, traced]; a lone other-currency row prices the line [inferred]. With the input passed and no row for that currency, the lookup returns no match, earlier values are kept, with no currency conversion [Platform behaviour, traced] | Add input on every currency-denominated lookup (list price, adjustment, tiers); see pricing-wiring "Wrong-currency price returned" |
| Price stays at earlier value | No matching row with resolution off; element keeps prior values (with resolution on, Help says the line stops instead) | Check table freshness, product/price book/selling model inputs |
| Contract price not applied | Table stale, contract not activated, dates outside Contract Item Price range | Activate, refresh Contract Pricing Entries, check `StartDate` |
| Derived product prices at 0 | Expected: list price must be 0 | Add Derived Price element after |

## Feasibility / not supported

- Several matching rows without output resolution: error, not first-row-wins (see table above). [Core]
- With resolution off, a table with no matching row leaves prior values untouched; the element never zeroes them (only `IsContracted` is set false). [Help, Core] With resolution on, Help says every product needs a matching row or the line stops; core was read otherwise, so verify on the org. To force a default, add a later Assignment or Formula. [inferred]
- A matched row whose `ListPriceField` column is null writes nothing (prior values kept). [Core]
- Price column other than the default needs `ListPriceField` naming it. [Core]

## Help coverage
- Help coverage: `ind.pricing_contract_based_pricing`, `ind.pricing_calculate_contract_based_pricing` and `ind.pricing_add_list_price_element` are reflected above (contract prerequisites, refresh, `IsContracted` gating via List Group, no-match keeps values). Not stated in Help: the contract table's required `StartDate`/`EndDate` inputs beyond the walkthrough's `StartDate`; the walkthrough also writes the contract price to `NetUnitPrice`, while shipped XML writes `ItemContractPrice`. [Help, Repo]

## Open questions
- Whether `ListPriceField` constants are Builder-generated per table (the shipped names follow `Constant_<column>_<table>_LP`) or hand-defined: core treats it as an ordinary optional Text parameter; Builder generation is inferred.
- Exact column binding for tables other than shipped ones is only visible in Builder.
