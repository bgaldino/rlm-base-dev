---
page_id: sforce_api_objects_usagegrantrolloverpolicy.htm
title: UsageGrantRolloverPolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usagegrantrolloverpolicy.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# UsageGrantRolloverPolicy

      Represents a policy about the rollover of a usage grant.This object is
      available in API version 62.0 and later. 

      

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

                  

            

            
| Field | Details |
| --- | --- |
| Code | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** A unique user-defined string for the usage grant rollover policy. |
| IsRolloverAllowed | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the policy allows the rollover of the usage grant. The default value is `false`. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The date when this record was last referenced. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp for when the current user last viewed a record related to this record. |
| MaximumRolloverCount | **Type** int **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The maximum number of times that the usage grant can roll over. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** The name of the rollover policy record. |
| ShouldAllowRolloverExpiry | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the rollover for the associated usage grant is allowed to expire. The default value is `false`. |
| Status | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** Specifies the status of the rollover policy. Possible values are: `Active` `Draft` `Inactive` |

      

      

## Associated Objects

         
         

This object has these associated objects. If the API version isn’t specified, they’re
            available in the same API versions as this object. Otherwise, they’re available in the
            specified API version and later.

         
            
               

**[UsageGrantRolloverPolicyFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[UsageGrantRolloverPolicyHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.
