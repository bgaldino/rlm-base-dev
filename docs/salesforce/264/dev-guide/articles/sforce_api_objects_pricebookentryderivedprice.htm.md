---
page_id: sforce_api_objects_pricebookentryderivedprice.htm
title: PriceBookEntryDerivedPrice
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pricebookentryderivedprice.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# PriceBookEntryDerivedPrice

Represents the price of a product that’s derived from another source
         such as a product or an asset. This object is available in API version 61.0 and
      later.

      

## Supported Calls

      
      

         `create()`, 
         `delete()`, 
         `describeLayout()`, 
         `describeSObjects()`, 
         `getDeleted()`,
         `getUpdated()`,
         `query()`, 
         `retrieve()`, 
         `search()`, 
         `undelete()`, 
         `update()`, 
         `upsert()`
      

      

      

## Fields

         
         

               
               
            
               
                  

                  

               

            

            
                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

            

            
| Field | Details |
| --- | --- |
| ContributingProductId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort **Description** Source product from which the derived price is calculated. The source product is associated with the derived price product. This field is a relationship field. **Relationship Name** ContributingProduct **Relationship Type** Lookup **Refers To** Product2 |
| CurrencyIsoCode | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** ISO code for any currency allowed by the organization. Available only if the multicurrency feature is enabled. Valid values are: `BHD`—Bahraini Dinar `JPY`—Japanese Yen `USD`—U.S. Dollar The default value is `USD`. |
| DerivedPricingScope | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** Scope of the product based on which the derived price is calculated. Valid values are: `Both` `NonTransactional` `Transactional` |
| EffectiveFrom | **Type** dateTime **Properties** Create, Filter, Sort, Update **Description** Date and time when the derived pricing comes into effect. |
| EffectiveTo | **Type** dateTime **Properties** Create, Filter, Nillable, Sort, Update **Description** Date and time when the derived pricing is no longer in effect. |
| Formula | **Type** string **Properties** Create, Filter, Sort, Update **Description** Coded format of the formula used to calculate the derived price of a product from another product or asset. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Timestamp for when the current user last referred to this record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Timestamp for when the current user last viewed this record. If this value is null, it’s possible that this record was referenced (LastReferencedDate) and not viewed. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** Name of the derived price record. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** ID of the user who created the record. This field is a polymorphic relationship field. **Relationship Name** Owner **Relationship Type** Lookup **Refers To** Group, User |
| PricebookEntryId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** Price book entry associated with the source product. This field is a relationship field. **Relationship Name** PricebookEntry **Relationship Type** Lookup **Refers To** PricebookEntry |
| PricebookId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort **Description** Price book associated with the source product. This field is a relationship field. **Relationship Name** Pricebook **Relationship Type** Lookup **Refers To** Pricebook2 |
| PricingSource | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort **Description** Pricing type used to calculate the derived price of the product. Valid values are: `Header` `Product` |
| ProductId | **Type** reference **Properties** Filter, Group, Sort **Description** Product associated with the derived pricing. This field is a relationship field. **Relationship Name** Product **Relationship Type** Lookup **Refers To** Product2 |
| ProductSellingModelId | **Type** reference **Properties** Filter, Group, Sort **Description** Product selling model associated with this record. This field is a relationship field. **Relationship Name** ProductSellingModel **Relationship Type** Lookup **Refers To** ProductSellingModel |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
            
               

**[PriceBookEntryDerivedPriceFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[PriceBookEntryDerivedPriceHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.

            
            
            
               

**[PriceBookEntryDerivedPriceShare](./sforce_api_associated_objects_share.htm.md)**

               
: Sharing is available for the object.
