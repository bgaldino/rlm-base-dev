---
page_id: connect_responses_explainability_action_log_create.htm
title: Explainability Action Log Create
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_explainability_action_log_create.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Decision Explainer
parent_page: decision_explainer_apis_responses.htm
fetched_at: 2026-06-25
---

# Explainability Action Log Create

Output representation of the create Explainability action log
request.

JSON example
:   ```
    {
       "sequenceNumber" : 1,
       "uniqueIdentifier" : "de3b62ae-410b-419a-b75e-1d2d5cb24b88"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `sequenceNumber` | Integer | The sequence number of the explainability action log. | Small, 54.0 | 54.0 |
| `uniqueIdentifier` | String | The unique ID of the explainability action log created after a successful create request. | Small, 54.0 | 54.0 |
