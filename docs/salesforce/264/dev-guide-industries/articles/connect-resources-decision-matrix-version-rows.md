---
page_id: connect-resources-decision-matrix-version-rows
title: Decision Matrix Version Rows
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decision-matrix-version-rows.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Omnistudio
parent_page: omnistudio-apis-resources-1
legacy_page_id: connect_resources_decision_matrix_version_rows.htm
fetched_at: 2026-11-25
---

# Decision Matrix Version Rows

Retrieve a paginated list of or manage rows in a decision matrix version. Use this resource to add new rows, or update or delete existing rows in a decision matrix version.

## Resource

```
/connect/omnistudio/decision-matrices/${matrixId}/versions/${versionId}/rows
```

## Example

```
/services/data/v53.0/connect/omnistudio/decision-matrices/0lIR000000000u0MAA
/versions/0lNR000000000rFMAQ/rows
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
| `versionId` | String | The ID of the decision matrix version record. | Required | 53.0 |

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `file` | Boolean | Indicates whether to get the rows by generating a CSV file for downloading (`true`) or fetching the rows in JSON format (`false`). The default value is `false`. | Optional | 53.0 |

## Response Body for GET

[Decision Matrix Rows Output](./connect-responses-decision-matrix-rows-output.md)

## Request Body for POST

### JSON Example

Add a row:

```
{
  "rows": [
    {
      "rowData": {
        "Age": "45",
        "Gender": "F",
        "Premium": "2000"
      }
    }
  ]
}
```

Delete a row:

```
{
  "rows": [
    {
      "id": "a1j5w000006D04uAAC",
      "action": "delete",
      "rowData": {
        "Age": "45",
        "Gender": "F",
        "Premium": "2000"
      }
    }
  ]
}
```

Update a row:

```
{
  "rows": [
    {
      "id": "a1j5w000006D04uAAC",
      "action": "update",
      "rowData": {
        "Age": "45",
        "Gender": "F",
        "Premium": "1500"
      }
    }
  ]
}
```

Add row using a CSV file:

```
{
   "fileId" : "f1j5w000005D04uFGC"
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fileId` | String | The ID of the [Content Document Version](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_contentversion.htm) that contains the rows details to be added or updated in a decision matrix version. | Optional Note: This field is required if you’re using a CVS file to add or update rows. | 53.0 |
| `rows` | [Decision Matrix Row Input](./connect-requests-decision-matrix-row-input.md)[] | List of rows to be added, updated, or deleted in a decision matrix version. | Required | 53.0 |

## Response Body for POST

[Decision Matrix Output](./connect-responses-decision-matrix-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-decision-matrix-version-rows.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
