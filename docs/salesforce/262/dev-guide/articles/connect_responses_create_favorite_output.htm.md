---
page_id: connect_responses_create_favorite_output.htm
title: Configuration Record Save
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_create_favorite_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configuration Record Save

Output representation of the details of a saved configuration.

JSON example
:   This example shows a sample when the save operation is successful.
:   ```
    {
      "errors": [],
      "id": "1Nyxx0000004CNYCA2"
    }
    ```
:   This example shows a sample when the save operation has errors.
:   ```
    {
      "errors": [{
      "code": "INTERNAL_SERVER_ERROR",
      "message": "INVALID_REFERENCEOBJECTID"
    }]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](./connect_responses_configuration_list_error_response.htm.md "Output representation of the details of the error.") | List of errors that contains a message and an error code. | Small, 63.0 | 63.0 |
| `id` | String | ID of the configuration that's saved. This property isn't shown if the operation has errors. | Small, 63.0 | 63.0 |
