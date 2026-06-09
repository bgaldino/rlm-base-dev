---
page_id: apex_connectapi_output_reference_line_error.htm
title: ConnectApi.ReferenceLineError
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_reference_line_error.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.ReferenceLineError

Output representation of the details of the line level errors.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm "HTML (New Window)")> | List of errors with error code and error message for the specified invoice line ID. | 62.0 |
| `reference​LineId` | String | ID of the invoice line specified in the API request that has an issue, causing the API request to fail. | 62.0 |
