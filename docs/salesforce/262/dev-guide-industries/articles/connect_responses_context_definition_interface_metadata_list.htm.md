---
page_id: connect_responses_context_definition_interface_metadata_list.htm
title: Context Definition Interface Metadata List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_definition_interface_metadata_list.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-06-25
---

# Context Definition Interface Metadata List

Output representation of the metadata list associated with the context definition
interfaces.

JSON example
:   ```
    {
      "contextDefinitionInterfaceMetadataList": [
        {
          "createdBy": "Automated Process",
          "createdDate": "2024-05-15T00:00:00.000Z",
          "description": "Test Interface",
          "developerName": "TestBaseInterface",
          "interfaceName": "TestBaseInterface",
          "lastModifiedBy": "Automated Process",
          "parentInterfaces": [
            "TestBaseInterface1"
          ],
          "version": "62.1"
        }
      ],
      "contextDefinitionInterfaceMetadataListId": "43db7f18-9dd7-40a2-9a34-a2b3a1cff9e5",
      "isSuccess": true
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinition​Interface​MetadataList` | [Context Definition Interface Metadata](./connect_responses_context_definition_interface_metadata.htm.md "Output representation of the metadata associated with the context definition interface.")[] | List of metadata associated with the context definition interfaces. | Small, 62.0 | 62.0 |
| `contextDefinition​Interface​MetadataListId` | String | Unique ID of the metadata list associated with the context definition interfaces. Required for Lightning Data Service (LDS). | Small, 62.0 | 62.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 62.0 | 62.0 |
