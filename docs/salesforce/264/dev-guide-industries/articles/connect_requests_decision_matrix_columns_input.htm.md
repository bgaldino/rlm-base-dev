---
page_id: connect_requests_decision_matrix_columns_input.htm
title: Decision Matrix Columns Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_columns_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests_1.htm
fetched_at: 2026-11-23
---

# Decision Matrix Columns Input

Input representation of the information to manage columns in relation
to a decision matrix.

## JSON Example

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

Delete a column:

```
{
   "columns" : [ {
      "action" : "delete",
      "id" : "0lJR0000000014bMAA"
   }]
}
```

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

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `columns` | [Decision Matrix Column Input](./connect_requests_decision_matrix_column.htm.md "Input representation of the information required to add, update, or delete columns in a decision matrix.")[] | List of columns to be added, updated, or deleted in a decision matrix. | Required | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_columns_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
