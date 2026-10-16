---
page_id: deployment_contracts_objects.htm
title: Salesforce Contracts Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_contracts_objects.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_A.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Salesforce Contracts Objects

This table provides the deployment sequence, object types, API names, and lookup fields
    for Salesforce Contracts in Revenue Management.

    

        
        
        
        
        
        
          
            

            

            

            

            

          

        

        
          
            

            

            

            

            

          

          
            

            

            

            

            

          

          
            

            

            

            

            

          

        

      
| Object Use Type | Object Name | Object API | Deployment Sequence | Lookup Fields (Foreign Keys) |
| --- | --- | --- | --- | --- |
| Metadata | Clause Category Configuration | ClauseCatgConfiguration | 1 | None |
| Configuration | Document Clause Set | DocumentClauseSet | 2 | ClauseCatgConfiguration |
| Configuration | Document Clause | DocumentClause | 3 | DocumentClauseSet, ContentDocument |
