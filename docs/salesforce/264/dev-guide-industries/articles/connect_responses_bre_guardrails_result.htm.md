---
page_id: connect_responses_bre_guardrails_result.htm
title: BRE Guardrails Result
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_bre_guardrails_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-11-23
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_bre_guardrails_result.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
