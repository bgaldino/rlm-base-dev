---
page_id: connect_responses_tax_details_output.htm
title: Tax Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_details_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Tax Details

Output representation of the tax details for each line item.

JSON example
:   ```
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
| `imposition` | [Tax Imposition](./connect_responses_tax_imposition_output.htm.md "Output representation of the details of the imposed tax.") | Tax imposition details applicable to the line item. | Big, 62.0 | 62.0 |
| `jurisdiction` | [Tax Jurisdiction](./connect_responses_tax_jurisdiction_output.htm.md "Output representation of the details of the tax jurisdiction for the tax line.") | Details of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `rate` | Double | Tax rate applied to the taxable amount to calculate the tax. | Big, 62.0 | 62.0 |
| `tax` | Double | Actual amount of tax that’s applicable to the line item. | Big, 62.0 | 62.0 |
| `taxId` | String | Unique identifier such as a code or a number that’s assigned to a specific tax. This value helps users identify which type of tax is applied. | Big, 62.0 | 62.0 |
| `taxableAmount` | Double | Total amount of the line item that’s eligible for taxation. | Big, 62.0 | 62.0 |
