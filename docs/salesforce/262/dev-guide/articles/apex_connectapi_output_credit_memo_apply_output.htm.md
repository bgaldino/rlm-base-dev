---
page_id: apex_connectapi_output_credit_memo_apply_output.htm
title: ConnectApi.ApplyCreditResult
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_credit_memo_apply_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.ApplyCreditResult

Connect API representation of credit memo apply output result

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `appliedToId` | String | ID of the invoice record that the credit is applied to. | 62.0 |
| `errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm "HTML (New Window)")> | List of errors encountered during the processing of the API request. | 62.0 |
| `id` | String | ID of the credit memo invoice application. | 62.0 |
| `success` | Boolean | Indicates whether the credit memo is successfully applied (`true`) or not (`false`). | 62.0 |
