---
page_id: product_catalog_management_fields_on_product_category.htm
title: Product Catalog Management Fields on Product Category
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_category.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Catalog Management Fields on Product Category

Standard and custom fields extend the standard Product Category
         object for use in Product Catalog Management.

      

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
| Code | **Type** string **Properties** Create, Filter, Group, idLookup, Nillable, Sort, Update **Description** A unique ID associated with the catalog. The maximum size is 80 alphanumeric characters. |
| IsNavigational | **Type** boolean **Properties** Create, Defaulted on create, Filter, Group, Sort, Update **Description** Indicates whether the category or subcategory is shown in the menu as a navigational breadcrumb (`true`) or not (`false`). Available in API version 62.0 and later. The default value is `false`. |

      

   

#### See Also

- [Product Category](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_productcategory.htm)
