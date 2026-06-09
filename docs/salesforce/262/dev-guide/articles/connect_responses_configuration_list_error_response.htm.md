---
page_id: connect_responses_configuration_list_error_response.htm
title: Error Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configuration_list_error_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Error Response

Output representation of the details of the error.

JSON example
:   ```
    {
      "errors": [
        {
          "code": "BAD_REQUEST",
          "message": "MISSING_REFERENCEOBJECTID"
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code of the error. | Small, 63.0 | 63.0 |
| `message` | String | Description of the error. | Small, 63.0 | 63.0 |
