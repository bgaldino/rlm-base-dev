---
page_id: billing_sforce_api_objects_assetactionsource.htm
title: Billing Fields on AssetActionSource
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/billing_sforce_api_objects_assetactionsource.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_extended_standard_object_fields.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Billing Fields on AssetActionSource

      Standard fields extend the AssetActionSource object for use in Billing to
         represent information about the billing term.

      

## Supported Calls

         
         

            `describeLayout()`, `describeSObjects()`, `getDeleted()`,
               `getUpdated()`, `query()`, `retrieve()`, `search()`
         

      

      

## Special Access Rules

         
         

You need the Revenue Cloud Billing license, and the Billing Admin permission set or the
            Billing Operations User permission set to access this object.

      

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| BillingTerm | **Type** int **Properties** Defaulted on create, Filter, Group, Nillable, Sort **Description** The number of billing frequency units to combine into a billing period item. Available in API version 68.0 and later. |
