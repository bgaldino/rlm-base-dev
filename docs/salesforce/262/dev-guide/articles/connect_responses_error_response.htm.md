---
page_id: connect_responses_error_response.htm
title: Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_error_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Error Response

Output representation of the error details encountered during the API
request.

JSON example
:   This example shows a sample error
    response.

    ```
    {
      "errors": [
        {
          "errorCode": "INVALID_STATUS",
          "message": "CreditMemo 50gxx00000000XtAAI is not in the Posted status."
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code that indicates the type of error. | Big, 66.0 | 66.0 |
| `message` | String | Message stating the reason for error, if any. | Big, 66.0 | 66.0 |
