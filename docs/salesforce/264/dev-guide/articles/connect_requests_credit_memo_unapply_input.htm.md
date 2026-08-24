---
page_id: connect_requests_credit_memo_unapply_input.htm
title: Credit Memo Unapply Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_credit_memo_unapply_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Credit Memo Unapply Input

Input representation of the request to unapply a credit memo from an invoice.

**JSON example**

: 

```
    {
      "description": "Unapply credit memo from invoice to revert an error",
      "effectiveDate": "2024-07-01"
    }
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Explanation or reason for unapplying the credit memo. | Optional | 62.0 |
| `effectiveDate` | String | Effective date for the credit memo. | Optional | 62.0 |
