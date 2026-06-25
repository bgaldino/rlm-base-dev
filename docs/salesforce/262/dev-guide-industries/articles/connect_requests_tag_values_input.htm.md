---
page_id: connect_requests_tag_values_input.htm
title: Tag Values Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_tag_values_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Tag Values Input

Input representation of the list of Tag Names to be updated and their
values.

JSON example
:   ```
                    {
                        "tagName": "Name",
                        "tagValue": "updatedAccount"
                    },
                    {
                        "tagName": "City",
                        "tagValue": "Bangalore"
                    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `tagName` | String | Name of tag thats need to be updated. | Required | 63.0 |
    | `tagValue` | String | Updated value of tags. | Required | 63.0 |
