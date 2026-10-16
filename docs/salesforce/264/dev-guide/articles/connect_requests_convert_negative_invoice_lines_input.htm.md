---
page_id: connect_requests_convert_negative_invoice_lines_input.htm
title: Convert Negative Invoice Lines Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_convert_negative_invoice_lines_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Convert Negative Invoice Lines Input

Input representation of the details of the request to convert a list of negative invoice
    lines into a credit.

**JSON example**

: 

```
  {
  "invoiceLines": ["5TVxx0000004C92GAE", "5TVxx0000004C93GAE"],
  "description": "Convert negative invoice lines into credit",
  "effectiveDate":"2022-05-18"
  }
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | Description stamped on the credit memo that’s created after the negative invoice line conversion. | Optional | 62.0 |
| `effectiveDate` | String | Date stamped on the credit memo that’s created after the negative invoice line conversion. | Required | 62.0 |
| `invoiceLines` | String[] | Complete list of the negative invoice lines along with the associated invoice line taxes. The specified negative invoice lines are converted into a posted credit memo. | Optional | 62.0 |
