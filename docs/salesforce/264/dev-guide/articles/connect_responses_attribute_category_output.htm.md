---
page_id: connect_responses_attribute_category_output.htm
title: Attribute Category
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_attribute_category_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Attribute Category

Output representation of the attribute category.

      
        
          

**JSON example**

          
: 
            

```
"attributeCategory": [
        {
          "attributes": [
            {
              "additionalFields": {
                "scope": "Order"
              },
              "attributeNameOverride": "AD Text",
              "code": "AD02",
              "dataType": "Text",
              "defaultValue": "AD Text DV",
              "description": "AD Text Desc",
              "displayType": "Text",
              "helpText": "AD Text DHT",
              "id": "0tjT1000000002bIAA",
              "isHidden": false,
              "isPriceImpacting": true,
              "isReadOnly": true,
              "isRequired": true,
              "label": "AD Text Label",
              "maximumCharacterCount": "20",
              "maximumValue": "100",
              "minimumCharacterCount": "1",
              "minimumValue": "50",
              "name": "AD Text",
              "sequence": 1,
              "status": "Active",
              "valueDescription": "AD Text VD"
            }
          ],
          "code": "AC001",
          "id": "0v3T1000000000BIAQ",
          "name": "build and make"
    }
]
```

          

        
      

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributes` | [Attribute Definition](./connect_responses_attribute_definition_output.htm.md)[] | List of categorized attributes associated with the product. | Small, 60.0 | 60.0 |
| `code` | String | Code of the attribute category. | Small, 60.0 | 60.0 |
| `id` | String | ID associated with the attribute category. | Small, 60.0 | 60.0 |
| `name` | String | Name of the attribute category. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
