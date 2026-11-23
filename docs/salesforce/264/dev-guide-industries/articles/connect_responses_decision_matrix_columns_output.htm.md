---
page_id: connect_responses_decision_matrix_columns_output.htm
title: Decision Matrix Columns Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_columns_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-11-23
---

# Decision Matrix Columns Output

Output representation of columns of a decision
matrix.

## JSON Example

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

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `columns` | [Decision Matrix Column Output](./connect_responses_decision_matrix_column_output.htm.md "Representation of the details of a column in a decision matrix.")[] | The list of columns in a decision matrix. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_columns_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
