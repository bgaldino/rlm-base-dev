---
page_id: connect_requests_configurator_input.htm
title: Configurator Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configurator Input

Input representation of the request to modify the product configuration.

**JSON example**

                    
: This example shows a sample to initiate a context based on a transaction
                        ID.

                    
: 
                        

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

                    

          
: This example shows a sample to add, update, or delete a node in an existing
            context.

: 

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
                "businessObjectType": "QuoteLineItemRelationship",
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

**Properties**

: 

                                    
                                        

                                        

                                        

- 
- 
- 
- 

                                        

                                        

                                    

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `added​Nodes` | [Configurator Added Node Input](./connect_requests_configurator_added_node_input.htm.md)[] | List of added context nodes that’s passed to the product configurator. | Optional | 60.0 |
| `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md)[] | Options to pass to the configurator. | Optional | 60.0 |
| `context​ResponseType` | String | Specifies the type of transaction context response. Valid values are: `Delta`—Returns the sales transaction items that are added or updated. `Full`—Returns all sales transaction items in a transaction. `None`—Returns empty transaction context response. `Product`—Returns the sales transaction items related to the product that's being configured. | Required for large sales transactions with more than 1000 line items and less than 15K line items. | 65.0 |
| `correlation​Id` | String | ID that’s specified for traceability of logs. | Optional | 60.0 |
| `deleted​Nodes` | [Configurator Deleted Node Input](./connect_requests_configurator_deleted_node_input.htm.md)[] | List of deleted context nodes that’s passed to the product configurator. | Optional | 60.0 |
| `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md)[] | Details such as account ID, contact ID, and context ID that are used for executing qualification rules. | Optional | 60.0 |
| `transaction​ContextId` | String | ID of the transaction context. | Optional | 60.0 |
| `transaction​Id` | String | ID of the sales transaction that’s being configured such as a quote or an order. | Required | 60.0 |
| `transaction​LineId` | String | ID of the top-level line item that’s being configured. | Optional | 60.0 |
| `updated​Nodes` | [Configurator Updated Node Input](./connect_requests_configurator_updated_node_input.htm.md)[] | List of updated context nodes that’s passed to the product configurator. | Optional | 60.0 |

#### See Also

- [*Salesforce Help*: Context Service](https://help.salesforce.com/s/articleView?id=ind.context_service.htm&type=5&language=en_US)

- [*Developer Documentation*: Context Service](https://developer.salesforce.com/docs/atlas.en-us.264.0.industries_reference.meta/industries_reference/context_service_overview.htm)
