---
page_id: actions_obj_post_draft_invoice.htm
title: Post Draft Invoice Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_post_draft_invoice.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Post Draft Invoice Action

Update the status of an invoice from `Draft` to `Posted` for a credit memo
application.

This action uses the ID of the draft invoice and triggers an asynchronous process to post the
invoice. This action is available in API version 62.0 and later.

## Special Access Rules

The Post Draft Invoice action is available in Enterprise, Unlimited, and Developer Editions
where Billing is enabled. To use this action, you need the Billing Operations User
permission set.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/postDraftInvoice`

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
| correlationId | Type  string  Description  Splunk correlation ID to track the messages that are related to the request and are logged in Splunk by the different services involved in the request. If the ID isn’t specified, the service creates a random Universally Unique Identifier (UUID). |
| invoiceId | Type  string  Description  Required.  ID of the `Draft` invoice to be posted. |

## Outputs

| Output | Details |
| --- | --- |
| requestIdentifier | Type  string  Description  UUID that’s used to track the status of the asynchronous action. |
| statusUrl | Type  string  Description  URL that’s used to check the status of the API request. |

## Example

POST
:   This example shows a sample request for the Post Draft Invoice
    action.

    ```
    {
      "inputs": [
        {
          "invoiceId": "3ttDU00000000iZYAQ"
        }
      ]
    }
    ```

    This example shows a sample response for the Post Draft Invoice
    action.

    ```
    {
      "actionName": "postDraftInvoice",
      "errors": null,
      "isSuccess": true,
      "outputValues": {
        "requestIdentifier": "4sFDU00000000652AA",
        "statusUrl": "/services/data/v62.0/sobjects/AsyncOperationTracker/16Pxx0000004NhAEAU"
      }
    }
    ```
