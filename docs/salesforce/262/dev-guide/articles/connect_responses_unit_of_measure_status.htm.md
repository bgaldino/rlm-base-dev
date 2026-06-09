---
page_id: connect_responses_unit_of_measure_status.htm
title: Unit of Measure Status
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_unit_of_measure_status.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Unit of Measure Status

Output representation of the status of the Unit of Measure API request.

JSON example
:   ```
      "status": {
        "errors": [],
        "httpStatusCode": "200",
        "message": " Successfully fetched UnitOfMeasure Info. "
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Unit Of Measure Error](./connect_responses_unit_of_measure_error_output.htm.md "Output representation of the details of errors encountered during the processing of the Unit of Measure API request.")[] | Errors encountered during the processing of the API request. | Small, 63.0 | 63.0 |
| `httpStatus​Code` | String | HTTP status code of the API request. | Small, 63.0 | 63.0 |
| `message` | String | Localized response message. | Small, 63.0 | 63.0 |
