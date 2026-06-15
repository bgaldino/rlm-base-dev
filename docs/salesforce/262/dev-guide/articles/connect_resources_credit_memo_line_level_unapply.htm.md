---
page_id: connect_resources_credit_memo_line_level_unapply.htm
title: Unapply Credit Memo Line (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_credit_memo_line_level_unapply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Unapply Credit Memo Line (POST)

Unapply a credit memo line from an invoice line and return the invoice
line and the credit memo line to their pre-application states.

Special Access Rules
:   You need the Credit Memo Operations User permission set to use this API.

Resource
:   ```
    /commerce/invoicing/credit-memo-line-invoice-line/creditMemoLineInvoiceLineId/actions/unapply
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/credit-memo-line-invoice-line/4sGSG0000002kQ92AI/actions/unapply
    ```

Available version
:   62.0

HTTP methods
:   POST

Path parameter for POST
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `creditMemo​LineInvoice​LineId` | String | ID of the credit memo line invoice line record. | Required | 62.0 |

Request body for POST
:   JSON example
    :   ```
        {
         "description": "Unapply a credit memo line from invoice line 1",
         "effectiveDate": "2024-07-01"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `description` | String | Explanation or reason for unapplying the credit memo line. | Optional | 62.0 |
        | `effectiveDate` | String | Effective date for the credit memo line. | Optional | 62.0 |

Response body for POST
:   [Credit Memo Line
    Unapplied](./connect_responses_credit_memo_line_unapplied.htm.md "Output representation of the details of the credit memo line invoice line record with the status of the request.")
