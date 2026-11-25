---
page_id: connect-requests-sales-transaction-filter-condition-input
title: Sales Transaction Filter Condition Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-sales-transaction-filter-condition-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_sales_transaction_filter_condition_input.htm
fetched_at: 2026-11-25
---

# Sales Transaction Filter Condition Input

Input representation of filter conditions used to query sales transaction context data.

## JSON Example

```
{
  "filters": [
    {
      "sObjectName": "Quote",
      "fieldName": "Status",
      "operator": "Equals",
      "operands": [
        {
          "value": "Draft",
          "type": "STRING"
        }
      ]
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `sObjectName` | String | Name of the sObject that contains the field to filter on. | Required if the `fieldName` property value isn’t specified. Or, specify the `nodeName` and `attributeName` property values. | 67.0 |
| `fieldName` | String | Name of the field on the specified sObject to filter on. | Required if the `sObjectName` property value isn’t specified. Or, specify the `nodeName` and `attributeName` property values. | 67.0 |
| `operator` | String | Operator to use to filter the results. Valid values are `Equals`, `NotEquals`, `Gt`—Greater Than, `GtEq`—Greater Than or Equals, `Lt`—Less Than, `LtEq`—Less Than or Equals, or `In`. | Required | 67.0 |
| `nodeName` | String | Name of the context node to apply filtering on. | Optional | 67.0 |
| `attributeName` | String | Name of the node attribute to apply filtering on. | Optional | 67.0 |
| `operands` | [Sales Transaction Operand](./connect-requests-sales-transaction-operand-input.md#properties)[] | Operand values with explicit value and type metadata. | Required | 67.0 |
| `underlyingFilters` | [Sales Transaction Filter Condition](#properties)[] | Nested filter conditions used to compose a composite filter. | Optional | 67.0 |
| `operatorLogic` | String | Logical expression that defines how underlying filters are combined. Valid values are `AND` or `OR`. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-sales-transaction-filter-condition-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
