---
page_id: connect_responses_tax_amount_details_output.htm
title: Tax Amount Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_amount_details_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-11-23
---

# Tax Amount Details

Output representation of the details of the tax amount.

## JSON Example

```
{
    "exemptAmount": 0.0,
    "taxAmount": 12.5,
    "totalAmount": 100.0,
    "totalAmountWithTax": 112.5
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `exemptAmount` | Double | Amount exempted from taxation. | Big, 62.0 | 62.0 |
| `taxAmount` | Double | Tax amount applicable to the transaction. | Big, 62.0 | 62.0 |
| `totalAmount` | Double | Total amount without tax. | Big, 62.0 | 62.0 |
| `totalAmount​WithTax` | Double | Total amount with tax. The `totalAmountWithTax` property value is the sum of the `taxAmount` and `totalAmount` property values. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_amount_details_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
