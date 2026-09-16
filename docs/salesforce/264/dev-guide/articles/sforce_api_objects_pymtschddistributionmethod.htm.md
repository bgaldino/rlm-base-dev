---
page_id: sforce_api_objects_pymtschddistributionmethod.htm
title: PymtSchdDistributionMethod
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_pymtschddistributionmethod.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# PymtSchdDistributionMethod

Represents information about the partial payments that the total
         payment is divided into. This object is available in API version 64.0 and
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
      

      

      

## Special Access Rules

         
         

You need the Revenue Cloud Billing license, and the Payment Admin permission set or the
            Payment Operations User permission set to access this object.

      

      

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

                  

            

            
| Field | Details |
| --- | --- |
| Description | **Type** textarea **Properties** Create, Filter, Nillable, Sort, Update **Description** The user-entered details of the payment schedule distribution method. |
| DistributionCount | **Type** int **Properties** Create, Filter, Group, Sort, Update **Description** Required. The number of payment schedule items for the payment schedule. The payment schedule items are used to distribute the payment schedule’s total payment into partial payments. |
| DistributionMethodType | **Type** picklist **Properties** Create, Filter, Group, Restricted picklist, Sort, Update **Description** Required. The time interval of the payment distribution method. Valid value is: `FullDistribution`—The full amount on the payment schedule is distributed to a single payment schedule item. |
| LastReferencedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last accessed this record indirectly, for example, through a list view or related record. |
| LastViewedDate | **Type** dateTime **Properties** Filter, Nillable, Sort **Description** The timestamp when the current user last viewed this record or list view. If this value is null, and LastReferenceDate is not null, the user accessed this record or list view indirectly. |
| Name | **Type** string **Properties** Create, Filter, Group, idLookup, Sort, Update **Description** Required. The user-entered name for the payment schedule distribution method. |
| OwnerId | **Type** reference **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Required. The ID of the owner of the PaymentScheduleDistributionMethod record. This field is a polymorphic relationship field. **Relationship Name** Owner **Refers To** Group, User |

      

      

## Associated Objects

         
         

This object has the following associated objects. If the API version isn’t specified,
            they’re available in the same API versions as this object. Otherwise, they’re available
            in the specified API version and later.

         
            
               

**[PymtSchdDistributionMethodHistory](./sforce_api_associated_objects_history.htm.md)**

               
: History is available for tracked fields of the object.
