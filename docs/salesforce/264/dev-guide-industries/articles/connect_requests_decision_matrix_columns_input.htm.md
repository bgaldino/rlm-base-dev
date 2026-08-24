---
page_id: connect_requests_decision_matrix_columns_input.htm
title: Decision Matrix Columns Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_columns_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests_1.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Decision Matrix Columns Input

Input representation of the information to manage columns in relation
      to a decision matrix.

**JSON example**

: 
            

Add a column:

            

```
{
   "columns" : [ {
      "apiName" : "Name",
      "columnType" : "Input",
      "dataType" : "Text",
      "displaySequence" : 4,
      "name" : "Name"
   }]
}
```

          

          
: 
            

Delete a column:

            

```
{
   "columns" : [ {
      "action" : "delete",
      "id" : "0lJR0000000014bMAA"
   }]
}
```

          

          
: 
            

Update a column:

            

```
{
   "columns" : [ {
      "id" : "0lJR0000000014hMAA",
      "action" : "update",
      "columnType" : "Input",
      "name" : "First Name"
   }]
}
```

          

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `columns` | [Decision Matrix Column Input](./connect_requests_decision_matrix_column.htm.md)[] | List of columns to be added, updated, or deleted in a decision matrix. | Required | 53.0 |
