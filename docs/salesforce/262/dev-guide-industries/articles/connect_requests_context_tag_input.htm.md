---
page_id: connect_requests_context_tag_input.htm
title: Context Tag Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_tag_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Tag Input

Input representation of the context tag.

JSON example
:   ```
    {
        "contextTags": [
            {
                "name": "Attribute_Tag",
                "contextAttributeId": "11nxx000001hOozAAE"
            },
            {
                "name": "Node_Tag",
                "contextNodeId": "11oxx000001G9D2AAK"
            }
        ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextAttributeId` | String | ID of the (parent) context attribute. | Required | 59.0 |
    | `contextNodeId` | String | ID of the (parent) context node. | Required | 59.0 |
    | `contextTagId` | String | ID of this Context tag. Required only for update. | Optional | 59.0 |
    | `name` | String | Name of the context tag. | Required | 59.0 |
