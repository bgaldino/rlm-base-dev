---
page_id: connect_requests_cancel_input.htm
title: Cancellation Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_cancel_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-11-23
---

# Cancellation Input

Input representation of the details of the request to cancel a quote or an order.

## JSON Example

```
{
  "assetIds": [
    "02iSG0000003NMhYAM",
    "02iSG0000006DvSYAU"
  ],
  "cancellationDate": "2023-10-04T00:00:00",
  "contractId": "800SG00000CFpepYAD",
  "opportunityId": "006SG000004W5tVYAS",
  "outputRecordId": "801SG00000DX1jWYAT",
  "outputRecordType": "Quote"
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assetIds` | String[] | IDs of the assets that you want to cancel. All assets in a request must belong to the same price book. | Required | 62.0 |
| `cancellation​Date` | String | Effective date of the cancellation. | Required | 62.0 |
| `contract​Id` | String | ID of the Contract record that you want to sync with the cancellation quote. | Optional | 62.0 |
| `opportunity​Id` | String | ID of the Opportunity record that you want to sync with the cancellation quote. | Optional | 62.0 |
| `output​RecordId` | String | ID of the quote or order that you want to cancel. | Optional | 62.0 |
| `output​RecordType` | String | Type of cancellation record that you want to create. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_cancel_input.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
