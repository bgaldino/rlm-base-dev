---
page_id: connect_requests_document_decision_input.htm
title: Document Decision Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_document_decision_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_requests.htm
fetched_at: 2026-06-25
---

# Document Decision Input

Input representation of the Document Decision request.

JSON example
:   ```
    {
      "inputs": [
        {
          "Country": "USA",
          "State": "CA"
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `inputs` | List<Map<String, Object>> | List of inputs passed to Decision Table. Each key is a Decision Table field name, and each value is valid for that field. | Required | 59.0 |
