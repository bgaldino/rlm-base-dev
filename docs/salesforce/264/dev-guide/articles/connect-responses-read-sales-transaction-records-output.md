---
page_id: connect-responses-read-sales-transaction-records-output
title: Read Sales Transaction Records
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-read-sales-transaction-records-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_read_sales_transaction_records_output.htm
fetched_at: 2026-11-25
---

# Read Sales Transaction Records

Output representation of the details of a map of keys and associated values. The keys are record type names, such as a Quote or QuoteLineItem, and values are lists of records of that type.

## JSON Example

```
{
  "response": {
    "records": {
      "Quote": [
        {
          "data": {
            "Id": "0Q05g000000AJK954",
            "Name": "Sample Quote",
            "Status": "Draft",
            "TotalPrice": 1500
          }
        }
      ],
      "QuoteLineItem": [
        {
          "data": {
            "Id": "0QL5g000000DEF456",
            "Product2Id": "01t5g000000GUE752",
            "Quantity": 2,
            "UnitPrice": 750,
            "TotalPrice": 1500
          }
        }
      ]
    }
  },
  "isSuccess": true,
  "errorResponse": []
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `records` | Map<String, [Sales Transaction Record](./connect-responses-sales-transaction-record-output.md)>> | Map of record type names to the list of records. | Small, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-read-sales-transaction-records-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
