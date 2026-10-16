---
page_id: connect_responses_lookup_tables_result_list.htm
title: Lookup Tables Result List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_lookup_tables_result_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Lookup Tables Result List

Output representation of the result of a lookup table search
      request.

      
        
          

**JSON example**

          
: 
            

```
{
  "code": "200",
  "isSuccess": true,
  "lookupTables": [
    {
      "id": "0lIxx000000003FEAQ",
      "lookupTableDefinitionId": "0lDxx000000001dEAA",
      "lookupTableType": "DecisionTable",
      "name": "DT_Apr27_2",
      "apiName": "DT_Apr27_2"
    }
  ],
  "message": ""
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Response code of the API request. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `lookupTables` | [Lookup Table Details](./connect_responses_lookup_table_details.htm.md)[] | List of the retrieved lookup tables. | Small, 59.0 | 59.0 |
| `message` | String | API response message if the request fails. | Small, 59.0 | 59.0 |
