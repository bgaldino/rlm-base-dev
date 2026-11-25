---
page_id: connect-requests-object-with-reference-input
title: Object with Reference Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-object-with-reference-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_object_with_reference_input.htm
fetched_at: 2026-11-25
---

# Object with Reference Input

Input representation of a list of records to be inserted or updated. To update a record, specify the record ID.

This is a sample request to create a sales transaction for an order line item.

## JSON Example

```
{
  "referenceId": "refOrderItem0",
  "record": {
    "attributes": {
      "type": "OrderItem",
      "method": "POST"
    },
    "OrderId": "@{refOrder.id}",
    "OrderActionId": "@{refOrderAction.id}",
    "PricebookEntryId": "01uRM000000igZG",
    "Quantity": 2
  }
}
```

This is a sample request to update an order line item.

## JSON Example

```
{
  "referenceId": "refOrderItem0",
  "record": {
    "attributes": {
      "type": "OrderItem",
      "method": "PATCH",
      "id": "402xx000003KY5vJGH"
    },
    "OrderId": "@{refOrder.id}",
    "OrderActionId": "@{refOrderAction.id}",
    "PricebookEntryId": "01uRM000000igZG",
    "Quantity": 2,
    "UnitPrice": 800
  }
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceId` | String | Reference ID that maps to the response and can be used as a reference in later subrecords. This property value starts with a letter or number only and can contain letters, numbers, and underscores. It’s also case-sensitive when used for referencing. | Required | 60.0 |
| `records` | [Object Input Map](./connect-requests-object-input-representation-map.md) | Details of a record to be ingested. | Required | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-object-with-reference-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
