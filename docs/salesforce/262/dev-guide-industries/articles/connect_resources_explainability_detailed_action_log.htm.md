---
page_id: connect_resources_explainability_detailed_action_log.htm
title: Explainability Detailed Action Log (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_explainability_detailed_action_log.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_apis_resources.htm
fetched_at: 2026-06-25
---

# Explainability Detailed Action Log (GET)

Retrieve detailed action logs and combine log segments to generate a consolidated
explainability action log.

Resource
:   ```
    /connect/decision-explainer/detailed-action-log
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/decision-explainer/detailed-action-log?actionContextCode=001xx000003GYiCAAW&applicationType=0&applicationSubType=BREDES&processType=BREDES&actionLogDateTime=2024-03-06T05:09:32.000Z&uniqueIdentifier=f89eff41-94ed-4fe7-9b72-f6df2bb5f4aa
    ```

Available version
:   61.0

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `actionContextCode` | String | Record ID within the context of the associated application's action that can be used to retrieve the action log | Required | 61.0 |
    | `actionLogDateTime` | String | Date and time when the explainability action log records are to be returned Date format - yyyy-MM-ddTHH:mm:ss.SSSZ. | Required | 61.0 |
    | `applicationSubType` | String | Subtype of the associated application for which the explainability log is generated. | Required | 61.0 |
    | `applicationType` | String | Name of the application for which the explainability service is run. | Required | 61.0 |
    | `processType` | String | Type of business process associated with the explainability action. | Required | 61.0 |
    | `uniqueIdentifier` | String | A unique ID that's associated with a specific explainability action log. | Required | 61.0 |

Response body for GET
:   [Explainability Detailed Action Log Detail](./connect_responses_explainability_detailed_action_log_detail.htm.md "Output representation of explainability action log in detail.")
