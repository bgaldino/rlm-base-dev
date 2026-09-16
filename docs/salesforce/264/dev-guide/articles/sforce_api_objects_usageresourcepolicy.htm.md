---
page_id: sforce_api_objects_usageresourcepolicy.htm
title: UsageResourcePolicy
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_usageresourcepolicy.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# UsageResourcePolicy

Represents the policies applicable to the usage resource whether it’s
         associated with a sellable product or not. This object is available in API version 65
      and later.

      
         

#### Important

Where possible, we changed noninclusive terms to align with our
            company value of Equality. We maintained certain terms to avoid any effect on customer
            implementations.

      

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`
         

      

      

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

: 
: 

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Date and time when the current user last viewed or modified this record, a record related to this record, or a list view. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** Date and time when the current user last viewed or modified this record. |
| RatingFrequencyPolicyId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The rating frequency policy associated with the usage resource. This field is a relationship field. **Relationship Name** RatingFrequencyPolicy **Refers To** RatingFrequencyPolicy |
| UsageAggregationPolicyId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The usage aggregation policy associated with the usage resource. This field is a relationship field. **Relationship Name** UsageAggregationPolicy **Refers To** UsageResourceBillingPolicy |
| UsageCommitmentPolicyId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** The usage commitment policy associated with the usage resource. This field is a relationship field. **Relationship Name** UsageCommitmentPolicy **Refers To** UsageCommitmentPolicy |
| UsageOveragePolicyId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The usage overage policy associated with the usage resource. This field is a relationship field. **Relationship Name** UsageOveragePolicy **Refers To** UsageOveragePolicy |
| UsageResourceId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** The usage resource associated with the usage resource policy. This field is a relationship field. **Relationship Name** UsageResource **Relationship Type** Master-detail **Refers To** UsageResource (the master object) |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[UsageResourcePolicyFeed](./sforce_api_associated_objects_feed.htm.md)**

               
: Feed tracking is available for the object.

            
            
               

**[UsageResourcePolicyHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.
