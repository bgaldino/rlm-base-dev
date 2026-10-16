---
page_id: apex_connectapi_output_payment_line_unapply_output.htm
title: ConnectApi.PaymentLineUnapplyResponse
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_payment_line_unapply_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.PaymentLineUnapplyResponse

Output representation of the details of the reversed payment line application. The
    details include the ID of the payment line record and date when the payment line application was
    reversed.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `id` | String | ID of the payment line record. | 64.0 |
| `unapplied​Date` | Datetime | Date when the payment line application was reversed. | 64.0 |
