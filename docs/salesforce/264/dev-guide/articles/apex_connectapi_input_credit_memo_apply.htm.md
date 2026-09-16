---
page_id: apex_connectapi_input_credit_memo_apply.htm
title: ConnectApi.CreditMemoApplyInputRequest
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_apply.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.CreditMemoApplyInputRequest

Input representation of the request to apply a credit memo to an invoice.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applications` | List<[ConnectApi.ApplicationsRequest](./apex_connectapi_input_credit_memo_apply_application.htm.md)> | List of one or more applications to apply the credit memo for. Each application represents an invoice that’s credited by using the balance of the specified credit memo. | Required | 62.0 |
| `creditMemoId` | String | ID of the credit memo record. | Required | 62.0 |
