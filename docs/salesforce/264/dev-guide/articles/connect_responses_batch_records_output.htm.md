---
page_id: connect_responses_batch_records_output.htm
title: Batch Records
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_batch_records_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-11-23
---

# Batch Records

Output representation of a single batch and the records that it contains.

## JSON Example

This example response shows a single batch and the records that it contains.

```
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
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `batchIndex` | Integer | Zero-based index of the batch. | Small, 68.0 | 68.0 |
| `batchRecords` | [Read Sales Transaction Records](./connect_responses_read_sales_transaction_records_output.htm.md "Output representation of the details of a map of keys and associated values. The keys are record type names, such as a Quote or QuoteLineItem, and values are lists of records of that type.") | Records that the batch contains. | Small, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_batch_records_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
