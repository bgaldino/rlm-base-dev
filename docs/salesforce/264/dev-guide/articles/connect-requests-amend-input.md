---
page_id: connect-requests-amend-input
title: Amendment Input
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-amend-input.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-api-requests
legacy_page_id: connect_requests_amend_input.htm
fetched_at: 2026-11-25
---

# Amendment Input

Input representation of the details of the request to create an amendment record.

## JSON Example

```
{
  "assetIds": [
    "02iSG0000003NMhYAM",
    "02iSG0000006DvSYAU"
  ],
  "amendmentStartDate": "2023-10-04T00:00:00",
  "contractId": "800SG00000CFpepYAD",
  "opportunityId": "006SG000004W5tVYAS",
  "outputRecordId": "801SG00000DX1jWYAT",
  "outputRecordType": "Quote",
  "quantityChange": 5
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assetIds` | String[] | IDs of the assets that you want to add to the amendment record. | Required | 62.0 |
| `amendmentStart​Date` | String | Start date of the amendment. | Required | 62.0 |
| `contract​Id` | String | ID of the Contract record that you want to sync with the amendment quote. | Optional | 62.0 |
| `opportunity​Id` | String | ID of the Opportunity record that you want to sync with the amendment quote. | Optional | 62.0 |
| `outputRecord​Id` | String | ID of the quote or order record that you want to add the assets to. | Optional | 62.0 |
| `output​RecordType` | String | Type of amendment record that you want to create. For usage products, set this value to `Quote`. The usage-related records (`QuoteLineItemUseResourceGrant`, `QuoteLineItemUsageResourcePolicy`, and `QuoteLineRateCardEntry`) are copied in the quote action flow, not in the amend order flow. | Required | 62.0 |
| `quantity​Change` | Double | Quantity to add to or reduce from the asset’s existing quantity. | Required | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-requests-amend-input.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
