---
page_id: apex_connectapi_input_credit_memo_line_apply.htm
title: ConnectApi.CreditMemoLineApplyInput
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_credit_memo_line_apply.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_apex_input_classes.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# ConnectApi.CreditMemoLineApplyInput

Input representation of the details of the request to apply a credit memo line to an
    invoice line.

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applyCreditDetails` | List<[`ConnectApi.CreditDetailsApplyInput`](./apex_connectapi_input_credit_memo_line_application.htm.md)> | List of one or more applications to apply the credit memo line for. Each application represents an invoice line that’s credited by using the balance of the specified credit memo line. | Required | 62.0 |
| `creditMemoLineId` | String | ID of the credit memo line record. | Required | 62.0 |
