---
page_id: connect_resources_decision_table_csv_based_dt.htm
title: CSV Based Decision Table (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_table_csv_based_dt.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: decision_table_apis_resources.htm
fetched_at: 2026-11-23
---

# CSV Based Decision Table (GET)

Fetch paginated data from a CSV based decision table. This resource is responsible for
managing rows in a Decision Table.

## Resource

```
/connect/business-rules/decision-table/${decisionTableId}/data
```

## Example for GET

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/business-rules/decision-table/0lDxx0000000001EAA/data?filter=AssetLevel:101
```

## Example for POST

```
https://yourInstance.salesforce.com/services/data/v68.0/connect/business-rules/decision-table/0lDxx0000000001EAA/data
```

## Available Version

62.0

## HTTP Methods

GET POST

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `filter` | String | Filters applied to rows based on column criteria. | Optional | 62.0 |
| `limit` | Integer | Limits the number of records viewed at a time. The default value is `20`. | Optional | 62.0 |
| `offset` | Integer | Token that represents the page offset for pagination. Use this value with the pageSize parameter to indicate where the page starts. The maximum offset is `100` and the default is `0`. | Optional | 62.0 |

## Response Body for GET

[Decision Table Rows List](./connect_responses_decision_table_rows_list_output.htm.md "Output representation of the rows in relation to the decision table, including current state of pagination.")

## Request Body for POST

### JSON Example

```
{
  "rows": [
    {
      "id": "1FIxx0000004CSOGA2",
      "rowData": {
        "City": "City3",
        "AssetLevel": "300"
      },
      "action": "update"
    }
  ]
}
```

### Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `rows` | [Decision Table Row Input](./connect_requests_decision_table_row_list_input.htm.md "Input representation of the data for a row in the CSV based decision table that has to be added or updated.")[] | List of rows to be updated or added. | Required | 62.0 |

## Request Parameters for POST

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `rows​Input` | Object |  |  | 62.0 |

## Response Body for POST

[Decision Table Data](./connect_responses_decision_table_data_output.htm.md "Output representation of the status of an action performed.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_decision_table_csv_based_dt.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
