---
page_id: connect_responses_business_rules_result.htm
title: Business Rules Results
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_business_rules_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Business Rules Results

Output representation of executing an expression set.

    
      
        
          

**JSON example**

          
: 
            

```
{
  "outputs": [
    {
      "result": {
        "Premium": "1200",
        "Tax": "100"
      },
      "variables": {
        "age": "25",
        "state": "CA"
      },
      "error": {
        "stepId": "<stepId>",
        "errorMessage": "The rule is missing inputs: ['var1', 'var2'] and 3 more steps have 5 error"
      }
    },
    {
      "result": {
        "Premium": "2400",
        "Tax": "300"
      }
    },
    {
      "result": {
        "Premium": "500",
        "Tax": "25"
      }
    }
  ],
  "aggregationResults": {
    "result": {
      "TotalPremium": "4100",
      "TotalTax": "425"
    },
    "error": {
      "stepId": "<stepId>",
      "errorMessage": "The rule is missing inputs: ['var1', 'var2'] and 3 more steps have 5 error"
    }
  }
}
```

          

        
      

      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `aggregationResults` | [Business Rule Aggregation Results Output](./connect_responses_business_rule_aggregation_results_output.htm.md) | The result of the aggregation step in an expression set. | Small, 55.0 | 55.0 |
| `outputs` | [Rule Result](./connect_responses_rule_result.htm.md)[] | List of outputs returned by an expression set. | Small, 55.0 | 55.0 |
