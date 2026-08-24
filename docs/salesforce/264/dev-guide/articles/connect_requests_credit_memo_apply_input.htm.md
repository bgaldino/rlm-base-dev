---
page_id: connect_requests_credit_memo_apply_input.htm
title: Credit Memo Apply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_apply_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Credit Memo Apply Input

Input representation of the request to apply a credit memo to an invoice.

**JSON example**

: 

```
{
  "applications": [
    {
      "appliedToId": "3ttxx000000003FAAQ",
      "amount": 10,
      "description": "Apply to invoice for refund",
      "effectiveDate": "2024-07-01"
    },
    {
      "appliedToId": "3ttxx0000000001AAA",
      "amount": 100
    }
  ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `applications` | [Credit Memo Apply Application Input](./connect_requests_credit_memo_apply_application_input.htm.md)[] | List of one or more applications to apply the credit memo for. Each application represents an invoice that’s credited by using the balance of the specified credit memo. | Required | 62.0 |
