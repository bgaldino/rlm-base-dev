---
page_id: connect_responses_p_c_m_error_output.htm
title: Product Catalog Management Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_p_c_m_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Product Catalog Management Error

Output representation that contains error details, including error codes and
messages.

JSON example
:   ```
    {
      "errorCode": "INSUFFICIENT_ACCESS",
      "message": "Insufficient access rights on cross-reference ID"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Error code that identifies the type of error. | Small, 66.0 | 66.0 |
| `message` | String | Message that explains the reason for the error. | Small, 66.0 | 66.0 |
