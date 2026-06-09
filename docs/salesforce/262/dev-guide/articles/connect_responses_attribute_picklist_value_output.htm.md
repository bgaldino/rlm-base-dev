---
page_id: connect_responses_attribute_picklist_value_output.htm
title: Attribute Picklist Value
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_attribute_picklist_value_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Attribute Picklist Value

Output representation of the attribute picklist value.

JSON example
:   ```
    "values": [
          {
            "abbreviation": "IFM1"
            "code": "PV0051",
            "displayValue": "25G Intelligent Fabric Module with 8x 25G SFP28 ports",
            "id": "0v61Q0000008OMYQA2",
            "name": "25G Intelligent Fabric Module with 8x 25G SFP28 ports",
            "sequence": "1",
            "value": "25G Intelligent Fabric Module with 8x 25G SFP28 ports",
            "status" : "Active"
          }
         ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `abbreviation` | String | Name of the picklist value that appears at run time. | Small, 60.0 | 60.0 |
| `code` | String | Unique code of the picklist value within the picklist. | Small, 60.0 | 60.0 |
| `display​Value` | String | Picklist value that appears at run time in the order capture page. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `id` | String | ID associated with the attribute picklist value. | Small, 60.0 | 60.0 |
| `name` | String | Name of the picklist value. | Small, 60.0 | 60.0 |
| `sequence` | String | Order in which the picklist value appears in the picklist. | Small, 60.0 | 60.0 |
| `status` | String | Status of the attribute picklist value. | Small, 62.0 | 62.0 |
| `value` | String | Value of the picklist item. Value must be unique within the picklist. | Small, 60.0 | 60.0 |
