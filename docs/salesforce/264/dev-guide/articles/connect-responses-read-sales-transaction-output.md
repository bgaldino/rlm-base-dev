---
page_id: connect-responses-read-sales-transaction-output
title: Read Sales Transaction
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-read-sales-transaction-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-responses
legacy_page_id: connect_responses_read_sales_transaction_output.htm
fetched_at: 2026-11-25
---

# Read Sales Transaction

Output representation of the request to read a sales transaction.

## JSON Examples

```
{
  "response": {
    "isSuccess": true,
    "batchMetadata": {
      "parentContextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
      "totalBatches": 3,
      "batchId": "b1f2c3d4-5678-90ab-cdef-1234567890ab"
    },
    "batches": [
      {
        "batchIndex": 0,
        "batchRecords": {
          "records": {
            "Quote": [
              {
                "data": {
                  "Id": "0Q0d2700000AbCdEAAV",
                  "Name": "Q-00001",
                  "Status": "Draft",
                  "GrandTotalAmount": 1500.00,
                  "hasDeletedLines": true
                }
              }
            ],
            "QuoteLineItem": [
              {
                "data": {
                  "Id": "0QLd2700000XyZaBAAX",
                  "Quantity": 2,
                  "Product2Id": "01td2700000PqRsTAAV"
                }
              },
              {
                "data": {
                  "Id": "0QLd2700000XyZaCAAX",
                  "Quantity": 5,
                  "Product2Id": "01td2700000PqRsUAAV"
                }
              }
            ]
          }
        }
      },
      {
        "batchIndex": 1,
        "batchRecords": {
          "records": {
            "QuoteLineItem": [
              {
                "data": {
                  "Id": "0QLd2700000XyZaDAAX",
                  "Quantity": 1,
                  "Product2Id": "01td2700000PqRsVAAV"
                }
              }
            ]
          }
        }
      }
    ]
  }
}
```

```
{
  "isSuccess": false,
  "errors": [
    {
      "errorCode": "INVALID_API_INPUT",
      "message": "Specify either queryTags or sObjectEntitiesToFields in the request."
    }
  ]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `batches` | [Batch Records](./connect-responses-batch-records-output.md)[] | List of the requested batches and their records. The API returns this property when you fetch specific batches by using the `batchIndices` property. | Small, 68.0 | 68.0 |
| `batchMetadata` | [Batch Metadata](./connect-responses-batch-metadata-output.md) | Metadata that describes the available batches for the context, such as the total number of batches. The API returns this property when you request only the batch metadata or when you fetch specific batches. | Small, 68.0 | 68.0 |
| `errors` | [Place Sales Transaction Error Response](./connect-responses-place-sales-transaction-error-response.md)[] | List of errors encountered during the processing of the API request. | Small, 65.0 | 65.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 65.0 | 65.0 |
| `response` | [Read Sales Transaction Records](./connect-responses-read-sales-transaction-records-output.md)[] | Contains a map of keys and associated values. The keys are record type names, such as a Quote or QuoteLineItem, and values are lists of records of that type. | Small, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-read-sales-transaction-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
