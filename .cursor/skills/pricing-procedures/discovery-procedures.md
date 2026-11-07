# Pricing Discovery Procedures

> Release 264 / API v68.0. Sources: Help `ind.pricing_discovery_procedure_for_pricing.htm`,
> `ind.pricing_set_up_your_discovery_procedure.htm`, `ind.pricing_discover_and_explore.htm`
> (the last is a Salesforce Pricing getting-started page with no discovery content);
> shipped XML: `RLM_DefaultPricingDiscoveryProcedure`, `Salesforce_Pricing_Discovery_Procedure`,
> `RLM_ProductDiscoveryPricingProcedure`. Not live-verified; spot-checked against core 264 (see Open questions). Generic Expression Set mechanics:
> [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md).

Two different things carry "discovery" in the name. Do not mix them.

| Thing | Metadata type | Purpose |
|---|---|---|
| Pricing Discovery procedure | `interfaceSourceType` `DiscoveryProcedure`, `processType` `PricingDiscovery` [Repo] | Gathers the contributing factors (products, assets) for **derived price** and stores them in the context's Contributor node [Help] |
| Product Discovery pricing procedure | `interfaceSourceType` `PricingProcedure`, `processType` `DefaultPricing`, `usageSubtype` `RevenueCloud` [Repo] | An ordinary pricing procedure that yields the list price shown in Product Discovery |

Qualification procedures (for example `RLM_ProductDiscoveryQualificationProcedure`) are out of
scope; see [`../expression-sets/SKILL.md`](../expression-sets/SKILL.md).

## 1. Pricing Discovery procedure (derived price)

Derived price needs data from several sources (products, assets, quotes). The discovery
procedure runs first, collects contributors, and the pricing procedure's Derived Price element
consumes them. [Help] Derived Price itself: [`elements/`](./elements/).

### Default elements

| Builder element | actionType | Role | Source |
|---|---|---|---|
| Fetch Pricing Rules | `RuleFetch` | Reads rules from the Derived Pricing Entries decision table and writes them to the Contributor node (product ids, formulas, scope transactional/non-transactional, source header/product) | [Help], [Repo] |
| Map Product | `MapProduct` | Matches contributing products from the fetched rules to products on the quote/order; with conditions, only matches; without, all contributing products present in both | [Help] |
| Asset Discovery | `AssetDiscovery` | Non-transactional derived price: queries the Asset Action Source Entries V2 table for each contributing product's active assets; Product2Id comes from the Contributor node set by Map Product | [Help], [Repo] |

Optional first elements: Discovery Settings, then Map Line Item (must come immediately after
Discovery Settings). [Help] The Help article calls the second element "Map Products"; the
actionType in XML is `MapProduct`. [Help]/[Repo]

### Ordering

1. Discovery Settings, then Map Line Item (optional, in that order). [Help]
2. Fetch Pricing Rules: must be the first element of the procedure proper. [Help]
3. Map Product (reads fixed variables set by Fetch Pricing Rules). [Help]
4. Asset Discovery only when a derived price record has scope Non-Transactional or Both. [Help]

Shipped XML orders by `sequenceNumber`: FetchPricingRules 1, MapProduct 2, AssetDiscovery 3.
Steps are listed in the file with AssetDiscovery first, so the **sequenceNumber, not file
order, is authoritative** (inferred from the values). [Repo]

### Parameters (from shipped XML)

All three are `stepType` `BusinessKnowledgeModel` with a `customElement` of parameters. Values
below are the shipped ones; `Parameter` values are variable names, `Literal` are constants. Names
are identical in `RLM_DefaultPricingDiscoveryProcedure` and `Salesforce_Pricing_Discovery_Procedure`. [Repo]

**`RuleFetch` (Fetch Pricing Rules)**

| Parameter | Dir | Type | Shipped value |
|---|---|---|---|
| `PricebookEntryId` | in | Parameter | `ItemPricebookEntry` |
| `ProductSellingModelId` | in | Parameter | `ProductSellingModel` |
| `ProductId` | in | Parameter | `Product` |
| `EffectiveFrom` / `EffectiveTo` | in | Parameter | `EffectiveFrom` (both) |
| `CurrencyIsoCode` | in | Parameter | `CurrencyIsoCode` |
| `LineItemId` | in | Parameter | `LineItem` |
| `IsDerived` | in | Parameter | `DerivedPricingAttribute` |
| `LookUpName` | in | Literal | `Derived Pricing Entries` |
| `LookUpApiName` | in | Literal | `Derived_Pricing_Entries_Decision_Table` |
| `IsRealTime` | in | Literal | `false` |
| `ContributorProduct`, `ContributorScope`, `ContributorFormulaInput`, `ContributorSource`, `Contributor`, `ContributorPriceDetail` | out | Parameter | same-named variables |

**`MapProduct`**: only `IsRealTime` (Literal `false`) is shipped; it uses the variables written
by `RuleFetch`. [Core] Its only formal parameters are the dynamic where-condition set (a condition count plus input/operator/output triples per condition, as set in the Builder); none are shipped. In delta mode it also processes deleted lines.

**`AssetDiscovery`**

| Parameter | Dir | Type | Shipped value |
|---|---|---|---|
| `AccountId` | in | Parameter | `Account` |
| `LifecycleStartDate`, `LifecycleEndDate`, `StartDate`, `EndDate` | in | Parameter | `EffectiveFrom` (all four) |
| `LookUpName` | in | Literal | `Asset Action Source Entries V2` |
| `LookUpApiName` | in | Literal | `Asset_Action_Source_Entries_Decision_Table_V2` |
| `IsRealTime` | in | Literal | `false` |
| `NetUnitPrice` | out | Parameter | `ContributorUnitPrice` |
| `TotalPrice` | out | Parameter | `ContributorTotalPrice` |
| `ListPrice` | out | Parameter | `ContributorListPrice` |

Shipped Fetch Pricing Rules sets `resultIncluded` false and Asset Discovery true. [Repo] Help
tells you to tick Include in Output on the procedure. [Help]

### Metadata shape (skeleton)

```xml
<ExpressionSetDefinition xmlns="http://soap.sforce.com/2006/04/metadata">
  <contextDefinitions>RLM_SalesTransactionContext</contextDefinitions>
  <executionMode>Cloud</executionMode>
  <interfaceSourceType>DiscoveryProcedure</interfaceSourceType>
  <processType>PricingDiscovery</processType>
  <template>false</template>
  <versions>
    <rank>1</rank>
    <status>Inactive</status>
    <steps>
      <actionType>RuleFetch</actionType>
      <customElement><parameters>
        <input>true</input><name>LookUpApiName</name><output>false</output>
        <type>Literal</type><value>Derived_Pricing_Entries_Decision_Table</value>
      </parameters><!-- ... --></customElement>
      <name>FetchPricingRules</name><sequenceNumber>1</sequenceNumber>
      <stepType>BusinessKnowledgeModel</stepType>
    </steps>
    <!-- MapProduct (2), AssetDiscovery (3) -->
  </versions>
</ExpressionSetDefinition>
```

Note the two shipped files ship `status` Inactive for the version; activation is a separate step.
[Repo] The `LookUpApiName` literal is how the engine finds the decision table; the table must
exist and be fresh ([`../decision-tables/SKILL.md`](../decision-tables/SKILL.md)).

### Create and run (Builder)

[Help] `ind.pricing_set_up_your_discovery_procedure.htm`

1. App Launcher > Discovery Procedures > New; name; usage type **Pricing Discovery**; context
   definition (Help examples use `SalesTransactionContext`; this repo uses
   `RLM_SalesTransactionContext`). Help recommends starting from the predefined Default
   Discovery Procedure.
2. Open the version in the Discovery Procedure Builder; add elements as ordered above.
3. Set rank 1 (when multiple enabled versions match, the highest rank wins), tick Include in
   Output, Save.
4. Simulate (Input tab), then Activate.
- Permissions: Salesforce Pricing Design Time User (create), Salesforce Pricing Run Time (run).

### Limits

[Help] `ind.pricing_limits.htm`: 2000 discovery procedures per org (1 to 10000); active
duration 10 s (1 to 60 s); 50 elements per discovery procedure (2 to 100); contributing
products per derived product 40 (max 50); contributing assets 50.

## 2. How discovery relates to the transaction pricing procedure

- The discovery procedure populates the Contributor node of the context; the pricing procedure's
  Derived Price element then calculates from it. Both share the context definition. [Help]
- Both run for the same API call and are logged separately: in the Operations Console Debug
  Details use the **Discovery Procedure** tab (JSON) and the **Pricing Procedure** tab. [Help]
  `ind.pricing_understand_and_resolve_api_execution_messages.htm`
- Pricing Setting in the transaction procedure maps `IsDerived` to `DerivedPricingAttribute`,
  the same variable Fetch Pricing Rules reads. [Repo]
- Derived Price only sees the Net Unit Price at the end of its own procedure; splitting
  procedures in a plan loses later adjustments. [Help] `ind.pricing_procedure_plan_limits.htm`
- A stale Derived Pricing Entries or Asset Action Source Entries table silently yields no or
  old contributors; refresh after catalog or asset changes.

## 3. Product Discovery pricing procedure (list price)

Selected in Setup > Product Discovery Settings > Select a Pricing Procedure; it computes the list
price shown in Product Discovery. [Help] `ind.pricing_set_default_pricing_procedure.htm`

It is a plain pricing procedure on a different context definition. Shipped
`RLM_ProductDiscoveryPricingProcedure` (context `RLM_ProductDiscoveryContext`, version status
Draft) contains two steps. [Repo]

| Step name | actionType | What it does |
|---|---|---|
| `PriceBookEntries` (label Price Book Entries) | `ListPrice` | Looks up `Price Book Entries V2` (`Price_Book_Entry_Decision_Table_v2`) for `Product2Id`, `Pricebook2Id`, `ProductSellingModelId`, `Quantity`, `CurrencyIsoCode`; outputs `Id` to `PriceBookEntryId`, `IsDerived`, `ListPrice` to `UnitPrice`, `Subtotal` to `SubTotal`. `ListPriceField` is a Constant variable; `IsOutputResolutionEnabled` false; `IsContractEnabled` false |
| `PricingSetting` (label Pricing Setting) | `PricingSettings` | Maps `LineItemId`, `NetUnitPrice`, `Subtotal`, `PriceWaterfall`; `IsPropagationEnabled` false |

Input tags use names such as `PricingProductId` and `PricingCurrencyCode` (a different tag set
than the sales-transaction procedure). ListPrice and Pricing Settings parameters are covered in
[`elements/`](./elements/). Shipped here the ListPrice step precedes Pricing Setting, unlike the
usual Pricing Setting first rule; check [procedure-anatomy-and-ordering.md](./procedure-anatomy-and-ordering.md)
before copying this order into a transaction procedure. [Repo]

Apex hooks can also be placed in a Product Discovery procedure plan (Pricing and Apex sections;
at most one Qualification section; section order decides how prices apply). [Help]
`ind.pricing_customize_pricing_procedures_with_apex_hooks.htm` (the sample classes for that case
are in the article, not reproduced here).

## Shipped in this repo (snapshot)

| Procedure | Kind | Steps |
|---|---|---|
| `RLM_DefaultPricingDiscoveryProcedure` | DiscoveryProcedure / PricingDiscovery, context `RLM_SalesTransactionContext` | FetchPricingRules, MapProduct, AssetDiscovery |
| `Salesforce_Pricing_Discovery_Procedure` | same step set | same |
| `RLM_ProductDiscoveryPricingProcedure` | PricingProcedure / DefaultPricing | PriceBookEntries, PricingSetting |
| `RLM_DefaultRatingDiscoveryProcedure` | rating discovery (not pricing) | out of scope |

Discover live state:
`python scripts/expression_sets/describe_expression_set.py --target-org <sf_alias> --developer-name <name> --params`

## Verify

- Simulate in the Discovery Procedure Builder (Input tab) and check the Contributor outputs.
- Operations Console > pricing API execution > Debug Details > Discovery Procedure tab.
- Confirm the lookup tables are fresh before blaming the procedure.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No derived price applied, no error | Discovery procedure not active/ranked, or Derived Pricing Entries table stale | Activate, check rank, refresh the table |
| Non-transactional contributors missing | Asset Discovery absent although scope is Non-Transactional/Both; Asset Action Source Entries V2 stale | Add the element; refresh |
| Contributors found but wrong products | Map Product conditions (for example RootItem) not matching | Review conditions |
| Discovery succeeds, pricing ignores it | Pricing procedure lacks Derived Price element or `IsDerived` not mapped | See Derived Price element file |
| Product Discovery shows wrong or no price | Procedure not selected in Product Discovery Settings, or Price Book Entries V2 table stale | Section 3 |

## Open questions

- Fetch-must-be-first and error text were not confirmed in core; those claims remain Help and shipped XML.
- `Salesforce_Pricing_Discovery_Procedure` vs `RLM_DefaultPricingDiscoveryProcedure`: step lists
  match by inventory; whether the files are byte-identical was not diffed.
- Whether Help's "Discovery Settings" element has a distinct actionType (not shipped here).
