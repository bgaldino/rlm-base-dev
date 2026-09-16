---
page_id: cml_require_rule_vs_constraint.htm
title: Require Rule vs Constraint
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_require_rule_vs_constraint.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_constraints.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Require Rule vs Constraint

In Constraint Modeling Language (CML), constraint() and require() can both enforce
    behavior, but they operate differently: constraint focuses on logical consistency, require
    focuses on physical presence of products.

    
      

Here's a comparison between `constraint()` and
          `require()`.

      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

            
              

              

              

            

          

        
| Feature | constraint() | require() |
| --- | --- | --- |
| Primary goal | Validates if a condition is met (LHS) and operates on the result (RHS). | Forces a product to be present. |
| Engine action | Resolves the constraint or displays an error if there are no options to resolve. | Adds the required product to the quote. |
