---
page_id: connect_resources_credit_memo_invoice_application_unapply.htm
title: Unapply Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_invoice_application_unapply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Unapply Credit Memo (POST)

Unapply a credit memo from an invoice and return the invoice and the
credit memo to their pre-application states.

Use this resource if an error occurred when a credit is issued. For example, if an incorrect
credit memo is applied to an invoice, or if a credit memo is created for an incorrect
amount, use this resource to unapply the credit memo.

Special Access Rules
:   You need the Credit Memo Operations User permission set to use this API.

Resource
:   ```
    /commerce/invoicing/credit-memo-inv-applications/creditMemoInvApplicationId/actions/unapply
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/credit-memo-inv-applications/4sFSG000002nxPB2AY/actions/unapply
    ```

Available version
:   62.0

HTTP methods
:   POST

Path parameter for POST
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `creditMemo​InvApplication​Id` | String | ID of the credit memo invoice application. | Required | 62.0 |

Request body for POST
:   JSON example
    :   ```
            {
              "description": "Unapply credit memo from invoice to revert an error",
              "effectiveDate": "2024-07-01"
            }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `description` | String | Explanation or reason for unapplying the credit memo. | Optional | 62.0 |
        | `effectiveDate` | String | Effective date for the credit memo. | Optional | 62.0 |

Response body for POST
:   [Credit Memo
    Unapply](./connect_responses_credit_memo_unapply_output.htm.md "Output representation of the details of the credit memo invoice application record with the status of the request.")
