---
page_id: connect_responses_bre_guardrails_result.htm
title: BRE Guardrails Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_bre_guardrails_result.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-06-25
---

# BRE Guardrails Result

Output representation of the BRE Guardrails result.

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
| `component​Name` | String | Name of the BRE component that the guardrail is fetched for. | Small, 63.0 | 63.0 |
| `guardrails` | [Guardrails](./connect_responses_guardrails.htm.md "Output representation of each guardrail that includes information to manage system thresholds and notifications in BRE components.")[] | Specify the guardrails for the provided BRE component. | Small, 63.0 | 63.0 |
