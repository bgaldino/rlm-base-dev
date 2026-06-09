---
page_id: connect_resources_payment_line_unapply.htm
title: Payment Line Unapply (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_payment_line_unapply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Payment Line Unapply (POST)

Revert the application of a payment line from an invoice, and return the
payment and invoices to their preapplication state. Use this API to correct an input during
the payment application process.

For example, you can use this API to revert an incorrect payment that's applied to an
invoice, or to rectify an incorrect amount.

Use the Commerce Payments APIs to send your payment and
refund details to external payment gateways for processing against a customer's bank. See
[Commerce Payments resources](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_resources_payments.htm "HTML (New Window)")
to check the APIs for payment gateways, payment captures, and payment authorizations.

Resource
:   ```
    /commerce/billing/payments/paymentId/paymentlines/paymentLineId/actions/unapply
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/billing/payments/0aQ1j000000001O/paymentlines/1PLR000000000dDOAQ/actions/unapply
    ```

Available version
:   64.0

HTTP methods
:   POST

Path parameters for POST
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `paymentId` | String | ID of the payment record. | Required | 64.0 |
    | `payment​LineId` | String | ID of the payment line record. | Required | 64.0 |

Request body for POST
:   JSON example
    :   ```
        {
          "effectiveDate": "2025-05-22T11:30:25.000Z",
          "comments": "Unapply payment"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `comments` | String | Comments that you can add when you revert a payment line application. | Optional | 64.0 |
        | `effective​Date` | String | Date from when the reversal of the payment line application is in effect. | Optional | 64.0 |

Response body for POST
:   [Payment Line
    Unapply](./connect_responses_payment_line_unapply_output.htm.md "Output representation of the details of the reversed payment line application. The details include the ID of the payment line record and date when the payment line application was reversed.")
