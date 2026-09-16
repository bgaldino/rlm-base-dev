---
page_id: connect_responses_bre_guardrails_result.htm
title: BRE Guardrails Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_bre_guardrails_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# BRE Guardrails Result

Output representation of the BRE Guardrails result.

        
          

**JSON Sample**

          
: 
            

```
{
  "result": [
    {
      "componentName": "DecisionTable",
      "guardrails": [
        {
          "name": "MaxProcessLimit",
          "guardrailType": "RateLimit",
          "limitValue": "100",
          "currentValue": "50",
          "notificationSupported": true
        }
      ]
    }
  ]
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `component​Name` | String | Name of the BRE component that the guardrail is fetched for. | Small, 63.0 | 63.0 |
| `guardrails` | [Guardrails](./connect_responses_guardrails.htm.md)[] | Specify the guardrails for the provided BRE component. | Small, 63.0 | 63.0 |
