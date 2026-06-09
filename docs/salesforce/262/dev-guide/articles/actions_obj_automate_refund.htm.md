---
page_id: actions_obj_automate_refund.htm
title: Automate Refund Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_automate_refund.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Automate Refund Action

Initiate refund orchestration for a credit memo
generated from a subscription cancellation or negative amendment.

When you cancel a subscription or make a change that lowers the price (a negative
amendment), a credit memo is generated. A credit memo is a record that represents
the amount to be returned. Use this action to process the refund for that credit
memo.

During an invoice batch run, Revenue Cloud Billing uses these two org preferences to
run the refund orchestration.

- Conversion of negative invoice lines to credit memo and credit memo
  lines—When turned on, this org preference creates a credit memo from the
  negative invoice lines of a cancellation or a negative amendment, and then emits
  a credit memo event.
- Issue refunds and settle balances — Listens to the credit memo event and starts
  the refund orchestration for the converted credit memo.

Turn off these org preferences to call this action directly and choose which credit
memo receives a refund.

In both modes, the orchestration runs these steps in order.

- Remove payments from the original invoice. Partial removal isn’t supported, so
  each selected payment is removed in full. For example, if an invoice has two
  payments P1 ($20) and P2 ($15) and the refund amount is $30, the orchestration
  removes both P1 and P2 in full for a total of $35.
- Apply back any extra amount to the invoice. In the example above, $35 was
  removed but only $30 is needed for the refund. The orchestration applies the
  extra $5 from P2 back to the original invoice.
- Apply the credit memo to the original invoice to record the credit.
- Send a refund request to the payment gateway. The payment gateway is the service
  that processes the customer's payment method. For example, a credit card
  processor. In the example above, the orchestration sends two separate refund
  requests, one for P1 ($20) and one for P2 ($10, the portion not applied
  back).
- Record each refund against its original payment.

The orchestration selects the fewest payments to unapply so that the total unapplied
amount is at least equal to the refund amount.

This action is available in API version 67.0 and later.

For
more information about automated refunds in Subscription Management, see [Automate a refund
(Subscription Management reference)](https://developer.salesforce.com/docs/revenue/subscription-management/references/payments?meta=Automate%2Ba%2Brefund "HTML (New Window)").

## Special Access Rules

The Automate Refund action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/automateRefund`

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
| credit​MemoId | Type  ID  Description  Required. ID of the credit memo to generate a refund. |
| invoiceId | Type  ID  Description  ID of the invoice that the credit memo converts from. This ID matches the value in the Reference Entity field of the credit memo object. When you omit this input, the action reads the invoice ID from the Reference Entity field. When you provide this input, the value must match the Reference Entity field. If the values don’t match, the action returns a validation error.. |

## Outputs

| Output | Details |
| --- | --- |
| status​Url | Type  string  Description  URL to poll for the `RefundAsyncOperation` status. Use this URL to access the tracking record for the credit memo and check the current orchestration run status. |

## Example

POST
:   This sample request is for the Automate Refund action.

    ```
    {
      "inputs": [
        {
          "creditMemoId": "3ttxx0000000001AAA",
          "invoiceId": "3ttxx0000000002BBB"
        }
      ]
    }
    ```
:   This sample response shows a successful invocation with a status URL.

    ```
    [
      {
        "actionName": "automateRefund",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "statusUrl": "/services/data/v67.0/async-operations/00Dxx0000000000EAA/status"
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
:   This sample shows an error response for an invalid credit memo ID.

    ```
    [
      {
        "actionName": "automateRefund",
        "errors": [
          {
            "statusCode": "INVALID_INPUT",
            "message": "The value \"INVALID\" for the creditMemoId parameter is invalid.",
            "fields": []
          }
        ],
        "invocationId": null,
        "isSuccess": false,
        "outcome": null,
        "outputValues": null,
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
