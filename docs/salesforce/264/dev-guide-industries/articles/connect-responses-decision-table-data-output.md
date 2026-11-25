---
page_id: connect-responses-decision-table-data-output
title: Decision Table Data
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-data-output.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-table-apis-responses
legacy_page_id: connect_responses_decision_table_data_output.htm
fetched_at: 2026-11-25
---

# Decision Table Data

Output representation of the status of an action performed.

**Sample Output**

: 

```
{
  "errors": [],
  "errorFileId": "string_value"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​FileId` | String | Error code if transaction failed for any reason. | Small, 62.0 | 62.0 |
| `errors` | String[] | List of error messages if transaction failed for any reason. | Small, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-responses-decision-table-data-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
