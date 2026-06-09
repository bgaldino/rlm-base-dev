---
page_id: connect_responses_revenue_async_output.htm
title: Revenue Async Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_revenue_async_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Revenue Async Response

Output representation of the result of the API request with the request
identifier.

JSON example
:   ```
      {
        "errors": null,
        "requestIdentifier": "ae6f23bc-f056-44b7-aa4d-c7f6fc5e0cf4",
        "success": true
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)") | Details of errors, if any. | Big, 62.0 | 62.0 |
| `request​Identifier` | String | Unique identifier of the request. | Big, 62.0 | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Big, 62.0 | 62.0 |
