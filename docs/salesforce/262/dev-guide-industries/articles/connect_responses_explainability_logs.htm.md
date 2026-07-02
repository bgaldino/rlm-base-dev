---
page_id: connect_responses_explainability_logs.htm
title: Explainability Logs
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_explainability_logs.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_explainer_bre_responses.htm
fetched_at: 2026-06-25
---

# Explainability Logs

Output representation of the list of explainability action
logs.

JSON example
:   ```
    {
      "actionLogs": [
        {
          "actionContextCode": "001x0000005SdzIAAS",
          "actionLog": "{This is a sample action log data.}",
          "applicationLogDate": "Mon Aug 01 10:29:35 GMT 2022",
          "applicationSubtype": "ASD1",
          "applicationType": "0",
          "name": "EAD1",
          "processType": "BPT1"
        }
      ],
      "queryMore": " "
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `actionLogs` | [Explainability Log Detail](./connect_responses_explainability_log_detail.htm.md "Output representation of the list of explainability logs.")[] | The list of explainability logs that matches the search criteria. | Small, 56.0 | 56.0 |
| `queryMore` | String | A string that can be passed to the next call to fetch the next batch of explainability log records. | Small, 56.0 | 56.0 |
