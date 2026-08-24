---
page_id: connect_responses_context_mapping_list.htm
title: Context Mapping List Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_mapping_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Mapping List Output

Output representation
    of
    a
    list of context mappings.

      
        
          

**Sample Response**

          
: 
            

```
{
  "contextMappingListId": "915c3ffc-65e6-47fd-b9c1-3fdfa92421c1",
  "contextMappings": [
    {
      "contextDefinitionVersionId": "11pxx0000004UcCAAU",
      "contextMappingId": "11jxx0000004LYBAA2",
      "contextNodeMappings": [],
      "description": "mappingDescription",
      "intents": [
        "ASSOCIATION",
        "HYDRATION",
        "PERSISTENCE",
        "TRANSLATION"
      ],
      "isDefault": false,
      "isInputMapped": false,
      "name": "mappingName"
    }
  ],
  "isSuccess": true
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextMappingListId` | String | Unique ID of the context mapping list. | Small, 59.0 | 59.0 |
| `contextMappings` | [Context Mapping Output[]](./connect_responses_context_mapping.htm.md) | List of context mappings. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the operation is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
