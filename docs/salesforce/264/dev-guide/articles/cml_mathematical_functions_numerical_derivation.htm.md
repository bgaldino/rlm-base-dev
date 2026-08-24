---
page_id: cml_mathematical_functions_numerical_derivation.htm
title: Mathematical Functions (Numerical Derivation)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/cml_mathematical_functions_numerical_derivation.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: cml_variables.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Mathematical Functions (Numerical Derivation)

Mathematical functions and operators are used to calculate derived values based on
    arithmetic relationships between variables.

    
      

          
          
          
          
            
              

              

              

            

          

          
            
              

              

              

            

            
              

              

              

            

          

        
| Function/Operator | Purpose | CML Keyword/Operator [Source] |
| --- | --- | --- |
| Arithmetic Operators | Perform standard arithmetic: addition (+), subtraction (-), multiplication (*), division (/), modulo (% or mod), and power (^). | `+, -, *, /, %, ^` |
| ceil() | Returns the smallest integer greater than or equal to the argument (rounds up). | `ceil` |

    

    

## Usage Example

      
      

```
surgeLoadKW == requiredKW * 1.25);
ceil(totalItems / itemsPerCrate)

```

      

See [Arithmetic Calculations and Functions](./cml_core_concept_examples.htm.md) and examples [here](./cml_business-centric_cml_guidelines_quantity_and_aggregation_fun.htm.md).
