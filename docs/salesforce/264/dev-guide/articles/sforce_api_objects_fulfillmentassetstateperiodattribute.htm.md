---
page_id: sforce_api_objects_fulfillmentassetstateperiodattribute.htm
title: FulfmtAssetStatePeriodAttr
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_fulfillmentassetstateperiodattribute.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_std_objects_parent.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# FulfmtAssetStatePeriodAttr

      Represents the key-value pair of a fulfillment asset attribute applicable
         during a specific asset state period. This object is available in API version 67.0 and
      later. 

      

## Supported Calls

         
         

            `create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `query()`, `retrieve()`, `update()`, `upsert()`
         

      

      

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

                  

               

            
| Field | Details |
| --- | --- |
| AttributeDefinitionId | **Type** reference **Properties** Create, Filter, Group, Sort, Update **Description** Represents the definition of the fulfillment asset state period attribute. This field is a relationship field. **Relationship Name** AttributeDefinition **Refers To** AttributeDefinition |
| AttributeName | **Type** string **Properties** Filter, Group, idLookup, Nillable, Sort **Description** Represents the name of the fulfillment asset state period attribute. |
| AttributePicklistValueId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Represents the reference identifier of the selected picklist value. This field is a relationship field. **Relationship Name** AttributePicklistValue **Refers To** AttributePicklistValue |
| AttributeValue | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Represents the value of the fulfillment asset state period attribute. |
| ExternalId | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** Represents the external ID of the fulfillment asset state period attribute. |
| FulfillmentAssetStatePeriodId | **Type** reference **Properties** Create, Filter, Group, Sort **Description** Represents the fulfillment asset period applicable to the object. This field is a relationship field. **Relationship Name** FulfillmentAssetStatePeriod **Relationship Type** Master-detail **Refers To** FulfillmentAssetStatePeriod (the master object) |
