---
page_id: product_catalog_management_fields_on_product_relationship_type.htm
title: Product Catalog Management Fields on Product Relationship Type
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/product_catalog_management_fields_on_product_relationship_type.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_fields_on_standard_objects.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Catalog Management Fields on Product Relationship Type

      Standard and custom fields extend the standard Product Relationship Type
         object for use in Product Catalog Management.

      

## Fields

         
         

               
               
               
                  
                     

                     

                  

               

               
                  
                     

                     

: 

: 

: 
: 
- 
- 

                  

               

            
| Field | Details |
| --- | --- |
| AssociatedProductRoleCat | **Type** picklist **Properties** Create, Filter, Group, Nillable, Restricted picklist, Sort **Description** The role that the associated component plays in the relationship. Valid values are: `BundleComponent`— The associated product is part of a bundle. `ClassificationComponent`— The associated component is a product classification. Available in API version 61.0 and later |

      

   

#### See Also

- [Product Relationship Type](https://developer.salesforce.com/docs/atlas.en-us.264.0.object_reference.meta/object_reference/sforce_api_objects_productrelationshiptype.htm)
