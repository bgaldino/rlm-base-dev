---
page_id: connect_responses_guardrails.htm
title: Guardrails
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_guardrails.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-11-23
---

# Guardrails

Output representation of each guardrail that includes information to manage system
thresholds and notifications in BRE components.

JSON Sample
:   ```
    {
      "guardrails": {
        "name": "MaxProcessLimit",
        "guardrailType": "RateLimit",
        "limitValue": "100",
        "currentValue": "50",
        "notificationSupported": true
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `currentValue` | String | Current value of the guardrail. | Small, 63.0 | 63.0 |
|  | [Guardrail Current Value](./connect_responses_guardrail_current_value.htm.md "Output representation of the current values of the guardrails along with the resource type.") | Resource type and the row-level current values of the guardrail. For future use only. | Small, 63.0 | 63.0 |
| `guardrail​Type` | Guardrail Type (enumeration of type string) | Type of guardrail. Valid values are:   - `RateLimit` - `OrgValueLimit` | Small, 63.0 | 63.0 |
| `limitValue` | String | Default or configured value of the given guardrail | Small, 63.0 | 63.0 |
|  | String | Maximum value of the given guardrail. For future use only. | Small, 63.0 | 63.0 |
| `multiValue` | Boolean | Specifies details if the current values are determined by an org level or aggregation of row levels. | Small, 63.0 | 63.0 |
| `name` | String | Name of the guardrail. | Small, 63.0 | 63.0 |
| `notification​Supported` | Boolean | Indicates whether the guardrail supports notifications (`true`) or not (`false`). | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_guardrails.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
