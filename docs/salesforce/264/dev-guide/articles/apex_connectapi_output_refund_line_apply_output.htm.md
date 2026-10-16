---
page_id: apex_connectapi_output_refund_line_apply_output.htm
title: ConnectApi.RefundLineApplyResponse
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_output_refund_line_apply_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_output_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.RefundLineApplyResponse

Output representation of the details of an applied refund. This representation includes
    the properties of a refund line, such as the date when the refund is applied against a payment
    and ID of the refund line record.

| Property Name | Type | Description | Available Version |
| --- | --- | --- | --- |
| `appliedDate` | Datetime | Date when the refund is applied against a payment. | 64.0 |
| `id` | String | ID of the refund line record. | 64.0 |
