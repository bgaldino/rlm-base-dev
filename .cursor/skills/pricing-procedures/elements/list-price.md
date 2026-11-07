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
It is the starting point for discounts and adjustments.

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
| Input rule: Product | `Product2Id` / `ProductId` / `ItemId` / `ProductNId` | Parameter | Yes | Name varies by table/procedure [Repo]; Help label "Product" |
| Input rule: Price Book | `Pricebook2Id` / `PricebookNId` | Parameter | Price book tables | Variable `PriceBooks` or `PricebookId` [Repo] |
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

[Core] Formal inputs are the table's **input columns** (dynamic, from the decision table or matrix) plus `Quantity` and `ListPriceField`. Outputs are the table's **output columns**, any `section-N-output` entries, `ListPrice` (required; the generic unit-price output is replaced by it for this element), `Subtotal` (optional), and `IsContracted` (added only when `IsContractEnabled=true`). Multiple-output mode (shipped flag `IsOutputResolutionEnabled`, inferred) adds `ResolutionStrategy` (required), `CandidatePriority`, `FinalPriceSequence` and `UseAsList`; shipped procedures leave it `false`.

The Builder's "Lookup Table Details" maps table columns to variables; metadata
stores only variable names, so the table column is implied by the table plus the
variable binding (inferred). `IsDerived` appears as an output on some steps. [Repo]

## Placement and ordering

- After [Pricing Setting](./pricing-setting.md) (and Map Line Item if used). Everything that discounts or adjusts must come after it.
- If the table returns no match, the element keeps whatever List Price and Subtotal earlier elements set; it does not zero them. [Help]
- Contract flow: contract List Price step, then a List Group filtered on `IsContracted = true` holding Manual Discount and Stop Pricing. [Help]
- Shipped default procedure runs a cost-book `ListPrice` after the price-book one, and re-runs `ListPrice` inside ListGroups for contract-dated and undated lines. [Repo]
- Ordering across elements: [procedure anatomy and ordering](../procedure-anatomy-and-ordering.md).

## Rules and limits

- [Core] If `LookUpApiName` is set but neither `LookUpId` nor the name resolves: `Exception in pricing element. Lookup API name: <name>, but LookUpId is null.`
- The lookup table must be Active and have a **pricing recipe table mapping**; otherwise: `Ensure that the lookup table in the ListPrice step is valid and try again.` See [pricing-wiring sections A and B](../../pricing-wiring/SKILL.md). [Repo skill]
- Pricing recipes bundle the predefined tables (Price Book Entries, Contract Pricing Entries, etc.); sync or create via recipe. [Help: `ind.pricing_pricing_recipes.htm`, `ind.pricing_create_or_use_predefined_lookup_tables.htm`]
- `LookUpApiName` vs `LookUpId`: prefer `LookUpApiName`; add `__LOOKUPID_*__` only when needed and never both casually; never commit real record ids. Full rules: [pricing-wiring section B](../../pricing-wiring/SKILL.md). Shipped XML carries both with placeholders, replaced at deploy. [Repo]
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
Live orgs may carry hard-coded `LookUpId` record ids from Builder saves; repo source uses placeholders.

## Shipped in this repo (snapshot)

| Procedure | Step | What it does |
|---|---|---|
| RLM_DefaultPricingProcedure | `Getbasepricesfrompricebook` | Price Book Entries V2 to `ListPrice` |
| RLM_DefaultPricingProcedure | `Getunitcostfromcostbook` | Cost Book Entries to `ItemUnitCost__std` |
| RLM_DefaultPricingProcedure | `AssignItemContractPricetoListPrice` (in ListGroup) | Contract Pricing Entries, `IsContractEnabled=true`, outputs `ItemContractPrice`, `IsContracted`, discount type/value |
| RLM_DefaultPricingProcedure | `AssignedFromPricingContractforundatedlines` | Same for lines without dates |
| PRM DISTI / Recalc | `Getbasepricesfrompricebook`, contract step; DISTI also `GetCostsfromCostBook` | Same pattern |
| RLM_ProductDiscoveryPricingProcedure | `PriceBookEntries` | Price book lookup for discovery |

Snapshot. Discover with
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

- Simulate: waterfall shows the list price; with contract pricing, shows the contracted price and any follow-on discount. [Help]
- Query the table's source (e.g. `PricebookEntry`, `ContractItemPrice`) to confirm the expected row; check the decision table is Fresh.

## Troubleshooting

| Symptom / error | Cause | Fix |
|---|---|---|
| `Ensure that the lookup table in the ListPrice step is valid and try again.` | Missing recipe table mapping, inactive table, or bad `LookUpApiName`/`LookUpId` | pricing-wiring section A and B |
| `Exception in pricing element. Lookup API name: <name>, but LookUpId is null.` | API name not found as a decision table / matrix in the org | Fix `LookUpApiName`; deploy the table first |
| Plausible but wrong-currency price | `CurrencyIsoCode` not an input on the step; lookup returns first row | Add input on every currency-denominated lookup (list price, adjustment, tiers); see pricing-wiring "Wrong-currency price returned" |
| Price stays at earlier value | No matching row; element keeps prior values | Check table freshness, product/price book/selling model inputs |
| Contract price not applied | Table stale, contract not activated, dates outside Contract Item Price range | Activate, refresh Contract Pricing Entries, check `StartDate` |
| Derived product prices at 0 | Expected: list price must be 0 | Add Derived Price element after |

## Open questions

- Whether `ListPriceField` constants are Builder-generated per table (the shipped names follow `Constant_<column>_<table>_LP`) or hand-defined: core treats it as an ordinary optional Text parameter; Builder generation is inferred.
- Exact column binding for tables other than shipped ones is only visible in Builder.
