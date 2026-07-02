---
page_id: connect_responses_decision_table_data_output.htm
title: Decision Table Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_data_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-06-25
---

# Decision Table Data

Output representation of the status of an action performed.

Sample Output
:   ```
    {
      "errors": [],
      "errorFileId": "string_value"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​FileId` | String | Error code if transaction failed for any reason. | Small, 62.0 | 62.0 |
| `errors` | String[] | List of error messages if transaction failed for any reason. | Small, 62.0 | 62.0 |
