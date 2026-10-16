---
page_id: connect_requests_field_data_input.htm
title: Field Data Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_field_data_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Field Data Input

Input representation of the details of the field data input.

        
          

**JSON example**

          
: 
            

```
      "fieldDataInputs": [
        {
          "fieldApiName": "MaxQuantity",
          "originalValue": 0.437584,
          "unitOfMeasureId": "uomId2"
        },
        {
          "fieldApiName": "MinQuantity",
          "originalValue": 7364.58923,
          "unitOfMeasureId": "uomId2"
        }
      ]
```

          

        

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `fieldApi​Name` | String | Unique API name of the field. | Required | 63.0 |
| `original​Value` | String | Original value of the fields. | Required | 63.0 |
| `unitOf​MeasureId` | String | ID of the unit of measure record that’s associated to the field. | Required | 63.0 |
