---
page_id: connect_resources_save_product_configurations.htm
title: Saved Configuration (GET, POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_save_product_configurations.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_resources.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Saved Configuration (GET, POST)

Save and reuse a record's configurations, and get a list of the saved configurations
    for a record.

    
      
        
          

**Resource**

          
: 
            

```
/connect/cpq/configurator/saved-configuration
```

          

        
        
          

**Resource example**

          
: 
            

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/cpq/configurator/saved-configuration
```

          

        
        
          

**Available version**

          
: 63.0

        
        
          

**HTTP methods**

          
: GET, POST

        
        
          

**Request parameters for GET**

          
: 
            

                
                
                
                
                
                
                  
                    

                    

                    

                    

                    

                  

                

                
                  
                    

                    

                    

                    

                    

                  

                

              
| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceRecordId` | String | ID of the record whose saved configurations must be retrieved. | Required | 63.0 |

          

        
        
          

**Response body for GET**

          
: [Configuration
              List](./connect_responses_favorite_list_output_represenation.htm.md)

        
        
          

**Request body for POST**

          
: 
            

**JSON example**

: 

```
{
  "data": "{\"LegalEntity\":null,\"ProductName\":\"Monitor\",\"businessObjectType\":\"QuoteLineItem\",\"Product\":\"01txx0000006i2aAAA\",\"ItemIsPrimarySegment\":false,\"ListPrice\":144.99,\"ValidationResult\":null,\"StartDate\":null,\"ContractVolumePasId\":null,\"BillingTreatment\":null,\"PeriodBoundaryStartMonth\":null,\"SalesTransactionSourceAsset\":null,\"id\":\"0QLxx0000004C9VGAU\",\"PartnerDiscountPercent\":10,\"PriceWaterFall\":null,\"BillingFrequency\":null,\"ProductCode\":\"MO001\",\"DerivedPricingAttribute\":false,\"TaxTreatment\":null,\"Subtotal\":1739.88,\"ItemRampIdentifier\":null,\"ItemSegmentName\":null,\"SalesTransactionItemAttribute\":[{\"AttributeKey\":\"0tjxx0000000001AAA\",\"AttributeValue\":\"1080p Built-in Display\",\"ParentReference\":\"0QLxx0000004C9VGAU\",\"AttributePicklistValue\":\"0v6xx0000000001AAA\",\"IsPriceImpacting\":false,\"businessObjectType\":\"QuoteLineItemAttribute\",\"AttributeName\":\"Display\",\"id\":\"0zuxx000000000FAAQ\",\"AttributeDefinitionCode\":null,\"SalesTransactionItemAttrParent\":\"0QLxx0000004C9VGAU\"},{\"AttributeKey\":\"0tjxx0000000009AAA\",\"AttributeValue\":\"24 Inch\",\"ParentReference\":\"0QLxx0000004C9VGAU\",\"AttributePicklistValue\":\"0v6xx000000000GAAQ\",\"IsPriceImpacting\":false,\"businessObjectType\":\"QuoteLineItemAttribute\",\"AttributeName\":\"Display_Size\",\"id\":\"0zuxx000000000GAAQ\",\"AttributeDefinitionCode\":null,\"SalesTransactionItemAttrParent\":\"0QLxx0000004C9VGAU\"}],\"PricebookEntry\":\"01uxx0000008yX0AAI\",\"DiscountAmount\":null,\"PricingTermCount\":0,\"SubscriptionTermUnit\":null,\"NetUnitPrice\":144.99,\"ItemEffectiveGrantDate\":null,\"ProductCategory\":null,\"SalesTransactionAction\":null,\"SalesTransactionActionType\":null,\"SalesTransactionItemGroup\":null,\"PeriodBoundaryDay\":null,\"SalesTrxnItemDescription\":null,\"LineItemDistributionType\":null,\"ProrationPolicy\":null,\"ContractDiscountType\":null,\"TransactionType\":null,\"ParentReference\":\"0Q0xx0000004C92CAE\",\"Discount\":null,\"PricingTermUnit\":null,\"ProductSellingModel\":\"0jPxx0000000001EAA\",\"PricingSource\":null,\"StockKeepingUnit\":null,\"PartnerUnitPrice\":130.491,\"ItemTotalAdjustmentAmount\":0,\"SalesTransactionItemSource\":\"0QLxx0000004C9VGAU\",\"ContractAttributePasId\":null,\"SubscriptionTerm\":null,\"SellingModelType\":\"OneTime\",\"EndQuantity\":12,\"NetTotalPrice\":1739.88,\"TotalLineAmount\":1739.88,\"ItemSegmentType\":null,\"ProductBasedOn\":\"11Bxx000002C1nqEAC\",\"Deleted\":false,\"BillingReference\":null,\"ArePartialPeriodsAllowed\":false,\"ItemRecordedPrice\":null,\"CustomProductName\":null,\"ItemSegmentIdentifier\":null,\"SalesTransactionItemParent\":\"0Q0xx0000004C92CAE\",\"Quantity\":12,\"PeriodBoundary\":null,\"ContractDiscountValue\":null,\"LineItemDiscountValue\":null,\"ContractId\":null,\"EndDate\":null,\"ItemGroupSummarySubtotal\":null,\"IsContracted\":false,\"UnitPrice\":144.99,\"StartQuantity\":null,\"ContractPrice\":null,\"TotalPrice\":1739.88,\"LineItemDiscountType\":null,\"ItemPath\":\"01txx0000006i2aAAA\",\"productKey\":[\"0QLxx0000004C9VGAU\"]}\",
  \"description\": \"This configuration is saved for reuse.\",
  \"name\": \"Favorite Configuration\",
  \"referenceRecordId\": \"01txx0000006iCFAAY\"
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `data` | String | JSON object that contains the details of the sales transaction, formatted as a string. | Optional | 63.0 |
| `description` | String | Description of the saved configuration. | Optional | 63.0 |
| `name` | String | Name of the saved configuration. | Optional | 63.0 |
| `referenceRecord​Id` | String | ID of the record for which the configuration must be saved. | Required | 63.0 |

          

        
        
          

**Response body for POST**

          
: [Configuration Record
            Save](./connect_responses_create_favorite_output.htm.md)

        
      

    

  

#### See Also

- [*Salesforce Help*: Considerations to Save and Reuse Configurations](https://help.salesforce.com/s/articleView?id=ind.product_configurator_considerations_to_save_and_reuse_configurations.htm&language=en_US)
