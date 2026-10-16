---
page_id: quote_and_order_capture_fields_on_object_state_definition.htm
title: Transaction Management Fields on Object State Definition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_object_state_definition.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Transaction Management Fields on Object State Definition

      Standard and custom fields extend the standard Object State Definition object
         for use in Transaction Management to represent the object state model for a particular
         status field for an entity.  This object is available in API version 60.0 and later. 

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| AppUsageType | **Type** string **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** This field indicates under which AppUsageType the transition applies to. For example, ObjectStateDefinition associated with “Revenue Lifecycle Management” AppUsageType will apply to quotes, assets, or orders associated with “Revenue Lifecycle Management”. |
