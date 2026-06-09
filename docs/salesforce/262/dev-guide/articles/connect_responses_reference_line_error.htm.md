---
page_id: connect_responses_reference_line_error.htm
title: Reference Line Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_reference_line_error.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Reference Line Error

Output representation of the details of the line level errors.

JSON example
:   If the API request fails, the `referenceLineErrorResults` property contains a list of errors grouped by the
    invoice line IDs.

    ```
    [
      {
        "referenceLineId": "5TV9A000007x2gz",
        "errors": [
          {
            "errorCode": "INVALID_INPUT",
            "message": "Invalid invoice line id"
          }
        ]
      }
    ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)") | List of errors with error code and error message for the specified invoice line ID. | Big, 62.0 | 62.0 |
| `reference​LineId` | String | ID of the invoice line specified in the API request that has an issue, causing the API request to fail. | Small, 62.0 | 62.0 |
