---
page_id: connect_responses_usage_detail_error_response.htm
title: Usage Details Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_detail_error_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Usage Details Error Response

Output representation of the details of an error related to usage details.

JSON Example
:   ```
    {
       "errors": [
            {
                "referenceId": "MyOrderItem",
                "errorCode": "INVALID_API_INPUT",
                "message": "Something has failed"
            }
       ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code associated with the error. | Small, 63.0 | 63.0 |
| `message` | String | Message associated with the error. | Small, 63.0 | 63.0 |
| `referenceId` | String | Unique ID that’s associated with the specific error for tracking and reference purposes. | Small, 63.0 | 63.0 |
