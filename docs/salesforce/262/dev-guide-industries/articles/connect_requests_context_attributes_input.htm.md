---
page_id: connect_requests_context_attributes_input.htm
title: Context Attributes Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_attributes_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-06-25
---

# Context Attributes Input

Input representation of context attribute.

JSON example
:   ```
    {
        "contextAttributes": [
            {
                "dataType": "STRING",
                "fieldType": "INPUT",
                "name": "Attribute_5",
                "tags": {
                    "contextTags": [
                        {
                            "name": "Attribute_5_Tag"
                        }
                    ]
                }
            },
            {
                "dataType": "NUMBER",
                "fieldType": "OUTPUT",
                "name": "Attribute_6"
            }
        ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `contextAttributeId` | String | ID of the attribute. | Required | 59.0 |
    | `dataType` | String | Data type of the attribute. | Required | 59.0 |
    | `domainSet` | String | Comma separated node names referenced by this attribute. | Optional | 59.0 |
    | `fieldType` | String | Field type of the attribute. | Required | 59.0 |
    | `isKey` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Optional | 59.0 |
    | `isValue` | Boolean | Specifies if it used for transposable feature (`true`) or not (`false`). | Optional | 59.0 |
    | `name` | String | Name of the attribute. | Required | 59.0 |
    | `tags` | [Context Tag Input](./connect_requests_context_tag_input.htm.md "Input representation of the context tag.")[] | List of tags for the attribute. | Optional | 59.0 |
