---
page_id: quote_and_order_capture_fields_on_order_item_relationship.htm
title: Transaction Management Fields on Order Item Relationship
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/quote_and_order_capture_fields_on_order_item_relationship.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: quote_and_order_capture_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Transaction Management Fields on Order Item Relationship

      Standard and custom fields extend the standard Order Item Relationship object
         for use in Transaction Management. This object is available in API version 58.0 and
      later.

      

## Special Access Rules

         
         

To view these fields, you must have the Revenue Cloud Advanced license. See [Order Item Relationship](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_orderitemrelationship.htm) for fields on the
            platform object.

      

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 
: 

: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| ProductRelatedComponentId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort **Description** The ID of the product that is included in a product bundle, a set, or a product and an add-on. This field is a relationship field. **Relationship Name** ProductRelatedComponent **Relationship Type** Lookup **Refers To** ProductRelatedComponent |
