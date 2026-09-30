---
page_id: connect_resources_product_configurator_configure.htm
title: Configuration (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_product_configurator_configure.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-09-29
---

# Configuration (POST)

Retrieve and update a product’s configuration from a configurator. Execute configuration rules and notify users of any violations for changes to product bundle, attributes, or product quantity within a bundle. Additionally, get pricing details for the configured bundle.

    

      

#### Note

When you add multiple products, to make sure that the constraint
        rules engine evaluates all rules, call the Configure API after each individual node
        addition. This mirrors the incremental pattern in the Product Configurator UI, which calls
        the Configure API incrementally, one product addition per call, and triggers CML after each
        addition.

    

    

## Resource

      
      

```
/connect/cpq/configurator/actions/configure
```

    

    

## Resource Example

      
      

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/actions/configure
```

      

If you’re calling this API from an external website, include the site name in the resource.

      

```
https://yourInstance.salesforce.com/<siteName>/services/data/v68.0/connect/cpq/configurator/actions/configure
```

    

    

## Available Version

      
      

60.0

    

    

## HTTP Methods

      
      

POST

    

    

## Request Body for POST

      
      

**JSON Example**

      

This example shows a sample to initiate a context based on a transaction ID.

      

```
{
    "transactionLineId": "0QLDE000000IBXw4AO",
    "transactionId": "0Q0xx0000000001GAA",
    "correlationId": "c95246d4-102c-4ecd-a263-f74ac525d1e5",
    "configuratorOptions": {
        "executePricing": true,
        "returnProductCatalogData": true
    },
    "qualificationContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI"
    }
}
```

      

This example shows a sample to add, update, or delete a node in an existing context.

      

```
{
    "transactionLineId": "0QLDE000000IBXw4AO",
    "transactionId": "0Q0DE000000ISHJs81",
    "correlationId": "c95246d4-102c-4ecd-a263-f74ac525d1e5",
    "configuratorOptions": {
        "executePricing": true,
        "returnProductCatalogData": true,
        "qualifyAllProductsInTransaction": true,
        "validateProductCatalog": true,
        "validateAmendRenewCancel": true,
        "executeConfigurationRules": true,
        "addDefaultConfiguration": true
    },
    "contextResponseType": "Full",
    "qualificationContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI"
    },
    "transactionContextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
    "addedNodes": [
        {
            "path": ["0Q0DE000000ISHJs81", "sti2_id"],
            "addedObject": {
                "id": "ref_sti2_id",
                "SalesTransactionSource": "sti2_id",
                "PricebookEntry": "01uxx0000000001AAA",
                "ProductSellingModel": "0jPxx0000000001AAA",
                "businessObjectType": "QuoteLineItem",
                "Quantity": 10,
                "UnitPrice": 2.0,
                "Product": "01txx0000000001AAA"
            }
        },
        {
            "path": ["0Q0DE000000ISHJs81", "ref_sti2_id","ref_stir1_id"],
            "addedObject": {
                "id": "ref_stir1_id",
                "businessObjectType": "QuoteLineRelationship",
                "MainItem": "0QLDE000000IBXw4AO",
                "AssociatedItem": "ref_sti2_id",
                "ProductRelatedComponent": "0dSxx0000000001AAA",
                "ProductRelationshipType": "0yoxx0000000001AAA",
                "AssociatedItemPricing": "IncludedInBundlePrice"
                
            }
        }
    ],
    "updatedNodes": [
        {
            "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"],
            "updatedAttributes": {
                "Quantity": 5
            }
        }
    ],
    "deletedNodes": [
        {
            "path": ["0Q0DE000000ISHJs81", "0QLDE000000IBXw4AO"]
        }
    ]
}
```

      

This example adds a node to an existing context and includes the contextFieldsList property.

      

```
{
  "configuratorInput": {
    "transactionId": "0Q0xx0000004DEmCAM",
    "transactionLineId": "ref_a7cdf3fb_d912_4c21_b683_9aadd591ac3c",
    "transactionContextId": "",
    "addedNodes": [
      {
        "path": [
          "0Q0xx0000004DEmCAM",
          "ref_a7cdf3fb_d912_4c21_b683_9aadd591ac3c"
        ],
        "addedObject": {
          "Product": "01txx0000006ip1AAA",
          "ProductCode": "PB001",
          "ProductName": "Printer Bundle",
          "ProductBasedOn": null,
          "id": "ref_a7cdf3fb_d912_4c21_b683_9aadd591ac3c",
          "PricebookEntry": "01uxx0000008zXxAAI",
          "ProductSellingModel": "0jPxx00000000ODEAY",
          "SellingModelType": "OneTime",
          "SubscriptionTerm": null,
          "PricingTermUnit": null,
          "UnitPrice": 205,
          "Quantity": 1,
          "businessObjectType": "QuoteLineItem",
          "SalesTransactionItemSource": "ref_a7cdf3fb_d912_4c21_b683_9aadd591ac3c",
          "SalesTransactionItemParent": "0Q0xx0000004DEmCAM",
          "SalesTransactionItemGroup": null,
          "ItemRampIdentifier": null,
          "ItemSegmentIdentifier": null,
          "EffectiveFrom": null,
          "EffectiveTo": null,
          "StartDate": null,
          "EndDate": null,
          "ItemSegmentType": null
        }
      }
    ],
    "updatedNodes": [],
    "deletedNodes": [],
    "correlationId": "859100d0_0a78_4203_9cdc_bead3cb243a9",
    "contextFieldsList": [
      "SalesTransaction.Account",
      "SalesTransaction.QuoteAccount",
      "SalesTransaction.Pricebook",
      "SalesTransaction.CurrencyIsoCode",
      "SalesTransaction.SalesTransactionSource",
      "SalesTransaction.OriginalActionType",
      "SalesTransaction.Contract",
      "SalesTransaction.STContractHasCotermination__std",
      "SalesTransaction.STContractEndDate__std",
      "SalesTransaction.EffectiveDate",
      "SalesTransaction.Status",
      "SalesTransaction.Subtotal",
      "SalesTransaction.TransactionType",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemSource",
      "SalesTransaction.SalesTransactionItem.Product",
      "SalesTransaction.SalesTransactionItem.ProductName",
      "SalesTransaction.SalesTransactionItem.ProductCode",
      "SalesTransaction.SalesTransactionItem.ProductSellingModel",
      "SalesTransaction.SalesTransactionItem.PricebookEntry",
      "SalesTransaction.SalesTransactionItem.SellingModelType",
      "SalesTransaction.SalesTransactionItem.SubscriptionTerm",
      "SalesTransaction.SalesTransactionItem.PricingTermUnit",
      "SalesTransaction.SalesTransactionItem.ProductBasedOn",
      "SalesTransaction.SalesTransactionItem.CustomProductName",
      "SalesTransaction.SalesTransactionItem.StartQuantity",
      "SalesTransaction.SalesTransactionItem.EndQuantity",
      "SalesTransaction.SalesTransactionItem.Quantity",
      "SalesTransaction.SalesTransactionItem.StartDate",
      "SalesTransaction.SalesTransactionItem.EndDate",
      "SalesTransaction.SalesTransactionItem.UnitPrice",
      "SalesTransaction.SalesTransactionItem.NetUnitPrice",
      "SalesTransaction.SalesTransactionItem.NetTotalPrice",
      "SalesTransaction.SalesTransactionItem.PartnerUnitPrice",
      "SalesTransaction.SalesTransactionItem.Discount",
      "SalesTransaction.SalesTransactionItem.ListPrice",
      "SalesTransaction.SalesTransactionItem.PriceWaterFall",
      "SalesTransaction.SalesTransactionItem.TotalLineAmount",
      "SalesTransaction.SalesTransactionItem.Subtotal",
      "SalesTransaction.SalesTransactionItem.ItemRampIdentifier",
      "SalesTransaction.SalesTransactionItem.ItemSegmentIdentifier",
      "SalesTransaction.SalesTransactionItem.ItemSegmentName",
      "SalesTransaction.SalesTransactionItem.ItemSegmentType",
      "SalesTransaction.SalesTransactionItem.SalesTransactionAction",
      "SalesTransaction.SalesTransactionItem.Deleted",
      "SalesTransaction.SalesTransactionItem.DerivedPricingAttribute",
      "SalesTransaction.SalesTransactionItem.SalesTransactionSourceAsset",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemParent",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemGroup",
      "SalesTransaction.SalesTransactionItem.ItemPath",
      "SalesTransaction.SalesTransactionItem.LineItemPath",
      "SalesTransaction.SalesTransactionItem.ItemUnitOfMeasureName",
      "SalesTransaction.SalesTransactionItem.ItemUnitOfMeasureScale",
      "SalesTransaction.SalesTransactionItem.ItemUnitOfMeasureRoundingMethod",
      "SalesTransaction.SalesTransactionItem.BillingFrequency",
      "SalesTransaction.SalesTransactionItem.UsageModelType",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.AttributeKey",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.AttributeValue",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.AttributeName",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.AttributePicklistValue",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.SalesTransactionItemAttrParent",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.IsPriceImpacting",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.AttributeUnitOfMeasure",
      "SalesTransaction.SalesTransactionItem.SalesTransactionItemAttribute.AttributeUnitOfMeasureName",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.MainItem",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.AssociatedItem",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.RootItem",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.ProductRelatedComponent",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.ProductRelatedComponentPRT__std",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.AssociatedQuantScaleMethod",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.AssociatedItemPricing",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.ProductRelationshipType",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.RootItemProduct",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.RootItemProductCode",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.RootItemProductSellingModel",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.MainItemProduct",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.MainItemProductSellingModel",
      "SalesTransaction.SalesTransactionItem.SalesTrxnItemRelationship.IsPriceInclusive",
      "SalesTransaction.SalesTransactionAction.Type",
      "SalesTransaction.SalesTransactionAction.SourceAsset",
      "SalesTransaction.SalesTransactionAction.Subtype__std",
      "SalesTransaction.SalesTransactionGroup.SalesTransactionGroupParent",
      "SalesTransaction.SalesTransactionGroup.GroupIsRamped__std",
      "SalesTransaction.SalesTransactionGroup.GroupSortOrder",
      "SalesTransaction.SalesTransactionGroup.GroupSource",
      "SalesTransaction.SalesTransactionGroup.SummarySubtotal",
      "SalesTransaction.SalesTransactionGroup.GroupName",
      "SalesTransaction.SalesTransactionGroup.GroupStartDate__std",
      "SalesTransaction.SalesTransactionGroup.GroupEndDate__std",
      "SalesTransaction.SalesTransactionGroup.ParentSalesTransactionItemGroup__std",
      "SalesTransaction.SalesTransactionGroup.GroupType",
      "SalesTransaction.SalesTransactionGroup.SummaryTotalAmount__std"
    ],
    "configuratorOptions": {
      "explainabilityEnabled": false,
      "executePricing": false,
      "qualifyAllProductsInTransaction": false,
      "validateProductCatalog": true,
      "validateAmendRenewCancel": false,
      "executeConfigurationRules": true,
      "returnProductCatalogData": true,
      "addDefaultConfiguration": true
    },
    "contextResponseType": "Product"
  }
}

```

      

**Properties**

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `added​Nodes` | [Configurator Added Node Input](./connect_requests_configurator_added_node_input.htm.md)[] | List of added context nodes that’s passed to the product configurator | Optional | 60.0 |
| `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md)[] | Options to pass to the configurator | Optional | 60.0 |
| `context​FieldsList` | String[] | List of fields to return in the configurator response | Optional | 68.0 |
| `context​ResponseType` | String | Specifies the type of transaction context response. Valid values are `Delta`—returns only the sales transaction items that are added or updated in the call. Deleted items are returned separately in a `DeletedSTIIds` collection on the response. The response is always flat regardless of response type; reconstruct hierarchy from `SalesTransactionItemParent` on child items and `MainItem`/`AssociatedItem` on relationships; `Full`—Returns all sales transaction items in a transaction; `None`—Returns empty transaction context response; or `Product`—Returns the sales transaction items related to the product that's being configured. | Required for large sales transactions with more than 1000 line items and less than 15K line items. | 65.0 |
| `correlation​Id` | String | ID that’s specified for traceability of logs | Optional | 60.0 |
| `deleted​Nodes` | [Configurator Deleted Node Input](./connect_requests_configurator_deleted_node_input.htm.md)[] | List of deleted context nodes that’s passed to the product configurator | Optional | 60.0 |
| `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md)[] | Details such as account ID, contact ID, and context ID that are used for executing qualification rules | Optional | 60.0 |
| `transaction​ContextId` | String | ID of the transaction context. The context expires after 10 minutes by default (managed by Context Service). To extend it, set `ContextTtlInMinutes` on the Context Definition record. The org-level ceiling is controlled by `ContextMaxTtlInMinutes` (default: 45 minutes). Design for short-lived sessions: rebuild context on expiry rather than extending TTL indefinitely, because the durable state lives on the persisted transaction record. | Optional | 60.0 |
| `transaction​Id` | String | ID of the sales transaction that’s being configured such as a quote or an order | Required | 60.0 |
| `transaction​LineId` | String | ID of the top-level line item that’s being configured | Optional | 60.0 |
| `updated​Nodes` | [Configurator Updated Node Input](./connect_requests_configurator_updated_node_input.htm.md)[] | List of updated context nodes that’s passed to the product configurator | Optional | 60.0 |

    

    

## Response Body for POST

      
      

[Configuration Details](./connect_responses_configurator_output.htm.md)
