---
page_id: connect_responses_decision_table_rows_list_output.htm
title: Decision Table Rows List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_table_rows_list_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Table Rows List

Output representation of the rows in relation to the decision table, including current
    state of pagination.

        
          

**Sample Output**

          
: 
            

```
{
  "rows": [
    {
      "id": "1FIxx0000004CCG",
      "rowData": {
        "AssetLevel": "101",
        "City": "city1"
      }
    }
  ],
  "totalRows": 3
}
```

          

        
      

          
          
          
          
          
          
            
              

              

              

              

              

            

          

          
            
              

              

              

              

              

            

            
              

              

              

              

              

            

          

        
| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `rows` | [Decision Table Row](./connect_responses_decision_table_row_output.htm.md)[] | List of rows returned in response to the API request. | Small, 62.0 | 62.0 |
| `totalRows` | Integer | Total number of rows. | Small, 62.0 | 62.0 |
