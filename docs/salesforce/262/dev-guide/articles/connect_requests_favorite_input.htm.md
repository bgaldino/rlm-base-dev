---
page_id: connect_requests_favorite_input.htm
title: Configuration Save Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_favorite_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Configuration Save Input

Input representation of the details to save a configuration.

JSON example
:   ```
    {
      "data": "{&quot;LegalEntity&quot;:null,&quot;ProductName&quot;:&quot;Monitor&quot;,&quot;businessObjectType&quot;:&quot;QuoteLineItem&quot;,&quot;Product&quot;:&quot;01txx0000006i2aAAA&quot;,&quot;ItemIsPrimarySegment&quot;:false,&quot;ListPrice&quot;:144.99,&quot;ValidationResult&quot;:null,&quot;StartDate&quot;:null,&quot;ContractVolumePasId&quot;:null,&quot;BillingTreatment&quot;:null,&quot;PeriodBoundaryStartMonth&quot;:null,&quot;SalesTransactionSourceAsset&quot;:null,&quot;id&quot;:&quot;0QLxx0000004C9VGAU&quot;,&quot;PartnerDiscountPercent&quot;:10,&quot;PriceWaterFall&quot;:null,&quot;BillingFrequency&quot;:null,&quot;ProductCode&quot;:&quot;MO001&quot;,&quot;DerivedPricingAttribute&quot;:false,&quot;TaxTreatment&quot;:null,&quot;Subtotal&quot;:1739.88,&quot;ItemRampIdentifier&quot;:null,&quot;ItemSegmentName&quot;:null,&quot;SalesTransactionItemAttribute&quot;:[{&quot;AttributeKey&quot;:&quot;0tjxx0000000001AAA&quot;,&quot;AttributeValue&quot;:&quot;1080p Built-in Display&quot;,&quot;ParentReference&quot;:&quot;0QLxx0000004C9VGAU&quot;,&quot;AttributePicklistValue&quot;:&quot;0v6xx0000000001AAA&quot;,&quot;IsPriceImpacting&quot;:false,&quot;businessObjectType&quot;:&quot;QuoteLineItemAttribute&quot;,&quot;AttributeName&quot;:&quot;Display&quot;,&quot;id&quot;:&quot;0zuxx000000000FAAQ&quot;,&quot;AttributeDefinitionCode&quot;:null,&quot;SalesTransactionItemAttrParent&quot;:&quot;0QLxx0000004C9VGAU&quot;},{&quot;AttributeKey&quot;:&quot;0tjxx0000000009AAA&quot;,&quot;AttributeValue&quot;:&quot;24 Inch&quot;,&quot;ParentReference&quot;:&quot;0QLxx0000004C9VGAU&quot;,&quot;AttributePicklistValue&quot;:&quot;0v6xx000000000GAAQ&quot;,&quot;IsPriceImpacting&quot;:false,&quot;businessObjectType&quot;:&quot;QuoteLineItemAttribute&quot;,&quot;AttributeName&quot;:&quot;Display_Size&quot;,&quot;id&quot;:&quot;0zuxx000000000GAAQ&quot;,&quot;AttributeDefinitionCode&quot;:null,&quot;SalesTransactionItemAttrParent&quot;:&quot;0QLxx0000004C9VGAU&quot;}],&quot;PricebookEntry&quot;:&quot;01uxx0000008yX0AAI&quot;,&quot;DiscountAmount&quot;:null,&quot;PricingTermCount&quot;:0,&quot;SubscriptionTermUnit&quot;:null,&quot;NetUnitPrice&quot;:144.99,&quot;ItemEffectiveGrantDate&quot;:null,&quot;ProductCategory&quot;:null,&quot;SalesTransactionAction&quot;:null,&quot;SalesTransactionActionType&quot;:null,&quot;SalesTransactionItemGroup&quot;:null,&quot;PeriodBoundaryDay&quot;:null,&quot;SalesTrxnItemDescription&quot;:null,&quot;LineItemDistributionType&quot;:null,&quot;ProrationPolicy&quot;:null,&quot;ContractDiscountType&quot;:null,&quot;TransactionType&quot;:null,&quot;ParentReference&quot;:&quot;0Q0xx0000004C92CAE&quot;,&quot;Discount&quot;:null,&quot;PricingTermUnit&quot;:null,&quot;ProductSellingModel&quot;:&quot;0jPxx0000000001EAA&quot;,&quot;PricingSource&quot;:null,&quot;StockKeepingUnit&quot;:null,&quot;PartnerUnitPrice&quot;:130.491,&quot;ItemTotalAdjustmentAmount&quot;:0,&quot;SalesTransactionItemSource&quot;:&quot;0QLxx0000004C9VGAU&quot;,&quot;ContractAttributePasId&quot;:null,&quot;SubscriptionTerm&quot;:null,&quot;SellingModelType&quot;:&quot;OneTime&quot;,&quot;EndQuantity&quot;:12,&quot;NetTotalPrice&quot;:1739.88,&quot;TotalLineAmount&quot;:1739.88,&quot;ItemSegmentType&quot;:null,&quot;ProductBasedOn&quot;:&quot;11Bxx000002C1nqEAC&quot;,&quot;Deleted&quot;:false,&quot;BillingReference&quot;:null,&quot;ArePartialPeriodsAllowed&quot;:false,&quot;ItemRecordedPrice&quot;:null,&quot;CustomProductName&quot;:null,&quot;ItemSegmentIdentifier&quot;:null,&quot;SalesTransactionItemParent&quot;:&quot;0Q0xx0000004C92CAE&quot;,&quot;Quantity&quot;:12,&quot;PeriodBoundary&quot;:null,&quot;ContractDiscountValue&quot;:null,&quot;LineItemDiscountValue&quot;:null,&quot;ContractId&quot;:null,&quot;EndDate&quot;:null,&quot;ItemGroupSummarySubtotal&quot;:null,&quot;IsContracted&quot;:false,&quot;UnitPrice&quot;:144.99,&quot;StartQuantity&quot;:null,&quot;ContractPrice&quot;:null,&quot;TotalPrice&quot;:1739.88,&quot;LineItemDiscountType&quot;:null,&quot;ItemPath&quot;:&quot;01txx0000006i2aAAA&quot;,&quot;productKey&quot;:[&quot;0QLxx0000004C9VGAU&quot;]}",
      "description": "This configuration is saved for reuse.",
      "name": "Favorite Configuration",
      "referenceRecordId": "01txx0000006iCFAAY"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `data` | String | JSON object that contains the details of the sales transaction, formatted as a string. | Optional | 63.0 |
    | `description` | String | Description of the saved configuration. | Optional | 63.0 |
    | `name` | String | Name of the saved configuration. | Optional | 63.0 |
    | `referenceRecord​Id` | String | ID of the record for which the configuration must be saved. | Required | 63.0 |
