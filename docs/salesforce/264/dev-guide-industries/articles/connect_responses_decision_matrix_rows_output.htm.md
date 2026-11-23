---
page_id: connect_responses_decision_matrix_rows_output.htm
title: Decision Matrix Rows Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_rows_output.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses_1.htm
fetched_at: 2026-11-23
---

# Decision Matrix Rows Output

Output representation of rows of a decision matrix
version.

## JSON Example

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

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String | The error message in case of failure. | Small, 53.0 | 53.0 |
| `rows` | [Decision Matrix Row Output](./connect_responses_decision_matrix_row_output.htm.md "Representation of the details of a row in a decision matrix version.")[] | The list of rows in a decision matrix version. | Small, 53.0 | 53.0 |
| `totalRows` | Integer | The total count of rows retrieved. | Small, 53.0 | 53.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_decision_matrix_rows_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
