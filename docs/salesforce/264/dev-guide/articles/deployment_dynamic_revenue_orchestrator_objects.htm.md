---
page_id: deployment_dynamic_revenue_orchestrator_objects.htm
title: Dynamic Revenue Orchestrator Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_dynamic_revenue_orchestrator_objects.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Dynamic Revenue Orchestrator Objects

This table provides the deployment sequence, object types, API names, and lookup fields
    for Dynamic Revenue Orchestrator objects in Revenue Management.

    

        
        
        
        
        
        
          
            

            

            

            

            

          

        

        
          
          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

        

      
| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Configuration | Fulfillment Step Definition Group | FulfillmentStepDefinitionGroup | 1 | None |
| Configuration | Fulfillment Step Definition | FulfillmentStepDefinition | 2 | Ruleset, ExpressionSet, FulfillmentStepDefinitionGroup, IntegrationProviderDef, User, Queue |
| Configuration | Fulfillment Step Dependency Definition | FulfillmentStepDependencyDef | 3 | FulfillmentStepDefinition |
| Configuration | Product Fulfillment Scenario | ProductFulfillmentScenario | 4 | FulfillmentStepDefinitionGroup, Ruleset, Product2, ProductClassification, FlowDefinition, StageDefinition, FlowRecord, FlowOrchestration |
| Configuration | Fulfillment Workspace | FulfillmentWorkspace | 5 | None |
| Configuration | Fulfillment Workspace Item | FulfillmentWorkspaceItem | 6 | FulfillmentWorkspace, FulfillmentStepDefinitionGroup |
| Configuration | Fulfillment Fallout Rule | FulfillmentFalloutRule | 7 | IntegrationProviderDef, Group |
| Configuration | Fulfillment Step Jeopardy Rule | FulfillmentStepJeopardyRule | 8 | IntegrationProviderDef |
| Configuration | Fulfillment Task Assignment Rule | FulfillmentTaskAssignmentRule | 9 | Ruleset, ExpressionSet, User, Queue |
| Configuration | Product Fulfillment Decomposition Rule | ProductFulfillmentDecompRule | 1 | Ruleset, Product2, ProductClassification |
| Configuration | Value Transformation Group | ValTfrmGrp | 2 | None |
| Configuration | Value Transformation | ValTfrm | 3 | ValTfrmGrp, AttributePicklistValue |
| Configuration | Product Decomposition Enrichment Rule | ProductDecompEnrichmentRule | 4 | ProductFulfillmentDecompRule, ExpressionSet, AttributeDefinition, ValTfrmGrp, DecisionMatrixDefinition |
| Configuration | Product Decomposition Enrichment Variable Mapping | ProdtDecompEnrchVarMap | 5 | ProductDecompEnrichmentRule, AttributeDefinition |

  

#### See Also

- [*Revenue Cloud Developer Guide*: Dynamic Revenue Orchestrator Standard
       Objects](./dynamic_revenue_orchestrator_std_objects_parent.htm.md)

- [Explore the Revenue Cloud Data Model](https://help.salesforce.com/s/articleView?id=ind.data_model_overview.htm&language=en_US)
