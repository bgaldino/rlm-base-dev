---
page_id: connect_responses_epc_error_output.htm
title: Error Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_epc_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Error Output

Output representation of the error details.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Code of the error message. | Small, 60.0 | 60.0 |
| `message​Detail` | String | Details of the error message. | Small, 60.0 | 60.0 |
| `message​Title` | String | Title of the error message. | Small, 60.0 | 60.0 |
| `node​ProductId` | String | ID of the product node. | Small, 61.0 | 61.0 |
| `record​Id` | String | ID of the record. | Small, 60.0 | 60.0 |
| `record​Name` | String | Name of the record. | Small, 60.0 | 60.0 |
| `related​ObjectNodes` | [Invalid Related Object Node](./connect_responses_invalid_related_object_node_output.htm.md "Output representation of the invalid related object node with details of errors.")[] | List of related object nodes with errors. | Small, 62.0 | 62.0 |
| `source` | String | Name of the API that’s the source of the error. | Small, 60.0 | 60.0 |
