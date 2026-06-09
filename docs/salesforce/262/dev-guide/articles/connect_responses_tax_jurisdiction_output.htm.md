---
page_id: connect_responses_tax_jurisdiction_output.htm
title: Tax Jurisdiction
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_tax_jurisdiction_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Tax Jurisdiction

Output representation of the details of the tax jurisdiction for the tax
line.

JSON example
:   ```
    {
        "country": "US",
        "id": "63000",
        "level": "CIT",
        "name": "SEATTLE",
        "region": "WA",
        "stateAssignedNo": "1726"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `country` | String | Country of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `id` | String | ID of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `level` | String | Level of the tax jurisdiction, for example, `State` and `Federal`. | Big, 62.0 | 62.0 |
| `name` | String | Name of the tax jurisdiction authority. | Big, 62.0 | 62.0 |
| `region` | String | Parent region of the tax jurisdiction. | Big, 62.0 | 62.0 |
| `stateAssigned​No` | String | Number of the assigned state. | Big, 62.0 | 62.0 |
