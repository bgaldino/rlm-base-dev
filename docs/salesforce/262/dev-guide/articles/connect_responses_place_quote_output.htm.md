---
page_id: connect_responses_place_quote_output.htm
title: Place Quote
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_place_quote_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Place Quote

Output representation of the request to create or update a quote.

JSON Example
:   This example shows a sample response of the place quote request.
:   ```
    {
        "quoteId": "0Q0xx0000004E2mCAE",
        "requestIdentifier": "95Txx0000004Cx2",
        "responseError": [],
        "statusURL": "/services/data/v60.0/sobjects/RevenueAsyncOperation/95Txx0000004Cx2EAE",
        "success": true
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `quoteId` | String | ID of the quote created after a successful request. | Small, 60.0 | 60.0 |
| `request​Identifier` | String | Unique request identifier that can be used to poll the async request. | Big, 60.0 | 60.0 |
| `response​Error` | [Place Quote Error Response](./connect_responses_place_quote_error_response.htm.md "Output representation of the error responses of a place quote request.") [] | List of errors encountered during the synchronous processing. | Small, 60.0 | 60.0 |
| `status​URL` | String | Asynchronous status URL to track the operation, if available. | Big, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the synchronous part of the processing is successful (`true`) or not (`false`). | Small, 60.0 | 60.0 |
