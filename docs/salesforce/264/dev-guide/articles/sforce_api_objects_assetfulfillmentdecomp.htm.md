---
page_id: sforce_api_objects_assetfulfillmentdecomp.htm
title: AssetFulfillmentDecomp
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_assetfulfillmentdecomp.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# AssetFulfillmentDecomp

Represents the relationship between an ordered asset and its
         corresponding fulfillment asset. This object is available in API version 62.0 and
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
- 
- 

                  

               

            
| Field | Details |
| --- | --- |
| FulfillmentSourceAssetId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** The identifier of the relationship between an asset and a fulfillment asset. This field is a polymorphic relationship field. **Relationship Name** FulfillmentSourceAsset **Refers To** Asset, FulfillmentAsset |
| FulfillmentTargetAssetId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** The identifier of the target asset that's being fulfilled. This field is a relationship field. **Relationship Name** FulfillmentTargetAsset **Refers To** FulfillmentAsset |
| IsUsedForFulfmtAssetActivation | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates if internal jobs are allowed to activate the related fulfillment asset. The default value is true. This field is available in API version 6.0 and later. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** The name of the asset that's being fulfilled. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** The ID of the user who created the request record. This field is a polymorphic relationship field. **Relationship Name** Owner **Refers To** Group, User |
| RelationshipType | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** The type of relationship between an asset and a fulfillment asset. Valid values are: `SourceBundleRoot` `SourceLineItem` |
| SegmentIdentifier | **Type** string **Properties** Create, Group, Nillable, Sort, **Description** The ID of the ramp segment associated with the asset state period. This field is available in API version 63.0 and later in orgs that have Revenue Management when the Ramp Deals setting is enabled. |
| Status | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** The status of the fulfillment asset. Valid values are: `Active` `Inactive` |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
            
            
               

**[AssetFulfillmentDecompHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object starting API version
                  65.0.

            
            
            
               

**[AssetFulfillmentDecompShare](./sforce_api_associated_objects_share.htm.md)**

               
: Sharing is available for the object.
