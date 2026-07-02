---
page_id: connect_responses_context_definition_interface_attribute_tag.htm
title: Context Definition Interface Attribute Tag
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_attribute_tag.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Definition Interface Attribute Tag

Output representation of the attribute tags associated with the context definition
interface.

JSON example
:   ```
    {
      "attributeTags": [
        {
          "dataType": "REFERENCE",
          "isMappingRequired": false,
          "isNodeTag": false,
          "domainName": "Account",
          "tagName": "AccountRef_attr_tag"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataType` | String | Data type of the attribute associated with the context definition interface. | Small, 62.0 | 62.0 |
| `domainName` | String | Domain name of the attribute associated with the context definition interface. | Small, 62.0 | 62.0 |
| `isMappingRequired` | Boolean | Indicates whether the attribute tag must be mapped in the context definition (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isNodeTag` | Boolean | Indicates whether the attribute tag is a node tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isOptional` | Boolean | Indicates whether validation must be done for the attribute tag (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
| `tagName` | String | Name of the attribute tag. | Small, 62.0 | 62.0 |
