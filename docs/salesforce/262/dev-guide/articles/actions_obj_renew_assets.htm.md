---
page_id: actions_obj_renew_assets.htm
title: Initiate Renewal Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_renew_assets.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Initiate Renewal Action

Initiate and execute the renewal of an asset.

Specify the IDs of the assets that you want to add to renew by specifying a start date. You can
also specify the type of renewal record that you want to create, such as a quote or
an order.

This action is available in API version 60.0 and
later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/initiateRenewal`

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
| rampOptionsDetails | Type  Apex-defined  Description  An Apex RampOptionInputRepresentation record that contains the details of ramp options. The details include segment type, duration, and segment count. Specify this property if you want to include assets in a group ramp with a ramp schedule.  See [RampOptionInputRepresentation](./apex_connectapi_input_ramp_option.htm.md "Input representation of the ramp option details during an asset renewal.") to refer to the associated properties for ramp options. Available in API version 67.0 and later. |
| renewAssetIds | Type  string  Description  Required.  The IDs of the assets that you want to renew. |
| renewContractId | Type  string  Description  ID of the contract record to sync with the renewal quote. |
| renewEndDate | Type  datetime  Description  Effective end date of the renewal. Available in API version 62.0 and later. |
| renewOpportunityId | Type  string  Description  ID of the Opportunity record to sync with the renewal quote. |
| renewOutputType | Type  string  Description  Required.  Type of renewal record to create such as a quote or an order. |
| renewStartDate | Type  datetime  Description  Optional  Effective start date of the renewal. Required for early asset renewals and renewing expired assets, by using today’s date or a future date. Available in API version 62.0 and later. |
| skipPricing | Type  boolean  Description  Indicates whether the pricing procedure must be skipped (`true`) or performed (`false`). Available in API version 64.0 and later. |

## Outputs

| Output | Details |
| --- | --- |
| renewRecordId | Type  string  Description  The ID of the amendment record that’s created. |
| requestIdentifier | Type  string  Description  Request ID that’s used to track the async request. |

## Example

POST
:   This sample request is for the Initiate Renewal action.

    ```
    {
      "inputs": [
        {
          "rampOptionsDetails": {
            "segmentType": "Custom",
            "duration": 40,
            "numberOfSegments": 10
          },
          "renewAssetIds": [
            "02ixx0000004LMwAAM"
          ],
          "renewOutputType": "Quote",
          "renewContractId": "800DU0000000lZlYAI",
          "renewOpportunityId": "006DU0000025AanYAE",
          "renewStartDate": "2023-10-21T00:00:00.000Z",
          "renewEndDate": "2024-10-21T00:00:00.000Z",
          "skipPricing": false
        }
      ]
    }
    ```

    This sample response is for the Initiate Renewal action.

    ```
    [
        {
            "actionName": "initiateRenewal",
            "errors": null,
            "isSuccess": true,
            "outputValues": {
                "renewRecordId": "0Q0xx0000004P32CAE",
                "requestIdentifier": "16Pxx0000004OTY"
            },
            "version": 1
        }
    ]
    ```
