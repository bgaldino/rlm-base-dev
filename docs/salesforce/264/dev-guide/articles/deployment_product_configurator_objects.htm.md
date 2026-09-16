---
page_id: deployment_product_configurator_objects.htm
title: Product Configurator Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_product_configurator_objects.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Configurator Objects

This table provides the object deployment sequence and properties for Product
    Configurator in Revenue Management, including object types, API names, deployment sequences, and
    lookup fields.

    

        
        
        
        
        
        
          
            

            

            

            

            

          

        

        
          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

        

      
| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Configuration | Product Configuration Rule | ProductConfiguration​Rule | 1 | User |
| Configuration | Product Configuration Flow | ProductConfiguration​Flow | 1 | UserFlowIdentifier |
| Configuration | ExpressionSet​ConstraintObj | ExpressionSet​ConstraintObj | 1 | ExpressionSetId, ReferenceObjectId (Polymorphic) |
| Configuration | Product Configuration Flow Assignment | ProductConfig​FlowAssignment | 2 | User, ProductId, ProductClassificationId, ProductConfigurationFlow |
