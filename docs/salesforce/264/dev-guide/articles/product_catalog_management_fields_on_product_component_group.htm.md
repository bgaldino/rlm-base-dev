---
page_id: product_catalog_management_fields_on_product_component_group.htm
title: Product Catalog Management Fields on Product Component Group
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_component_group.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Catalog Management Fields on Product Component Group

      Standard and custom fields extend the standard Product Component Group object
         for use in Product Catalog Management.

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 
: 

: 

: 

                  

               

            
| Field | Details |
| --- | --- |
| ParentGroupId | **Type** reference **Properties** Create, Filter, Group, Nillable, Sort, Update **Description** The parent product component group in a nested group hierarchy for the same parent product. Available in API version 62.0 and later. This field is a relationship field. **Relationship Name** ParentGroup **Refers To** ProductComponentGroup |

      

   

#### See Also

- [Product Component Group](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_productcomponentgroup.htm)
