---
page_id: apex_connectapi_output_invoice_recovery_output.htm
title: ConnectApi.InvoiceRecoveryResult
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_invoice_recovery_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.InvoiceRecoveryResult

Output representation of the details of the recovered invoice and billing
schedules.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `billing​Schedules` | List<[ConnectApi.BillingScheduleRecoveryResult](./apex_connectapi_output_billing_schedule_recovery_output.htm.md "Output representation of the details of the recovered billing schedules.")> | Billing schedules associated with this invoice. | 62.0 |
| `invoice​Errors` | List<[ConnectApi.ErrorResponse](https://developer.salesforce.com/docs/atlas.en-us.262.0.apexref.meta/apexref/apex_connectapi_output_error_response.htm "HTML (New Window)")> | List of errors encountered during the invoice recovery. | 62.0 |
| `invoice​Id` | String | ID of the recovered invoice. | 62.0 |
| `invoice​Status` | String | Flag that indicates the invoice status. | 62.0 |
| `success` | Boolean | Indicates whether the overall transaction was successful or not (`true`) or not (`false`). | 62.0 |
