---
page_id: deployment_product_configurator_additional_info.htm
title: Product Configurator Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_product_configurator_additional_info.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Configurator Additional Information

Get to know additional deployment information for Product Configurator in Revenue
    Cloud, including active or inactive states, object information, and migration
    considerations.

    

## Object-Specific Information

      
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

            
              

              

              

            

            
              

              

              

            

          

        
| Object Name | Object API | Notes |
| --- | --- | --- |
| Product Configuration Rule | ProductConfiguration​Rule | ProductConfigurationRule has a Binary Large Object (BLOB) for the rule content. ConfigurationRuleDefinition contains a JSON with the rules details. The BLOB references product IDs, which can't be migrated as is. You must use the [npm migration utility](https://www.npmjs.com/package/rev-config-rule-migrator?activeTab=code) for the migration. ProductConfigurationRule has a status field. |
| Product Configuration Flow | ProductConfiguration​Flow | ProductConfigurationFlow has a status field. You don't require an API to set the status. |
| ExpressionSet​ConstraintObj | ExpressionSet​ConstraintObj | The ExpressionSet for Constraints has a status field. The ReferenceObjectId lookup field is polymorphic and references object IDs. |

    

    

## Other Information

        
- You can't update rules in active status.

        
- Product catalog management data must be migrated before the associations
          (ExpressionSetConstraintObj) are migrated and before the Business Rules Engine rules
          (ProductConfigurationRule) are migrated. When updating an Expression Set (Constraint
          Model), the target must be deactivated.

        
- Cross-Module Synchronization—Constraint Modeling Language (CML) and Business
          Rules Engine rules both reference product catalog management data. This data must be
          migrated before the business rules or the constraint rules.

        
- These components have dependencies on Industries common features.
            
  - Business Rules Product Configuration Rules—Business Rules Engine and Context
              Service

            
  - Constraint Builder Product Configuration Rules—Expression Set and Context
              Service

            
  - Product Configurator—Flow

          

      

In a future version of this guide, we plan to add information for moving Constraint
        Modeling Language (CML) code and related expression sets.
