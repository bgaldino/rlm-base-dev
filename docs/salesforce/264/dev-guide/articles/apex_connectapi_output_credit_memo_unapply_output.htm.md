---
page_id: apex_connectapi_output_credit_memo_unapply_output.htm
title: ConnectApi.UnapplyCreditResult
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_credit_memo_unapply_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.UnapplyCreditResult

Output representation of the details of the credit memo invoice application record with
    the status of the request.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.264.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm)> | List of errors encountered during the processing of the API request. | 62.0 |
| `id` | String | ID of the credit memo invoice application record. | 62.0 |
| `success` | Boolean | Indicates whether the credit memo is successfully unapplied (`true`) or not (`false`). | 62.0 |
