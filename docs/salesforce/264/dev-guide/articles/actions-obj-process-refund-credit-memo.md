---
page_id: actions-obj-process-refund-credit-memo
title: Process Refund Credit Memo Action
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-process-refund-credit-memo.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-invocable-actions-parent
legacy_page_id: actions_obj_process_refund_credit_memo.htm
fetched_at: 2026-11-25
---

# Process Refund Credit Memo Action

Initiates a refund against a posted credit memo. This action locks the credit memo, calls the Commerce Refund API, and returns the refund and application record IDs.

This action is available in API version 68.0 and later.

## Special Access Rules

The Process Refund Credit Memo action is available in Enterprise, Unlimited, and Developer Editions where Billing is enabled. To use this action, your org needs the Payment Run Advance permission.

## Supported REST HTTP Methods

**URI:**`/services/data/v68.0/actions/standard/processUnreferencedRefund`

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:**`Authorization: Bearer TOKEN`

Where TOKEN is a placeholder for your OAuth access token.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `appliedToId` | reference | Required. ID of the posted credit memo to refund against. |
| `currencyIsoCode` | string | Optional. ISO currency code for the refund. Required when multi-currency is enabled. The value must match the currency of the credit memo. |
| `refundNotes` | string | Optional. Notes stored in the refund record comments. |
| `paymentMethodId` | reference | Optional. ID of the payment method to issue the refund on. The payment method must be valid and active. |
| `refundAmount` | double | Required. Amount to refund. The value must be greater than 0 and less than or equal to the remaining balance of the credit memo. |
| `refundReason` | string | Optional. Reason for the refund. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `processRefundResponse` | Apex-defined (`ProcessRefundCreditMemoResponse`) | Result of the refund operation. Contains these fields `success` (boolean)—Indicates whether the refund was processed successfully ( `true` ) or not ( `false` ); `refundId` (string)—ID of the created refund record; `applicationId` (string)—ID of the created application junction record (`CreditMemoRefund` or `CreditMemoLineRefund` ) that links the refund to the credit memo; or `errors` (list of Apex-defined `ProcessRefundCreditMemoErrorResponse` )—List of errors returned if the refund wasn’t processed successfully. Each error contains an `errorCode` and a `message`. Possible error codes are `INVALID_CREDIT_MEMO`—The specified credit memo isn’t in a valid state for refund processing, `AMOUNT_EXCEEDS_BALANCE`—The refund amount exceeds the remaining balance on the credit memo, `CREDIT_MEMO_LOCKED`—The credit memo is locked by another operation, `LIMIT_EXCEEDED`—The number of requests exceeds the maximum allowed (50), `MISSING_REQUIRED_FIELD`—A required input parameter is missing, or `EXTERNAL_SERVICE_EXCEPTION`—The Commerce Refund API call failed without a more specific error. |

## Example

**POST**

This sample request is for the Process Refund Credit Memo action.

```
{
  "inputs": [
    {
      "appliedToId": "0PMxx0000000001AAA",
      "refundAmount": 100,
      "currencyIsoCode": "USD",
      "refundReason": "Customer requested refund",
      "paymentMethodId": "08pxx0000000001AAA",
      "refundNotes": "Refund processed per case 00298475."
    }
  ]
}
```

This sample response shows a successful invocation.

```
[
  {
    "actionName": "processUnreferencedRefund",
    "errors": null,
    "invocationId": null,
    "isSuccess": true,
    "outcome": null,
    "outputValues": {
      "processRefundResponse": {
        "success": true,
        "refundId": "0Rfxx0000000001AAA",
        "applicationId": "0CMxx0000000001AAA",
        "errors": []
      }
    },
    "sortOrder": -1,
    "version": 1
  }
]
```

This sample shows an error response for a credit memo already locked by another operation.

```
[
  {
    "actionName": "processUnreferencedRefund",
    "errors": [
      {
        "statusCode": "CREDIT_MEMO_LOCKED",
        "message": "The Credit Memo is currently locked by another operation. Please try again.",
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/actions-obj-process-refund-credit-memo.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
