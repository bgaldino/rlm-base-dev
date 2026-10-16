---
page_id: connect_responses_decision_matrix_columns_output.htm
title: Decision Matrix Columns Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_columns_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Columns Output

Output representation of columns of a decision
    matrix.

      
        
          

**JSON example**

          
: 
            

```
{
   "columns" : [ {
      "apiName" : “Age”,
      "columnType" : "Input",
      "dataType" : "Number",
      "displaySequence" : 1,
      "id" : "0lJR0000000014aMAA",
      "name" : “Age”,
      "rangeValues" : null
   }, {
      "apiName" : “Gender”,
      "columnType" : "Input",
      "dataType" : "Text",
      "displaySequence" : 2,
      "id" : "0lJR0000000014bMAA",
      "name" : “Gender”,
      "rangeValues" : null
   }, {
      "apiName" : “Premium”,
      "columnType" : "Output",
      "dataType" : "Number",
      "displaySequence" : 3,
      "id" : "0lJR0000000014fMAA",
      "name" : "Premium",
      "rangeValues" : null
   } ]
}
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `columns` | [Decision Matrix Column Output](./connect_responses_decision_matrix_column_output.htm.md)[] | The list of columns in a decision matrix. | Small, 53.0 | 53.0 |
