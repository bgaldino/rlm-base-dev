---
page_id: sforce_api_objects_productsellingmodel.htm
title: ProductSellingModel
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_productsellingmodel.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ProductSellingModel

      Defines one method by which a product can be sold; for example, as a one-time
         sale, an evergreen subscription, or a termed subscription. If the product is sold on
         subscription, this object defines the subscription’s term. A product can have multiple
         product selling models.  This object is available in API version 60.0 and later. 

      

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

: 

                  

                  
                     

                     

: 

: 

: 
: 
- 
- 
- 
- 

                  

                  
                     

                     

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

                  

            

            
| Field | Details |
| --- | --- |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Indicates when the user last referred to this record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Indicates when the user last viewed this record. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** The name given to the product selling model. |
| PricingTerm | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The number of pricing term units in the pricing term. Used with PricingTermUnit to define the length of the pricing term. For example, if PricingTermUnit is Months and this field is 1, the subscription is priced monthly.If the selling model is one-time, this field must be null. |
| PricingTermUnit | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The unit of time used to define the pricing term. Used with PricingTerm to define the length of the pricing term. For example, if this field is Months and PricingTerm is 1, the subscription is priced monthly. If the selling model is one-time, this field must be null. Possible values are: `Months` `Quarterly` `Semi-Annual` `Annual` |
| SellingModelType | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update **Description** Indicates whether the product is sold as a one-time sale, an evergreen subscription, or a subscription with a defined term. Possible values are: `Evergreen` `OneTime` `TermDefined` The default value is `OneTime`. |
| Status | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update **Description** The status of the product selling model. Possible values are: `Active` `Draft` `Inactive` The default value is `Draft`. |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
            
               

**[ProductSellingModelFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[ProductSellingModelHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.
