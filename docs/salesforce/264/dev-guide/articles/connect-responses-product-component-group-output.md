---
page_id: connect-responses-product-component-group-output
title: Product Component Group
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-component-group-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_product_component_group_output.htm
fetched_at: 2026-11-25
---

# Product Component Group

Output representation of the product component group.

## JSON Example

```
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

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | Unique code of the product component group, which is used only during design time. | Small, 60.0 | 60.0 |
| `components` | [Product](./connect-responses-product-output.md)[] | List of the product details. | Small, 60.0 | 60.0 |
| `childGroups` | [Product Component Group](./connect-responses-product-component-group-output.md)[] | List of child product components groups. | Small, 62.0 | 62.0 |
| `description` | String | Description of the product component group. | Small, 60.0 | 60.0 |
| `id` | String | ID of the record. | Small, 60.0 | 60.0 |
| `isExcluded` | Boolean | Indicates whether the product component group is excluded from the product bundle for selection in the run time (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `max​Bundle​Components` | Integer | Maximum number of product components that can be added to a group. | Small, 60.0 | 60.0 |
| `min​Bundle​Components` | Integer | Minimum number of product components that can be added to a group. | Small, 60.0 | 60.0 |
| `name` | String | Name of the record. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `parent​Product​Id` | String | ID associated with the parent product record. | Small, 60.0 | 60.0 |
| `parent​GroupId` | String | ID of the parent group record. | Small, 62.0 | 62.0 |
| `sequence` | Integer | Order in which the groups are listed in the bundle. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-component-group-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
