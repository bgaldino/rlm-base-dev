---
page_id: meta_pricingrecipe.htm
title: PricingRecipe
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/meta_pricingrecipe.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# PricingRecipe

Represents the data models or sets of objects of a particular
cloud that the pricing data store consumes during design time and run time.

## Parent Type

This type extends the [Metadata](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/metadata.htm "HTML (New Window)") metadata type and inherits its fullName
field.

## File Suffix and Directory Location

PricingRecipe components have the suffix .pricingRecipe and are stored in the pricingRecipe folder.

## Version

PricingRecipe components are available in API version 60.0 and later.

## Special Access Rules

This metadata type is available with Salesforce Pricing.

## Fields

| Field Name | Description |
| --- | --- |
| defaultPricingProcedure | Field Type  [ExpressionSetDefinition](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/meta_expressionsetdefinition.htm "HTML (New Window)")  Description  Expression set definition that's associated with this pricing recipe setting. |
| defaultPricingProcedureDeveloperName | Field Type  string  Description  For internal use only. |
| defaultPricingProcedureId | Field Type  string  Description  ID of the pricing procedure of the pricing recipe. |
| developerName | Field Type  string  Description  Required.  API name of the pricing recipe. |
| isActive | Field Type  boolean  Description  Indicates whether the pricing recipe is active (`true`) or not (`false`). The default value is `false` |
| isInternal | Field Type  boolean  Description  Indicates whether the price recipe record is created internally by the Salesforce platform (`true`) or not (`false`). The default value is `false` |
| masterLabel | Field Type  string  Description  Required.  Name for pricing recipe that's defined when the pricing recipe is created. |
| pricingRecipeTableMapping | Field Type  [PricingRecipeTableMapping[]](#PricingRecipeTableMapping)  Description  Mapping of the pricing components of a lookup table with the chosen pricing recipe. |

## PricingRecipeTableMapping

Represents the mapping of the lookup table with the chosen pricing recipe.

| Field Name | Description |
| --- | --- |
| isInternal | Field Type  boolean  Description  Indicates whether the price recipe field mapping record is created internally by the Salesforce platform (`true`) or not (`false`). The default value is `false`. |
| lookupTable | Field Type  [DecisionTable](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/meta_decisiontable.htm "HTML (New Window)")  [DecisionMatrixDefinition](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/meta_decisionmatrixdefinition.htm "HTML (New Window)")  Description  Lookup table that's associated with either a decision matrix or decision table. |
| lookupTableDeveloperName | Field Type  string  Description  For internal use only. |
| pricingComponentType | Field Type  string  Description  Pricing component field data that the decision table is built on.  Valid values are:  - `AttributeDiscount` - `BundleDiscount` - `DerivedPricing` - `ListPrice` - `PriceAdjustmentMatrix` - `PromotionsDiscount` - `VolumeDiscount` - `VolumeTierDiscount` - `DiscountDistributionService`. This value   is available in API version 60.0 and later. - `MinimumPrice`. Available in API version   62.0 and later. |
| pricingProcedureOutputMapList | Field Type  [PricingProcedureOutputMap[]](#PricingProcedureOutputMap)  Description  List of the mappings of the outputs of the pricing procedures to the associated lookup tables. Available in API version 60.0 and later. |
| pricingRecipe | Field Type  string  Description  Required.  Pricing data store that's associated with this pricing recipe field mapping. |

## PricingProcedureOutputMap

Represents the mapping of the outputs of the pricing procedures to the associated lookup
tables. Each record specifies the output mapping of the associated lookup table
based on the pricing component type specified in the PricingRecipeTableMapping
object.

| Field Name | Description |
| --- | --- |
| fieldName | Field Type  string  Description  For internal use only. |
| isPricingRecipeActive | Field Type  boolean  Description  Indicates whether the associated pricing recipe is active (`true`) or not (`false`).  The default value is `false`. |
| outputFieldName | Field Type  string  Description  Field name that contains the output type that's generated from the pricing element. |
| outputFieldNameString | Field Type  string  Description  Derived field that references a specific column in a decision table or decision matrix. |
| outputType | Field Type  string  Description  Output type that's generated from a pricing element.  Valid values are:  - `AdjustmentType` - `AdjustmentValue` - `CustomOutput` - `HashOutput` - `UnitPrice` |
| pricingElementType | Field Type  PricingElementType (enumeration of type string)  Description  Type of pricing element, which is a derived field from `PricingRecipeTableMapping.PricingComponentType`. Valid values are:   - `AssetDiscovery` - `AttributeDiscount` - `BundleDiscount` - `DerivedPricing` - `DiscountDistributionService` - `ListPrice` - `MinimumPrice` - `PriceAdjustmentMatrix` - `PriceRevision` - `PromotionsDiscount` - `RuleFetch` - `VolumeDiscount` - `VolumeTierDiscount` |

## Declarative Metadata Sample Definition

The following is an example of a PricingRecipe component.

```
<PricingRecipe xmlns="http://soap.sforce.com/2006/04/metadata">
    <defaultPricingProcedureId> </defaultPricingProcedureId>
    <developerName>CMEDefaultRecipe</developerName>
    <isActive>false</isActive>
    <isInternal>false</isInternal>
    <masterLabel>CMEDefaultRecipe</masterLabel>
    <pricingRecipeTableMapping>
        <isInternal>false</isInternal>
        <lookupTableDeveloperName>Bundle_Based_Adjustment_Decision_Table</lookupTableDeveloperName>
        <pricingComponentType>CUSTOMDISCOUNT</pricingComponentType>
        <fileBasedDecisionTableName>Bundle Based Adjustment Entries</fileBasedDecisionTableName>
        <pricingProcedureOutputMapList>
            <fieldName>AdjustmentValue</fieldName>
            <isPricingRecipeActive>false</isPricingRecipeActive>
            <outputFieldName>0lPxx000000000f</outputFieldName>
            <outputFieldNameString>false</outputFieldNameString>
            <outputType>AdjustmentValue</outputType>
	     <pricingElementType>BundleDiscount</pricingElementType>
        </pricingProcedureOutputMapList>
        <pricingProcedureOutputMapList>
            <fieldName>AdjustmentType</fieldName>
            <isPricingRecipeActive>false</isPricingRecipeActive>
            <outputFieldName>0lPxx000000000m</outputFieldName>
            <outputFieldNameString>false</outputFieldNameString>
            <outputType>AdjustmentType</outputType>
	     <pricingElementType>BundleDiscount</pricingElementType>
        </pricingProcedureOutputMapList>
        <pricingRecipe>CMEDefaultRecipe</pricingRecipe>
    </pricingRecipeTableMapping>
</PricingRecipe>
```

The following is an example `package.xml` that
references the previous definition.

```
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>*</members>
        <name>PricingRecipe</name>
    </types>
    <version>67.0</version>
</Package>
```

## Wildcard Support in the Manifest File

This metadata type supports the wildcard character `*` (asterisk) in the package.xml manifest file.
For information about using the manifest file, see [Deploying and Retrieving Metadata with the Zip File](https://developer.salesforce.com/docs/atlas.en-us.262.0.api_meta.meta/api_meta/file_based_zip_file.htm "HTML (New Window)").
