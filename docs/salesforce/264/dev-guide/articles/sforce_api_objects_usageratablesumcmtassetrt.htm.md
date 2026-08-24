---
page_id: sforce_api_objects_usageratablesumcmtassetrt.htm
title: UsageRatableSumCmtAssetRt
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usageratablesumcmtassetrt.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# UsageRatableSumCmtAssetRt

      Represents the rate that’s calculated and applicable for the usage resource
         associated with the commitment assets related to an anchor. This object is available
      in API version 65.0 and later.

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

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
      

      

      

## Special Access Rules

         
         
      

      

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

: 

: 

: 

                  

            

            
| Field | Details |
| --- | --- |
| CommitmentAssetId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** The asset ID associated with the Usage Ratable Summary. This field is a relationship field. **Relationship Name** CommitmentAsset **Refers To** Asset |
| ErrorCode | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the unique code generated when an error occurs. Valid value is `INTERNAL_ERROR`. |
| ErrorDescription | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Specifies the description of the error that occurred. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date when this record was last referenced. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed this record. |
| Name | **Type** string **Properties** Autonumber, Defaulted on create, Filter, idLookup, Sort **Description** Name of the Usage Commitment Summary record. |
| NetUnitRate | **Type** double **Properties** Create, Filter, Nillable, Sort, Update **Description** The calculated per-unit rate for usage after applying commitment-specific discounts during the rating process. |
| UsageRatableSummaryId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The usage ratable summary associated with the usage commitment summary record. This field is a relationship field. **Relationship Name** UsageRatableSummary **Relationship Type** Master-detail **Refers To** UsageRatableSummary (the master object) |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[UsageRatableSumCmtAssetRtHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.
