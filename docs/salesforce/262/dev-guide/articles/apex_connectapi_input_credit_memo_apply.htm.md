---
page_id: apex_connectapi_input_credit_memo_apply.htm
title: ConnectApi.CreditMemoApplyInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_apply.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.CreditMemoApplyInputRequest

Input representation of the request to apply a credit memo to an invoice.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applications` | List<[ConnectApi.ApplicationsRequest](./apex_connectapi_input_credit_memo_apply_application.htm.md "Connect API representation of an application item input request for credit memo apply api")> | List of one or more applications to apply the credit memo for. Each application represents an invoice that’s credited by using the balance of the specified credit memo. | Required | 62.0 |
| `creditMemoId` | String | ID of the credit memo record. | Required | 62.0 |
