---
page_id: billing_sforce_api_objects_disputeitem.htm
title: Billing Fields on DisputeItem
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_disputeitem.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Fields on DisputeItem

      Represents a specific invoice line or charge that’s being disputed. The
         details include the total transaction amount, transaction date, disputed amount, reason,
         and status of the dispute. This object is available in API version 66.0 and
      later.

      

## Supported Calls

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`
         

      

## Special Access Rules

         
         

You need the Revenue Cloud Billing license, and the Billing Operations User or the
            Billing Customer Service User permission set to access this object.

      

      

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

                  

               

            
| Field | Details |
| --- | --- |
| ApprovedAmount | **Type** currency **Properties** Create, Filter, Nillable, Sort, Update **Description** The amount that’s approved to be credited to the customer. |
| InvoiceLineId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The invoice line ID associated with the dispute. This field is a relationship field. **Relationship Name** Invoice Line **Refers To** Invoice Line |

      

   

#### See Also

- [*Financial Services Cloud Developer Guide*: DisputeItem](https://developer.salesforce.com/docs/atlas.en-us.264.0.financial_services_cloud_object_reference.meta/financial_services_cloud_object_reference/sforce_api_objects_disputeitem.htm)
