---
page_id: actions_obj_blng_svc_suspend_billing.htm
title: Suspend Billing Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_blng_svc_suspend_billing.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Suspend Billing Action

Suspend or resume the billing of an account to handle billing
disputes.

Specify the account ID and a date when billing must be suspended. Optionally, specify
the date when billing must be resumed. The action suspends billing for the account
from the suspension date and, if provided, resumes billing on the resumption
date.

This action is available in API version 66.0 and later.

## Special Access Rules

The Suspend Billing Action is available in Enterprise, Developer, and Unlimited
Editions where Dispute Management is enabled in Billing.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/blngSvcSuspendBilling`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| accountId | Type  string  Description  ID of the account for which billing must be suspended. |
| resumptionDate | Type  date  Description  Date when the billing must be resumed. |
| suspensionDate | Type  date  Description  Date when the billing must be suspended. |

## Outputs

| Output | Details |
| --- | --- |
| additional​Information | Type  string  Description  Any additional information to be included in the response. |
| isSuccess | Type  boolean  Description  Indicates whether the billing related to the specified account was suspended (`true`) or not (`false`). The default value is `false`. |

## Example

POST
:   This sample request is for the Suspend Billing action.

    ```
    {
      "inputs": [
        {
          "accountId": "001xx000003GYexAAG",
          "suspensionDate": "2025-03-01",
          "resumptionDate": "2025-03-15"
        }
      ]
    }
    ```
:   This sample response is for the Suspend Billing action.

    ```
    [
      {
        "actionName": "blngSvcSuspendBilling",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "isSuccess": true,
          "additionalInformation": "{\"status\":\"Billing suspended successfully\"}"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
