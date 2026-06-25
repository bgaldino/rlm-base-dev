---
page_id: connect_requests_context_node_id_input.htm
title: Context Node ID Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_node_id_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Node ID Input

Input representation of the list of context node IDs to create the relationship nodes
for.

JSON example
:   ```
    {
      "contextNodeIds": [
        "11oxx000001G3dtAAC",
        "11oxx000001G3duAAC"
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextNodeIds` | String | List of context node IDs to create the relationship nodes by adding them as child nodes to the context node that’s specified in the endpoint. | Required | 61.0 |
