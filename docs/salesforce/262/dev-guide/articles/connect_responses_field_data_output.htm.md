---
page_id: connect_responses_field_data_output.htm
title: Field Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_field_data_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Field Data

Output representation of the field data.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect_responses_unit_of_measure_error_output.htm.md "Output representation of the details of errors encountered during the processing of the Unit of Measure API request.")> | Error codes mapped to their details. | Small, 63.0 | 63.0 |
| `fieldApiName` | String | Unique API Name of the field. | Small, 63.0 | 63.0 |
| `isRounding​Applicable` | Boolean | Indicates whether data rounding is applicable to the decimal (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `original​Value` | String | Original value of the field. | Small, 63.0 | 63.0 |
| `rounded​Value` | String | Rounded field value that corresponds to the original value, if data rounding is applicable. | Small, 63.0 | 63.0 |
| `unitOf​MeasureId` | String | ID of the unit of measure record that’s associated to the field. | Small, 63.0 | 63.0 |
