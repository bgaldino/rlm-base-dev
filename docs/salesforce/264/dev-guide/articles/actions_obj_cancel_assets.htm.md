---
page_id: actions_obj_cancel_assets.htm
title: Initiate Cancellation Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_cancel_assets.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-11-23
---

# Initiate Cancellation Action

Initiate and execute the cancellation of an asset.

Specify the IDs of the assets that you want to add to cancel by specifying a start date. You can also specify the type of cancellation record that you want to create, such as a quote or an order.

This action is available in API version 60.0 and later.

## Supported REST HTTP Methods

**URI:** `/services/data/v68.0/actions/standard/initiateCancellation`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer token`

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| cancelAssetIds | string | Required. The IDs of the assets that you want to cancel. All assets in a request must belong to the same price book. |
| cancelContractId | string | The ID of the contract record to sync with the cancellation. |
| cancelOpportunityId | string | The ID of the Opportunity record to sync with the cancellation quote. |
| cancelOutputType | string | Required. Type of cancellation record to create such as a quote or an order. |
| cancelStartDate | datetime | Required. Effective date of the cancellation. |
| skipPricing | boolean | Indicates whether the pricing procedure must be skipped (`true`) or performed (`false`). Available in API version 64.0 and later. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| cancelRecordId | string | The ID of the cancellation record that’s created. |
| requestIdentifier | string | Request ID that’s used to track the async request. |

## Example

**POST**

This sample request is for the Initiate Cancellation action.

```
{
    "inputs": [
        {
            "cancelAssetIds": [
                "02iI8000000Lc5fIAC"
            ],
            "cancelStartDate": "2023-11-09T00:00:00",
            "cancelOutputType": "Quote",
            "cancelContractId": "800DU0000000lZlYAI",
            "cancelOpportunityId": "006DU0000025AanYAE",
            "skipPricing": false
        }
    ]
}
```

This sample response is for the Initiate Cancellation action.

```
[
    {
        "actionName": "initiateCancellation",
        "errors": null,
        "isSuccess": true,
        "outputValues": {
            "record_id": "0Q0xx0000004P32CAE",
            "requestIdentifier": "16Pxx0000004OTY"
        },
        "version": 1
    }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_cancel_assets.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
