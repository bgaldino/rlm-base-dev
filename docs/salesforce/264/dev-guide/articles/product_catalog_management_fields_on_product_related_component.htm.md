---
page_id: product_catalog_management_fields_on_product_related_component.htm
title: Product Catalog Management Fields on Product Related Component
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_related_component.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Catalog Management Fields on Product Related Component

      Standard and custom fields extend the standard Product Related Component
         object for use in Product Catalog Management.

      

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
- 
- 
- 

                  

               

            
| Field | Details |
| --- | --- |
| ChildProductClassificationId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort **Description** The child product classification that's associated with a product. This field is a relationship field. **Relationship Name** ChildProductClassification **Refers To** ProductClassification |
| QuoteVisibility | **Type** picklist **Properties** Create, Defaulted on create, Filter, Group, Nillable, Restricted picklist, Sort, Update **Description** Specifies the product-related component to display as a quote line item in the Transaction Line Editor and the quote document. The default value is Always. Possible values are: Always Transaction Line Editor Only Quote Document Only Never |

      

   

#### See Also

- [Product Related Component](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_productrelatedcomponent.htm)
