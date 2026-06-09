---
page_id: connect_resources_apply_refund_to_payment.htm
title: Refund Line Apply (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_apply_refund_to_payment.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Refund Line Apply (POST)

Make a refund transaction against a payment.

Resource
:   ```
    /commerce/billing/refunds/refundId/actions/apply
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/billing/refunds/0cbVc0000000G4nIAE/actions/apply
    ```

Available version
:   64.0

HTTP methods
:   POST

Path parameter for POST
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `refundId` | String | ID of the refund record. | Required | 64.0 |

Request body for POST
:   JSON example
    :   ```
        {
          "appliedToId": "0aQR00000004ZkKMAU",
          "amount": 10,
          "effectiveDate": "2020-08-11T07:53:15.000Z",
          "comments": "Payment application."
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `amount` | Double | Amount to refund. | Required | 64.0 |
        | `appliedToId` | String | ID of a payment or credit memo record. The refund is applied to this object. | Required | 64.0 |
        | `comments` | String | Additional details of the refund request. | Optional | 64.0 |
        | `effectiveDate` | String | Date from when the refund is in effect. | Optional | 64.0 |

Response body for POST
:   [Refund Line
    Apply](./connect_responses_refund_line_apply_output.htm.md "Output representation of the details of an applied refund. This representation includes the properties of a refund line, such as the date when the refund is applied against a payment and ID of the refund line record.")
