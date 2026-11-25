---
page_id: connect-resources-assets-renew
title: Asset Renewal (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-assets-renew.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-business-apis-rest-references
legacy_page_id: connect_resources_assets_renew.htm
fetched_at: 2026-11-25
---

# Asset Renewal (POST)

Initiate and execute the renewal of an asset.

## Special Access Rules

To use this API, you need the InitiateRenewal API permission set.

## Resource

```
/connect/revenue-management/assets/actions/renew
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/revenue-management/assets/actions/renew
```

## Available Version

62.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "assetIds": [
    "02iSG0000003NMhYAM",
    "02iSG0000006DvSYAU"
  ],
  "contractId": "800SG00000CFpepYAD",
  "opportunityId": "006SG000004W5tVYAS",
  "outputRecordId": "801SG00000DX1jWYAT",
  "outputRecordType": "Quote",
  "renewalEndDate": "2024-10-03T23:59:59",
  "renewalStartDate": "2023-10-04T00:00:00"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `assetIds` | String[] | IDs of the assets that you want to renew. | Required | 62.0 |
| `contractId` | String | ID of the Contract record that you want to sync with the renewal of the Quote or Order record. | Optional | 62.0 |
| `opportunity​Id` | String | ID of the Opportunity record that you want to sync with the renewal quote. | Optional | 62.0 |
| `output​RecordId` | String | ID of the Quote or Order record that you want to renew. | Optional | 62.0 |
| `output​RecordType` | String | Type of renewal record that you want to create. | Required | 62.0 |
| `renewal​EndDate` | String | End date of the renewal process for the assets. | Optional | 62.0 |
| `renewal​StartDate` | String | Start date of the renewal process for the assets. Required for early asset renewals and renewing expired assets, using today’s date or a future date. | Optional | 62.0 |

## Response Body for POST

[Renewal](./connect-responses-renew-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-assets-renew.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
