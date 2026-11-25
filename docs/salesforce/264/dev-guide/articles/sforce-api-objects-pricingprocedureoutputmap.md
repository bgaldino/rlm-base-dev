---
page_id: sforce-api-objects-pricingprocedureoutputmap
title: PricingProcedureOutputMap
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricingprocedureoutputmap.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-tooling-api-parent
legacy_page_id: sforce_api_objects_pricingprocedureoutputmap.htm
fetched_at: 2026-11-25
---

# PricingProcedureOutputMap

Represents the mapping of the outputs of the pricing procedures to the associated lookup tables. Each record specifies the output mapping of the associated lookup table based on the pricing component type specified in the Pricing Recipe Table Mapping object. This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`

## Fields

### IsPricingRecipeActive

- **Type**: boolean

- **Properties**: Defaulted on create, Filter, Group, Sort

- **Description**: Indicates if the pricing recipe is active (true) or not (false).

The default value is `false`.

### LookupField

- **Type**: reference

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: Definition of the fields that are used for this lookup.

### OutputFieldNameId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The field name containing the output type generated from the pricing element.

This field is a polymorphic relationship field.

- **Relationship Name**: OutputFieldName

- **Relationship Type**: Lookup

- **Refers To**: CalculationMatrixColumn, DecisionTableParameter

### OutputFieldNameString

- **Type**: string

- **Properties**: Filter, Group, Nillable, Sort

- **Description**: This is a derived field that references a specific column in a decision table or decision matrix.

### OutputType

- **Type**: picklist

- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The output type generated from a pricing element.

Possible values are:

- `AdjustmentType`—Adjustment Type

- `AdjustmentValue`—Adjustment Value

- `CustomOutput`—Custom Output

- `HashOutput`—Hash Output

- `PriceIndex`—Price Index

- `UnitPrice`—Unit Price

- `UpperBound`—Unit Price

- `LowerBound`—Unit Price

- `TierValue`—Unit Price

- `TierType`—Unit Price

### PricingComponentType

- **Type**: picklist

- **Properties**: Filter, Group, Nillable, Restricted picklist, Sort

- **Description**: The pricing component field data on which the decision table is built.

Possible values are:

- `AttributeDiscount`—Attribute Based Discount

- `BundleDiscount`—Bundle Based Discount

- `DerivedPricing`

- `DiscountDistributionService`—Discount Distribution Service

- `ListPrice`—List Price

- `PriceAdjustmentMatrix`

- `PromotionsDiscount`

- `VolumeDiscount`—Volume Based Discount

- `VolumeTierDiscount`—Tier Discount

- `RuleFetch`

- `AssetDiscovery`

### PricingRecipeTableMappingId

- **Type**: reference

- **Properties**: Create, Filter, Group, Sort, Update

- **Description**: The mapping of pricing components of a lookup table with the chosen pricing recipe.

This field is a relationship field.

- **Relationship Name**: PricingRecipeTableMapping

- **Relationship Type**: Lookup

- **Refers To**: PricingRecipeTableMapping

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-pricingprocedureoutputmap.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
