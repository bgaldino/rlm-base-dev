---
page_id: connect_resources_void_posted_credit_memo.htm
title: Void Posted Credit Memo (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_void_posted_credit_memo.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Void Posted Credit Memo (POST)

Void a credit memo in posted state.

The API response returns a unique identifier. In case of any asynchronous errors, a
RevenueTransactionErrorLog record is created.

Resource
:   ```
    /commerce/billing/credit-memos/creditMemoId/actions/void
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/billing/credit-memos/50gVB0000003khRYAQ/actions/void
    ```

Available version
:   66.0

HTTP methods
:   POST

Path parameter for POST
:   Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `creditMemoId` | String | ID of the posted credit memo to be voided. | Required | 66.0 |

Request body for POST
:   As this API accepts a credit memo ID as a path parameter in the URL, specify an empty
    request body.

Response body for POST
:   [Void Posted Credit
    Memo](./connect_responses_void_posted_credit_memo_output.htm.md "Output representation of the request to void a posted credit memo.")
