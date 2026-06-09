---
page_id: connect_responses_status.htm
title: Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_status.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Status

Output representation of the status of the request.

JSON example
:   ```
    "status": {
        "code": "200",
        "errors": [],
        "message": "Successfully fetched the catalog records."
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Code of the error message. | Small, 60.0 | 60.0 |
| `errors` | [Error](./connect_responses_epc_error_output.htm.md "Output representation of the error details.")[] | Details of the error. | Small, 60.0 | 60.0 |
| `message` | String | Error message. | Small, 60.0 | 60.0 |
