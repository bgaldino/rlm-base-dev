---
page_id: connect_responses_credit_memo_post_output.htm
title: Credit Memo Post
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_credit_memo_post_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Credit Memo Post

Output representation of the request to post a credit memo.

JSON example
:   This example shows a sample successful
    response.

    ```
    {
      "errors": [],
      "requestIdentifier": "d3a9d9ce-2a83-4a08-bcf3-df0348a0008c",
      "statusURL": "/services/data/v67.0/sobjects/AsyncOperationTracker/16PDU000000A4oz2AC",
      "success": true
    }
    ```
:   This example shows a sample error
    response.

    ```
    {
      "errors": [
        {
          "errorCode": "BAD_REQUEST",
          "message": "You can post up to 1 credit memo at a time."
        }
      ],
      "requestIdentifier": "9065b043-dcc3-4dcf-b5a1-55fdf5a79f7b",
      "statusURL": "",
      "success": false
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` |  | List of errors encountered during the processing of the API request. | Big, 65.0 | 65.0 |
| `requestIdentifier` | String | Unique request identifier for the request. | Big, 65.0 | 65.0 |
| `statusURL` | String | Status URL for tracking this operation. | Big, 65.0 | 65.0 |
| `success` | Boolean | Indicates whether the API request was successful (`true`) or not (`false`). | Big, 65.0 | 65.0 |
