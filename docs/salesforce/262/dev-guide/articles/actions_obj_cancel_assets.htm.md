---
page_id: actions_obj_cancel_assets.htm
title: Initiate Cancellation Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_cancel_assets.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Initiate Cancellation Action

Initiate and execute the cancellation of an asset.

Specify the IDs of the assets that you want to add to cancel by specifying a start date. You can
also specify the type of cancellation record that you want to create, such as a
quote or an order.

This action is available in API version 60.0 and
later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/initiateCancellation`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| cancelAssetIds | Type  string  Description  Required.  The IDs of the assets that you want to cancel.  All assets in a request must belong to the same price book. |
| cancelContractId | Type  string  Description  The ID of the contract record to sync with the cancellation. |
| cancelOpportunityId | Type  string  Description  The ID of the Opportunity record to sync with the cancellation quote. |
| cancelOutputType | Type  string  Description  Required.  Type of cancellation record to create such as a quote or an order. |
| cancelStartDate | Type  datetime  Description  Required.  Effective date of the cancellation. |
| skipPricing | Type  boolean  Description  Indicates whether the pricing procedure must be skipped (`true`) or performed (`false`). Available in API version 64.0 and later. |

## Outputs

| Output | Details |
| --- | --- |
| cancelRecordId | Type  string  Description  The ID of the cancellation record that’s created. |
| requestIdentifier | Type  string  Description  Request ID that’s used to track the async request. |

## Example

POST
:   This sample request is for the Initiate Cancellation action.

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
