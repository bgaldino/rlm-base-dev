---
page_id: actions-obj-amend-assets
title: Initiate Amendment Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-amend-assets.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Transaction Management
parent_page: qoc-invocable-actions-parent
legacy_page_id: actions_obj_amend_assets.htm
fetched_at: 2026-11-25
---

# Initiate Amendment Action

Initiate and execute the amendment of an asset.

Specify the IDs of assets to amend, the amendment start date, and any quantity changes. You can choose whether the action creates an amendment quote or order.

## Considerations

For usage products, creating an order directly by setting `amendOutputType` to `Order` is currently not supported. The direct-to-order flow can create Order Products without required related Rate Card Entry records, which can cause order activation to fail.

When you amend usage assets, use a two-step flow.

1. Create an amendment quote by calling `initiateAmendment` with `amendOutputType` set to `Quote`.

2. Create an order from that amendment quote.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/initiateAmendment`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `amendAssetIds` | string | Required. The IDs of the assets that you want to amend. |
| `amendContractId` | string | The ID of the contract record to be synced with the amendment. |
| `amendStartDate` | datetime | Required. Effective start date of the amendment. |
| `amendOpportunityId` | string | The ID of the Opportunity record to be synced with the amendment quote. |
| `amendOutputType` | string | Required. Type of amendment record to create such as a quote or an order. For usage products, set this value to `Quote`. The usage-related records (`QuoteLineItemUseResourceGrant`, `QuoteLineItemUsageResourcePolicy`, and `QuoteLineRateCardEntry`) are copied in the quote action flow, not in the amend order flow. |
| `quantityChange` | double | Required. Quantity to add to or reduce from the asset’s existing quantity. |
| `skipPricing` | boolean | Indicates whether the pricing procedure must be skipped (`true`) or performed (`false`). Available in API version 64.0 and later. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `amendRecordId` | string | The ID of the amendment record that’s created. |
| `requestIdentifier` | string | Request ID that’s used to track the async request. |

## Example

**POST**

This sample request is for the Initiate Amendment action.

```
{
    "inputs": [
        {
            "amendAssetIds": ["02iI8000000HPzXIAW"],
            "amendStartDate": "2023-10-21T00:00:00.000Z",
            "quantityChange": 5,
            "amendOutputType": "Quote",
            "amendContractId": "800DU0000000lZlYAI",
            "amendOpportunityId": "006DU0000025AanYAE",
            "skipPricing": false
        }
    ]
}
```

This sample response is for the Initiate Amendment action.

```
[
    {
        "actionName": "initiateAmendment",
        "errors": null,
        "isSuccess": true,
        "outputValues": {
            "record_id": "0Q0xx0000004NsSCAU",
            "requestIdentifier": "16Pxx0000004NIy"
        },
        "version": 1
    }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-amend-assets.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
