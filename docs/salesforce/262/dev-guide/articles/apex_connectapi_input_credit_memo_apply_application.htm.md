---
page_id: apex_connectapi_input_credit_memo_apply_application.htm
title: ConnectApi.ApplicationsRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_apply_application.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.ApplicationsRequest

Connect API representation of an application item input request for credit memo apply api

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `amount` | Double | Credit amount to be applied to the invoice. | Required | 62.0 |
| `appliedToId` | String | ID of the invoice record to apply the credit for. | Required | 62.0 |
| `description` | String | Explanation or reason for applying the credit memo. | Optional | 62.0 |
| `effectiveDate` | String | Effective date for the credit memo. | Optional | 62.0 |
