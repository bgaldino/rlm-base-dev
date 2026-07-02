---
page_id: connect_responses_bre_guardrails.htm
title: BRE Guardrails
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_bre_guardrails.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-06-25
---

# BRE Guardrails

Output representation of the BRE
guardrails
for each component.

JSON Sample
:   ```
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
| `result` | [BRE Guardrails Result](./connect_responses_bre_guardrails_result.htm.md "Output representation of the BRE Guardrails result.")[] | Guardrails associated with the specified BRE component. | Small, 63.0 | 63.0 |
