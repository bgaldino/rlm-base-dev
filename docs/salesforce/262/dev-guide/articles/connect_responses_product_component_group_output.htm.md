---
page_id: connect_responses_product_component_group_output.htm
title: Product Component Group
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_component_group_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Product Component Group

Output representation of the product component group.

JSON example
:   ```
    "productComponentGroups":[
      {
        "childGroups":[
         {
          "childGroups":[],
        "    components":[
              {
                "additionalFields":{},
                "attributeCategory":[],
                "attributes":[],
                "catalogs":[],
                "categories":[],
                "childProducts":[],
                "id":"01txx0000006i2aAAA",
                "isActive":true,
                "isAssetizable":true,
                "isSoldOnlyWithOtherProds":true,
                "name":"GenWatt Diesel 1000kW",
                "nodeType":"simpleProduct",
                "productCode":"GC1060",
                "productComponentGroups":[],
                "productRelatedComponent":
                 {
                  "childProductId":"01txx0000006i2aAAA",
                  "doesBundlePriceIncludeChild":true,
                  "id":"0dSxx00000001P7EAI",
                  "isComponentRequired":false,
                  "isDefaultComponent":true,
                  "isExcluded":false,
                  "isQuantityEditable":false,
                  "parentProductId":"01txx0000006iC8AAI",
                  "productRelationshipTypeId":"0yoxx000000001dAAA",
                  "quantity":1,
                  "quantityScaleMethod":"Proportional"
                  },
                  "productSellingModelOptions":[]
                  },
                  {
                  "additionalFields":{},
                  "attributeCategory":[],
                  "attributes":[],
                  "catalogs":[],
                  "categories":[],
                  "childProducts":[],
                  "id":"01txx0000006i2TAAQ",
                  "isActive":true,
                  "isAssetizable":true,
                  "isSoldOnlyWithOtherProds":true,
                  "name":"GenWatt Diesel 10kW",
                  "nodeType":"simpleProduct",
                  "productCode":"GC1020",
                  "productComponentGroups":[],
                  "productRelatedComponent":{
                      "childProductId":"01txx0000006i2TAAQ",
                      "doesBundlePriceIncludeChild":true,
                      "id":"0dSxx00000001P8EAI",
                      "isComponentRequired":false,
                      "isDefaultComponent":true,
                      "isExcluded":false,
                      "isQuantityEditable":false,
                      "parentProductId":"01txx0000006iC8AAI",
                      "productRelationshipTypeId":"0yoxx000000001dAAA",
                      "quantity":1,"quantityScaleMethod":"Proportional"
                   },
                  "productSellingModelOptions":[]
                   },
                   {
                    "additionalFields":{},
                    "attributeCategory":[],
                    "attributes":[],
                    "catalogs":[],
                    "categories":[],
                    "childProducts":[],
                    "id":"01txx0000006i2SAAQ",
                    "isActive":true,
                    "isAssetizable":true,
                    "isSoldOnlyWithOtherProds":true,
                    "name":"GenWatt Diesel 200kW",
                    "nodeType":"simpleProduct",
                    "productCode":"GC1040",
                    "productComponentGroups":[],
                    "productRelatedComponent":
                      {
                        "childProductId":"01txx0000006i2SAAQ",
                        "doesBundlePriceIncludeChild":true,
                        "id":"0dSxx00000001P9EAI",
                        "isComponentRequired":false,
                        "isDefaultComponent":true,
                        "isExcluded":false,
                        "isQuantityEditable":false,
                        "parentProductId":"01txx0000006iC8AAI",
                        "productRelationshipTypeId":"0yoxx000000001dAAA",
                        "quantity":1,
                        "quantityScaleMethod":"Proportional"
                       },
                      "productSellingModelOptions":[]
                        }
                      ],
                      "id":"0y7xx000000015lAAA",
                      "isExcluded":false,
                      "name":"G1.1",
                      "parentGroupId":"0y7xx0000000149AAA",
                      "parentProductId":"01txx0000006iC8AAI"
                       }
                      ],
                    "components":[],
                    "id":"0y7xx0000000149AAA",
                    "isExcluded":false,
                    "name":"G1",
                    "parentProductId":"01txx0000006iC8AAI"
                    }
              ]
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Unique code of the product component group, which is used only during design time. | Small, 60.0 | 60.0 |
| `components` | [Product](./connect_responses_product_output.htm.md "Output representation of the product definition.")[] | List of the product details. | Small, 60.0 | 60.0 |
| `childGroups` | [Product Component Group](# "Output representation of the product component group.")[] | List of child product components groups. | Small, 62.0 | 62.0 |
| `description` | String | Description of the product component group. | Small, 60.0 | 60.0 |
| `id` | String | ID of the record. | Small, 60.0 | 60.0 |
| `isExcluded` | Boolean | Indicates whether the product component group is excluded from the product bundle for selection in the run time (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `max​Bundle​Components` | Integer | Maximum number of product components that can be added to a group. | Small, 60.0 | 60.0 |
| `min​Bundle​Components` | Integer | Minimum number of product components that can be added to a group. | Small, 60.0 | 60.0 |
| `name` | String | Name of the record. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `parent​Product​Id` | String | ID associated with the parent product record. | Small, 60.0 | 60.0 |
| `parent​GroupId` | String | ID of the parent group record. | Small, 62.0 | 62.0 |
| `sequence` | Integer | Order in which the groups are listed in the bundle. | Small, 60.0 | 60.0 |
