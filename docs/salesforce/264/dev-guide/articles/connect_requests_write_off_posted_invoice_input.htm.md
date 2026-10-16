---
page_id: connect_requests_write_off_posted_invoice_input.htm
title: Posted Invoice Write-Off Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_write_off_posted_invoice_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Posted Invoice Write-Off Input

Input representation of the details of the request to write off a posted invoice. This
    representation includes invoice details such as invoice ID and reason for writing off
    invoices.

**JSON example**

: 

```
{
  "invoices": [
    {
      "invoiceId": "3ttxx00000000cjAAA",
      "reasonCode": "Bad Debt",
      "description": "Bad Debt"
    },
    {
      "invoiceId": "3ttxx00000000cjAAA",
      "reasonCode": "Concession",
      "description": "Concession"
    }
  ]
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `invoiceId` | String | ID of the invoice record that you want to write off. | Required | 64.0 |
| `reason` | String | Reason for writing off invoices. | Optional | 64.0 |
| `reason​Code` | String | Code that categorizes the write-off reason. For example, if the reason for the invoice write-off is a disputed amount, the reason code can be Disputed Amount (DA). | Required | 64.0 |
