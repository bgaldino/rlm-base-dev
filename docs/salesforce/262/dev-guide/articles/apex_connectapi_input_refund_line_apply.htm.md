---
page_id: apex_connectapi_input_refund_line_apply.htm
title: ConnectApi.RefundLineApplyRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_refund_line_apply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.RefundLineApplyRequest

Input representation of the details of a transaction refund request. This representation
outlines the properties of a refund, including the refund amount and ID of the payment or credit
memo record that the refund is applied to.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Amount to refund. | Required | 64.0 |
| `appliedToId` | String | ID of a payment or credit memo record. The refund is applied to this object. | Required | 64.0 |
| `comments` | String | Additional details of the refund request. | Optional | 64.0 |
| `effectiveDate` | Datetime | Date from when the refund is in effect. | Optional | 64.0 |
