---
page_id: connect_responses_qualification_context_output.htm
title: Qualification Context
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_qualification_context_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Qualification Context

Output representation of the details about the product qualification.

JSON example
:   ```
    {
      "qualificationContext": {
        "isQualified": true
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `isQualified` | Boolean | Indicates whether the product is qualified (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `reason` | String | Specifies the reason for product qualification or disqualification. | Small, 67.0 | 67.0 |
