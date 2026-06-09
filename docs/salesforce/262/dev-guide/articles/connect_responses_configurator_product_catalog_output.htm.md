---
page_id: connect_responses_configurator_product_catalog_output.htm
title: Configurator Product Catalog
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_catalog_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configurator Product Catalog

Output representation of the product catalog.

JSON example
:   ```
      "catalogProducts": {
        "additionalFields": [],
        "attributeCategories": [
          {
            "attributes": [
              {
                "attributeCategoryId": "0v3xx0000000001AAA",
                "attributeNameOverride": "Load Capacity",
                "code": "CAP",
                "dataType": "NUMBER",
                "defaultValue": "1500",
                "description": "Server racks are designed to support a specific load capacity, commonly measured in kilograms (kg) or pounds (lbs). Typical load capacities range from 500 kg (1102 lbs) to 1500 kg (3307 lbs) depending on the model.",
                "id": "0tjxx00000001DpAAI",
                "isCloneable": false,
                "isConfigurable": true,
                "isHidden": false,
                "isPriceImpacting": false,
                "isReadOnly": false,
                "isRequired": false,
                "label": "Load Capacity",
                "name": "Load Capacity"
              },
              {
                "attributeCategoryId": "0v3xx0000000001AAA",
                "attributeNameOverride": "Expansion Slots",
                "code": "SLOTCAP",
                "dataType": "NUMBER",
                "defaultValue": "12",
                "id": "0tjxx00000001H3AAI",
                "isCloneable": false,
                "isConfigurable": true,
                "isHidden": false,
                "isPriceImpacting": false,
                "isReadOnly": false,
                "isRequired": true,
                "label": "Expansion Slots",
                "name": "Expansion Slots"
              },
              {
                "attributeCategoryId": "0v3xx0000000001AAA",
                "attributeNameOverride": "Memory",
                "attributePicklist": {
                  "id": "0v5xx0000000001AAA",
                  "values": [
                    {
                      "code": "MEM",
                      "displayValue": "25",
                      "id": "0v6xx0000000001AAA",
                      "isBooleanValue": false,
                      "name": "25Mem",
                      "sequence": 0,
                      "textValue": "25"
                    },
                    {
                      "code": "50MEM",
                      "displayValue": "50",
                      "id": "0v6xx000000001eAAA",
                      "isBooleanValue": false,
                      "name": "50Mem",
                      "sequence": 1,
                      "textValue": "50"
                    },
                    {
                      "code": "100MEM",
                      "displayValue": "100",
                      "id": "0v6xx000000003FAAQ",
                      "isBooleanValue": false,
                      "name": "100Mem",
                      "sequence": 2,
                      "textValue": "100"
                    }
                  ]
                },
                "dataType": "MULTIPICKLIST",
                "defaultValue": "25",
                "id": "0tjxx00000001IfAAI",
                "isCloneable": false,
                "isConfigurable": true,
                "isHidden": false,
                "isPriceImpacting": false,
                "isReadOnly": false,
                "isRequired": true,
                "label": "Memory",
                "name": "Memory"
              }
            ],
            "code": "SPEC",
            "name": "Server Rack Specifications"
          }
        ],
        "description": "Introducing the Cisco Server Rack, a sleek and robust solution designed to streamline your data center infrastructure. With its scalable design and advanced cable management features, it ensures optimal performance, efficiency, and easy maintenance for your critical network equipment.",
        "displayUrl": "https://www.cisco.com/content/dam/en/us/products/servers-unified-computing/ucs-c240-m4-rack-server/product-large.jpg",
        "id": "01txx0000006jkuAAA",
        "isActive": true,
        "isAssetizable": true,
        "isConfigurable": true,
        "isSoldOnlyWithOtherProds": false,
        "name": "Cisco Server Rack NX44",
        "nodeType": "bundleProduct",
        "prices": [],
        "productClassification": {
          "id": "11Bxx000002CC02EAG"
        },
        "productCode": "RACK",
        "productComponentGroups": [
          {
            "classifications": [],
            "code": "SERVICE",
            "components": [
              {
                "additionalFields": [],
                "attributeCategories": [],
                "description": "Introducing the Cisco Rack Server NX44 Service, a comprehensive protection plan designed to safeguard your valuable data infrastructure. With extended coverage and rapid response times, this warranty ensures peace of mind and uninterrupted performance for your critical business operations.",
                "id": "01txx0000006jmWAAQ",
                "isActive": true,
                "isAssetizable": true,
                "isComponentRequired": false,
                "isConfigurable": false,
                "isDefaultComponent": false,
                "isQuantityEditable": false,
                "isSoldOnlyWithOtherProds": false,
                "name": "Cisco Rack Server Service - 1 Year",
                "nodeType": "simpleProduct",
                "prices": [],
                "productClassification": {},
                "productCode": "SERVICE",
                "productComponentGroups": [],
                "productRelatedComponent": {
                  "childProductId": "01txx0000006jmWAAQ",
                  "childSellingModelId": "0jPxx000000004rEAA",
                  "doesBundlePriceIncludeChild": true,
                  "id": "0dSxx000000001dEAA",
                  "isComponentRequired": false,
                  "isDefaultComponent": false,
                  "isQuantityEditable": false,
                  "parentProductId": "01txx0000006jkuAAA",
                  "parentSellingModelId": "0jPxx000000004rEAA",
                  "productComponentGroupId": "0y7xx000000001dAAA",
                  "productRelationshipTypeId": "0yoxx00000001IfAAI",
                  "quantity": 1,
                  "quantityScaleMethod": "Proportional"
                },
                "productSellingModelOptions": [
                  {
                    "id": "0iOxx000000009hEAA",
                    "productId": "01txx0000006jmWAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000004rEAA",
                      "name": "Termed Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "TermDefined",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000004rEAA"
                  },
                  {
                    "id": "0iOxx00000000PpEAI",
                    "productId": "01txx0000006jmWAAQ",
                    "productSellingModel": {
                      "id": "0jPxx0000000085EAA",
                      "name": "Evergreen Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "Evergreen",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx0000000085EAA"
                  }
                ]
              }
            ],
            "description": "The services available for the Cisco Server Rack NX44 product provide comprehensive coverage and support for optimal performance and reliability, ensuring peace of mind for your data center infrastructure.",
            "id": "0y7xx000000001dAAA",
            "maxBundleComponents": 1,
            "minBundleComponents": 0,
            "name": "Services",
            "parentProductId": "01txx0000006jkuAAA",
            "sequence": 1
          },
          {
            "classifications": [],
            "code": "WARRANTY",
            "components": [
              {
                "additionalFields": [],
                "attributeCategories": [],
                "description": "Introducing the Cisco Rack Server NX44 Warranty, a comprehensive protection plan designed to safeguard your valuable data infrastructure. With extended coverage and rapid response times, this warranty ensures peace of mind and uninterrupted performance for your critical business operations.",
                "id": "01txx0000006jjIAAQ",
                "isActive": true,
                "isAssetizable": true,
                "isComponentRequired": false,
                "isConfigurable": false,
                "isDefaultComponent": true,
                "isQuantityEditable": true,
                "isSoldOnlyWithOtherProds": false,
                "name": "Cisco Rack Server Warranty - 1 Year",
                "nodeType": "simpleProduct",
                "prices": [],
                "productClassification": {},
                "productCode": "WARRANTY",
                "productComponentGroups": [],
                "productRelatedComponent": {
                  "childProductId": "01txx0000006jjIAAQ",
                  "childSellingModelId": "0jPxx000000001dEAA",
                  "doesBundlePriceIncludeChild": false,
                  "id": "0dSxx0000000001EAA",
                  "isComponentRequired": false,
                  "isDefaultComponent": true,
                  "isQuantityEditable": true,
                  "maxQuantity": 1,
                  "parentProductId": "01txx0000006jkuAAA",
                  "parentSellingModelId": "0jPxx000000001dEAA",
                  "productComponentGroupId": "0y7xx0000000001AAA",
                  "productRelationshipTypeId": "0yoxx00000001IfAAI",
                  "quantity": 1,
                  "quantityScaleMethod": "Proportional",
                  "sequence": 0
                },
                "productSellingModelOptions": [
                  {
                    "id": "0iOxx000000001dEAA",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000001dEAA",
                      "name": "One Time",
                      "sellingModelType": "OneTime",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000001dEAA"
                  },
                  {
                    "id": "0iOxx00000000HlEAI",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000003FEAQ",
                      "name": "Termed Monthly",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Months",
                      "sellingModelType": "TermDefined",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000003FEAQ"
                  },
                  {
                    "id": "0iOxx00000000JNEAY",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000004rEAA",
                      "name": "Termed Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "TermDefined",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000004rEAA"
                  },
                  {
                    "id": "0iOxx00000000KzEAI",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx0000000085EAA",
                      "name": "Evergreen Annually",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Annual",
                      "sellingModelType": "Evergreen",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx0000000085EAA"
                  },
                  {
                    "id": "0iOxx00000000MbEAI",
                    "productId": "01txx0000006jjIAAQ",
                    "productSellingModel": {
                      "id": "0jPxx000000006TEAQ",
                      "name": "Evergreen Monthly",
                      "pricingTerm": 1,
                      "pricingTermUnit": "Months",
                      "sellingModelType": "Evergreen",
                      "status": "Active"
                    },
                    "productSellingModelId": "0jPxx000000006TEAQ"
                  }
                ]
              }
            ],
            "description": "The warranties available for the Cisco Server Rack NX44 product provide comprehensive coverage and support for optimal performance and reliability, ensuring peace of mind for your data center infrastructure.",
            "id": "0y7xx0000000001AAA",
            "maxBundleComponents": 1,
            "minBundleComponents": 0,
            "name": "Warranties",
            "parentProductId": "01txx0000006jkuAAA",
            "sequence": 0
          }
        ],
        "productSellingModelOptions": [
          {
            "id": "0iOxx000000003FEAQ",
            "productId": "01txx0000006jkuAAA",
            "productSellingModel": {
              "id": "0jPxx000000001dEAA",
              "name": "One Time",
              "sellingModelType": "OneTime",
              "status": "Active"
            },
            "productSellingModelId": "0jPxx000000001dEAA"
          },
          {
            "id": "0iOxx000000004rEAA",
            "productId": "01txx0000006jkuAAA",
            "productSellingModel": {
              "id": "0jPxx000000003FEAQ",
              "name": "Termed Monthly",
              "pricingTerm": 1,
              "pricingTermUnit": "Months",
              "sellingModelType": "TermDefined",
              "status": "Active"
            },
            "productSellingModelId": "0jPxx000000003FEAQ"
          },
          {
            "id": "0iOxx000000006TEAQ",
            "productId": "01txx0000006jkuAAA",
            "productSellingModel": {
              "id": "0jPxx000000004rEAA",
              "name": "Termed Annually",
              "pricingTerm": 1,
              "pricingTermUnit": "Annual",
              "sellingModelType": "TermDefined",
              "status": "Active"
            },
            "productSellingModelId": "0jPxx000000004rEAA"
          }
        ],
        "productType": "Bundle"
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `additional​Fields` | [Configurator Additional Fields](./connect_responses_configurator_additional_fields_output.htm.md "Output representation of the additional fields of a product configuration.")[] | Additional fields for this product. | Small, 60.0 | 60.0 |
| `attribute​Categories` | [Configurator Attribute Category](./connect_responses_configurator_attribute_category_output.htm.md "Output representation of the attribute category in a product configuration.")[] | List of attribute categories. The categories that aren’t categorized are specified in the uncategorized entry in this list. | Small, 60.0 | 60.0 |
| `availability​Date` | String | Availability date of this product. | Small, 60.0 | 60.0 |
| `description` | String | Description of this product. | Small, 60.0 | 60.0 |
| `discontinued​Date` | String | Date when this product is discontinued. | Small, 60.0 | 60.0 |
| `display​Url` | String | Display URL of this product. | Small, 60.0 | 60.0 |
| `endOf​LifeDate` | String | End of life date for this product. | Small, 60.0 | 60.0 |
| `id` | String | ID of the product. | Small, 60.0 | 60.0 |
| `isActive` | Boolean | Indicates whether this product is active (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Assetizable` | Boolean | Indicates whether this product is assetizable (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isComponent​Required` | Boolean | Indicates whether the component is required (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Configurable` | Boolean | Indicates whether the component is configurable (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isDefault​Component` | Boolean | Indicates whether the component is a default component (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isQuantity​Editable` | Boolean | Indicates whether the quantity of the component is editable ( `true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isSoldOnly​WithOtherProds` | Boolean | Indicates whether this product is sold only with other products (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `name` | String | Name of the product. | Small, 60.0 | 60.0 |
| `nodeType` | String | Node type of the product. | Small, 60.0 | 60.0 |
| `prices` | [Configurator Price](./connect_responses_configurator_price_output.htm.md "Output representation of the pricing details in a product configuration.")[] | List of prices from the product catalog. | Small, 60.0 | 60.0 |
| `product​Classification` | [Configurator Product Classification](./connect_responses_configurator_product_classification_output.htm.md "Output representation of the product classification in a product configuration.")[] | Classification details of the product. | Small, 60.0 | 60.0 |
| `productCode` | String | Code of the product. | Small, 60.0 | 60.0 |
| `product​ComponentGroups` | [Configurator Product Component Group](./connect_responses_configurator_product_component_group_output.htm.md "Output representation of the product component group in a product classification.")[] | List of product component groups for this product. | Small, 60.0 | 60.0 |
| `product​RelatedComponent` | [Configurator Product Related Component](./connect_responses_configurator_product_related_component_output.htm.md "Output representation of the product related component in a product configuration.")[] | Details of the product related component of this product. | Small, 60.0 | 60.0 |
| `productSelling​ModelOptions` | [Configurator Product Selling Model Option](./connect_responses_configurator_product_selling_model_option_output.htm.md "Output representation of the product selling model option in a product configuration.")[] | List of product selling model options for this product. | Small, 60.0 | 60.0 |
| `productType` | String | Type of product. | Small, 60.0 | 60.0 |
| `qualification​Context` | [Configurator Qualification Context](./connect_responses_configurator_qualification_context_output.htm.md "Output representation of the qualification context in a product configuration.")[] | Details of the qualification context of the product. | Small, 60.0 | 60.0 |
| `status` | String | Status of the product. | Small, 60.0 | 60.0 |
| `unitOfMeasure` | [Configurator Unit Of Measure](./connect_responses_configurator_unit_of_measure_output.htm.md "Output representation of the details of the unit of measure record.")[] | Details about the unit of measure associated with a product. | Small, 63.0 | 63.0 |
