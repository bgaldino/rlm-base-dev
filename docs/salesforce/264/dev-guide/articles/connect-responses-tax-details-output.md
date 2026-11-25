---
page_id: connect-responses-tax-details-output
title: Tax Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-tax-details-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-responses
legacy_page_id: connect_responses_tax_details_output.htm
fetched_at: 2026-11-25
---

# Tax Details

Output representation of the tax details for each line item.

## JSON Example

```
{
  "taxes": [
    {
      "exemptAmount": 0,
      "exemptReason": "NoExemption",
      "imposition": {
        "type": "General"
      },
      "jurisdiction": {
        "country": "US",
        "id": "63000",
        "level": "CIT",
        "name": "SEATTLE",
        "region": "WA",
        "stateAssignedNo": "1726"
      },
      "rate": 12.5,
      "tax": 12.5,
      "taxId": "11000378132466",
      "taxableAmount": 100
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `exemptAmount` | Double | Amount exempted from taxation for the line item. | Big, 62.0 | 62.0 |
| `exemptReason` | String | Reason for the tax exemption. | Big, 62.0 | 62.0 |
| `imposition` | [Tax Imposition](./connect-responses-tax-imposition-output.md) | Tax imposition details applicable to the line item. | Big, 62.0 | 62.0 |
| `jurisdiction` | [Tax Jurisdiction](./connect-responses-tax-jurisdiction-output.md) | Details of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `rate` | Double | Tax rate applied to the taxable amount to calculate the tax. | Big, 62.0 | 62.0 |
| `tax` | Double | Actual amount of tax that’s applicable to the line item. | Big, 62.0 | 62.0 |
| `taxId` | String | Unique identifier such as a code or a number that’s assigned to a specific tax. This value helps users identify which type of tax is applied. | Big, 62.0 | 62.0 |
| `taxableAmount` | Double | Total amount of the line item that’s eligible for taxation. | Big, 62.0 | 62.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-tax-details-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
