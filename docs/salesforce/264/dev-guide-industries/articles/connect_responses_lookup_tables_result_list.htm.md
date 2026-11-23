---
page_id: connect_responses_lookup_tables_result_list.htm
title: Lookup Tables Result List
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_lookup_tables_result_list.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: lookup_tables_responses.htm
fetched_at: 2026-11-23
---

# Lookup Tables Result List

Output representation of the result of a lookup table search
request.

## JSON Example

```
{
  "code": "200",
  "isSuccess": true,
  "lookupTables": [
    {
      "id": "0lIxx000000003FEAQ",
      "lookupTableDefinitionId": "0lDxx000000001dEAA",
      "lookupTableType": "DecisionTable",
      "name": "DT_Apr27_2",
      "apiName": "DT_Apr27_2"
    }
  ],
  "message": ""
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Response code of the API request. | Small, 59.0 | 59.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful (`true`) or not (`false`). | Small, 59.0 | 59.0 |
| `lookupTables` | [Lookup Table Details](./connect_responses_lookup_table_details.htm.md "Output representation of the basic details of a lookup table.")[] | List of the retrieved lookup tables. | Small, 59.0 | 59.0 |
| `message` | String | API response message if the request fails. | Small, 59.0 | 59.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_lookup_tables_result_list.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
