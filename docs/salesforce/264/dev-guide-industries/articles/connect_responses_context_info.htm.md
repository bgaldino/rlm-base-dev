---
page_id: connect_responses_context_info.htm
title: Context Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_context_info.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Information

Output representation containing detailed information about a context.

      
        
          

**Sample Response**

          
: 
            

```
{
  "childBusinessObjectTypes": [
    "Order"
  ],
  "contextDefinitionId": "11Oxx0000006VjNEAU",
  "contextId": "3729ed60-d16d-41b8-8951-9ad4f6407ad2",
  "contextMappingId": "11jxx0000004Q83AAE",
  "isSuccess": true
}
```

          

        
      

              

              

              

              

              

            

              

              

              

              

              

            

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `childBusinessObjectTypes` | String[] | List of associated child business object types. | Small, 59.0 | 59.0 |
| `contextDefinitionId` | String | ID of the context definition record. | Small, 59.0 | 59.0 |
| `contextId` | String | Unique ID of the context. | Small, 59.0 | 59.0 |
| `contextMappingId` | String | Identifier for the context's mapping structure. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the request was successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
