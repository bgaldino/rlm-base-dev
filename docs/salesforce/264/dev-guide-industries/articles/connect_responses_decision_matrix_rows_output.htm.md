---
page_id: connect_responses_decision_matrix_rows_output.htm
title: Decision Matrix Rows Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_rows_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Rows Output

Output representation of rows of a decision matrix
    version.

      
        
          

**JSON example**

          
: 
            

```

   "message" : null,
   "rows" : [ {
      "id" : "a1j5w000005D04uAAC",
      "name" : "303b5c8988601647873b4ffd247d83cb",
      "rowData" : {
         "Age" : 45,
         "Gender" : "F",
         "Premium" : 2000
      }
   } ],
   "totalRows" : 1
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String | The error message in case of failure. | Small, 53.0 | 53.0 |
| `rows` | [Decision Matrix Row Output](./connect_responses_decision_matrix_row_output.htm.md)[] | The list of rows in a decision matrix version. | Small, 53.0 | 53.0 |
| `totalRows` | Integer | The total count of rows retrieved. | Small, 53.0 | 53.0 |
