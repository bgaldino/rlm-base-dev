---
page_id: connect_responses_tax_imposition_output.htm
title: Tax Imposition
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_imposition_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Tax Imposition

Output representation of the details of the imposed tax.

JSON example
:   ```
    {
      "type": "Parish",
      "name": "Burbank"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `name` | String | Name of the tax imposition. | Big, 62.0 | 62.0 |
| `type` | String | Type of the tax imposition. | Big, 62.0 | 62.0 |
