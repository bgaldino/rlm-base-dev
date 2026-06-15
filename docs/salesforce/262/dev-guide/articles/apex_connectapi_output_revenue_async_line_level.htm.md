---
page_id: apex_connectapi_output_revenue_async_line_level.htm
title: ConnectApi.RevenueAsyncLineLevelOutputResponse
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_revenue_async_line_level.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.RevenueAsyncLineLevelOutputResponse

Output representation of the result of the API request for the async line level
operations.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm "HTML (New Window)")> | Details of errors, if any. | 62.0 |
| `referenceLineErrorResults` | List<[ConnectApi.ReferenceLineError](./apex_connectapi_output_reference_line_error.htm.md "Output representation of the details of the line level errors.")> | List of errors grouped by the invoice line IDs if the API request fails. | 62.0 |
| `referenceLineType` | String | Reference type for the reference line entity in the `referenceLineErrorResults` property. | 62.0 |
| `requestIdentifier` | String | Unique identifier of the request. | 62.0 |
| `statusURL` | String | URL to track the status of the operation. | 62.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | 62.0 |
