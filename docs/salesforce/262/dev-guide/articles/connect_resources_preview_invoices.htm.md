---
page_id: connect_resources_preview_invoices.htm
title: Invoice Preview (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_preview_invoices.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Invoice Preview (POST)

Generate preview invoices, which includes the estimated tax amounts,
for a billing transaction for the next two billing periods.

Invoice preview provides details of the upcoming invoices for orders or quotes within the
system.

Special Access Rules
:   You need the Billing Operations User or Billing Customer Service permission set to
    use this API.

    See these [requirements](https://help.salesforce.com/s/articleView?id=ind.billing_invoice_preview_procedure_plan_create.htm&language=en_US "HTML (New Window)") to learn
    more about the configuration prerequisites.

Resource
:   ```
    /commerce/invoicing/invoices/collection/actions/preview
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/invoices/collection/actions/preview
    ```

Available version
:   63.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
            "billingTransactionId": "801Z600000004LoIAI",
            "numberOfBillingPeriods": 2,
            "previewDate": "2024-12-04"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `billing​TransactionId` | String | ID of the record to generate the preview invoices for. | Required | 63.0 |
        | `numberOf​BillingPeriods` | Integer | Number of billing periods that the invoice preview is generated for. If unspecified, the default value is `2`. | Optional | 64.0 |
        | `preview​Date` | String | The date on which the preview invoice is generated. For the first invoice, the preview date is the target date for generating the invoice. For the second invoice, the target date is calculated based on the preview date and the minimum billing frequency of the transactions.  The default value is the current date. | Optional | 63.0 |

Response body for POST
:   [Invoice
    Preview](./connect_responses_invoice_preview_output.htm.md "Output representation of the list of preview invoices that are generated for the billing transaction.")
