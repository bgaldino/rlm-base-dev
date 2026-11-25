---
page_id: connect-resources-decision-matrix-columns
title: Decision Matrix Columns
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decision-matrix-columns.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-resources-1
legacy_page_id: connect_resources_decision_matrix_columns.htm
fetched_at: 2026-11-25
---

# Decision Matrix Columns

Retrieve a list of or manage columns in a decision matrix. Use this resource to add new columns, or update or delete existing columns in a decision matrix.

## Resource

```
/connect/omnistudio/decision-matrices/${matrixId}/columns
```

## Example

```
/services/data/v53.0/connect/omnistudio/decision-matrices/0lIR000000000u0MAA/columns
```

## Available Version

53.0

## Requires Chatter

No

## HTTP Methods

GET, POST

## Path parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `matrixId` | String | The ID of the decision matrix record. | Required | 53.0 |

## Response Body for GET

[Decision Matrix Columns Output](./connect-responses-decision-matrix-columns-output.md)

## Request Body for POST

### JSON Example

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

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `columns` | [Decision Matrix Column Input](./connect-requests-decision-matrix-column.md)[] | List of columns to be added, updated, or deleted in a decision matrix. | Required | 53.0 |

## Response Body for POST

[Decision Matrix Output](./connect-responses-decision-matrix-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decision-matrix-columns.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
