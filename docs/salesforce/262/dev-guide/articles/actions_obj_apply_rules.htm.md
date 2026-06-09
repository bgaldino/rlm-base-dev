---
page_id: actions_obj_apply_rules.htm
title: Apply Payments and Credits by Rules Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_apply_rules.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Apply Payments and Credits by Rules Action

Apply payments and credits to posted invoices by adhering to the specified
rules.

This action uses predefined logic to allocate payments and credits, reducing any
manual intervention and errors.

This action is available in API version 66.0
and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/applyPaymentsAndCreditsByRules`

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
| accountId | Type  reference  Description  Required. The ID of the account to perform the settlement of payments and credits against invoices in adherence with the applied rules. |
| targetDate | Type  date  Description  Optional. The date used to select invoices and invoice lines with a posted date equal to or later than the target date to apply payments and credits. |

## Outputs

| Output | Details |
| --- | --- |
| rulesApplicationResponse | Type  Apex-defined  Description  The Apex [RulesApplicationResponse](https://developer.salesforce.com/docs/./apex_class_RulesAppln_RulesApplicationResponse.htm.md "HTML (New Window)") record that contains the results of rules application including the list of applied rules, application details, and any errors. |

## Example

POST
:   Here's a sample request for the Apply Payments and Credits by Rules
    action.

    ```
    {
      "inputs": [
        {
          "accountId": "001AAC0001NmajhYBB",
          "targetDate": "2025-08-27"
        }
      ]
    }
    ```
:   Here's a sample success response for the Apply Payments and Credits by
    Rules action.

    ```
    [
      {
        "actionName": "applyPaymentsAndCreditsByRules",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "rulesApplicationResponse": {
            "rulesApplicationSummary": {
              "totalPaymentApplications": 1,
              "totalCreditMemoApplications": 1,
              "fetchedPaymentsCount": 1,
              "fetchedCreditMemosCount": 1,
              "areAllInvoicesConsidered": true
            },
            "isSuccess": true,
            "errors": null,
            "appliedRules": [
              "Match Balance",
              "Prioritize Highest Balance Invoices"
            ]
          }
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
:   Here's a sample error response for the Apply Payments and Credits by
    Rules action.

    ```
    [
      {
        "actionName": "applyPaymentsAndCreditsByRules",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "rulesApplicationResponse": {
            "rulesApplicationSummary": null,
            "isSuccess": false,
            "errors": [
              {
                "message": "We couldn't find eligible invoices to apply rules-based credits and payments. ",
                "errorCode": null
              }
            ],
            "appliedRules": null
          }
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
