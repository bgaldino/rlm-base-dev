---
page_id: connect_requests_read_sales_transaction_input.htm
title: Read Sales Transaction Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_read_sales_transaction_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-11-23
---

# Read Sales Transaction Input

Input representation of the filter criteria details to read a sales transaction.

## JSON Examples

```
{
  "contextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
  "batchIndices": [
    0,
    1
  ],
  "sobjectFieldMap": {
    "Quote": [],
    "QuoteLineItem": [
      "Quantity",
      "Product2Id"
    ]
  },
  "filters": [
    {
      "sobjectName": "Quote",
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

```
{
  "contextId": "0RSxx0000004C92GAE",
  "queryTags": [
    "QuoteLineItem"
  ],
  "filters": [
    {
      "nodeName": "SalesTransactionItem",
      "attributeName": "DmlStatus",
      "operator": "In",
      "operands": [
        {
          "value": "Inserted",
          "type": "STRING"
        },
        {
          "value": "Updated",
          "type": "STRING"
        }
      ]
    }
  ]
}
```

```
{
  "contextId": "0RSxx0000004C92GAE",
  "shouldReturnMetadataOnly": true
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `batchIndices` | List<Integer> | List of batch indices to fetch. The indices are zero-based. If you include this property, the API returns only the specified batches. This property supports fetching multiple batches in parallel. | Optional | 68.0 |
| `contextId` | String | ID of the context to retrieve the data records. | Required | 65.0 |
| `filters` | List<[Sales Transaction Filter Condition](./connect_requests_sales_transaction_filter_condition_input.htm.md#SalesTransactionFilterConditionInputRepresentation)> | Filter conditions to query the context data. | Optional | 67.0 |
| `queryTags` | List<String> | List of objects that must be retrieved from the context. | Optional | 65.0 |
| `shouldReturnMetadataOnly` | Boolean | Indicates whether to return only batch metadata without fetching batch data (`true`) or not (`false`). | Optional | 68.0 |
| `sobjectFieldMap` | Map<String, List<String>> | Mapping of an sObject name to a list. The list includes the sObject field names on the object or can be an empty list. An empty list specifies that all fields on the object must be queried. | Optional | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_read_sales_transaction_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
