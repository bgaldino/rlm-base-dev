---
page_id: connect_responses_products_output.htm
title: Products
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_products_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Products

Output representation of the list of retrieved products.

JSON example
:   ```
    {
      "correlationId": "9b6bc520-3c82-4d6c-a458-47590370681a",
      "facets":[
        {
          "attributeType": "ProductStandard",
          "displayName": "Product Type",
          "displayRank": 1,
          "displayType": "MultiSelect",
          "nameOrId": "Type",
          "values": [
            {
              "displayName": "Simple",
              "nameOrId": "Simple",
              "productCount": 9
            }
          ]
        },
        {
          "attributeType": "ProductStandard",
          "displayName": "Active",
          "displayRank": 2,
          "displayType": "MultiSelect",
          "nameOrId": "IsActive",
          "values": [
            {
              "displayName": "true",
              "nameOrId": "true",
              "productCount": 47
            }
          ]
        }
      ],
      "count": 3,
      "products": [
        {
          "attributeCategory": [],
          "attributes": [],
          "categories": [],
          "childProducts": [],
          "description": "Keep your organization connected with seamless collaboration across distributed teams. No matter where employees are located, organizations are seeking stronger employee engagement and customer experiences to enable more productivity and greater business agility. More effective collaboration helps organizations work smarter.",
          "displayUrl": "https://dispatch.m.io/wp-content/uploads/2023/01/History-of-Webex.png",
          "id": "01t1Q000008CD2eQAG",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "SmartBytes Collaboration Suite",
          "nodeType": "bundleProduct",
          "productClassification": {
            "id": "11B1Q0000008OMGUA2"
          },
          "productCode": "P0143",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iO1Q0000008OkeUAE",
              "productId": "01t1Q000008CD2eQAG",
              "productSellingModel": {
                "id": "0jP1Q000000CaVFUA0",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              }
            }
          ],
          "productSpecificationType": {
            "name": "None"
          }
        },
        {
          "attributeCategory": [],
          "attributes": [],
          "categories": [],
          "childProducts": [],
          "configureDuringSale": "Allowed",
          "displayUrl": "https://www.cisco.com/c/dam/en/us/products/collateral/wireless/small-business-300-series-wireless-access-points/datasheet-c78-732143.doc/_jcr_content/renditions/datasheet-c78-732143_1.jpg",
          "id": "01t1Q000008CD36QAG",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "SmartBytes Repeater",
          "nodeType": "simpleProduct",
          "productClassification": {
            "id": "11B1Q0000008OMMUA2"
          },
          "productCode": "BS_R001",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iO1Q0000008OlsUAE",
              "productId": "01t1Q000008CD36QAG",
              "productSellingModel": {
                "id": "0jP1Q000000CaVFUA0",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              }
            }
          ],
          "productSpecificationType": {
            "name": "COM_Offer"
          }
        },
        {
          "attributeCategory": [],
          "attributes": [],
          "categories": [],
          "childProducts": [],
          "configureDuringSale": "Allowed",
          "description": "A converged data center architecture that integrates computing, networking and storage resources to increase efficiency and enable centralized management. UCS products are designed and configured to work together effectively.",
          "displayUrl": "https://www.cisco.com/c/dam/en/us/products/collateral/servers-unified-computing/ucs-x-series-modular-system/sap-hana-scaleup-appliance-with-xseries-wp.docx/_jcr_content/renditions/sap-hana-scaleup-appliance-with-xseries-wp_3.png",
          "id": "01t1Q000008CD2sQAG",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "SmartBytes Unified Computing System",
          "nodeType": "bundleProduct",
          "productCode": "P0157",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iO1Q0000008OkzUAE",
              "productId": "01t1Q000008CD2sQAG",
              "productSellingModel": {
                "id": "0jP1Q000000CaVFUA0",
                "name": "One Time",
                "sellingModelType": "OneTime",
                "status": "Active"
              }
            },
            {
              "id": "0iO1Q0000008OlWUAU",
              "productId": "01t1Q000008CD2sQAG",
              "productSellingModel": {
                "id": "0jP1Q000000CaVHUA0",
                "name": "Evergreen",
                "pricingTerm": 1,
                "pricingTermUnit": "Months",
                "sellingModelType": "Evergreen",
                "status": "Active"
              }
            }
          ],
          "productSpecificationType": {
            "name": "None"
          }
        }
      ],
      "status": {
        "code": "200",
        "errors": [],
        "message": "Successfully fetched the product records."
      }
    }
    ```

    This example shows a sample response with data from Enterprise Product
    Catalog.

    ```
    {
      "correlationId": "4cf1997d-5d86-4997-9c6b-55842442f325",
      "facets": [],
      "products": [
        {
          "additionalFields": {},
          "attributeCategory": [
            {
              "attributes": [
                {
                  "additionalFields": {
                    "OptOutAssetization": true,
                    "OptOutDecompositionAction": false,
                    "OptOutSupplementalAction": false
                  },
                  "attributeNameOverride": "ATTRIBUTE-ABP-INT",
                  "code": "ABP-INT",
                  "dataType": "Number",
                  "developerName": "ABP-INT",
                  "id": "ABP-INT",
                  "isHidden": false,
                  "isPriceImpacting": false,
                  "isReadOnly": false,
                  "isRequired": false,
                  "name": "ATTRIBUTE-ABP-INT",
                  "sequence": 3,
                  "status": "Active"
                },
                {
                  "additionalFields": {
                    "OptOutAssetization": false,
                    "OptOutDecompositionAction": false,
                    "OptOutSupplementalAction": false
                  },
                  "attributeNameOverride": "ATTRIBUTE-ABP-CHECKBOX",
                  "code": "ABP-CHECKBOX",
                  "dataType": "Checkbox",
                  "developerName": "ABP-CHECKBOX",
                  "id": "ABP-CHECKBOX",
                  "isHidden": false,
                  "isPriceImpacting": false,
                  "isReadOnly": false,
                  "isRequired": false,
                  "name": "ATTRIBUTE-ABP-CHECKBOX",
                  "sequence": 2,
                  "status": "Active"
                }
              ],
              "code": "CATEGORY-ABP",
              "id": "a0Zxx000000c3tNEAQ",
              "name": "ATTRIBUTE_CATEGORY-ABP"
            }
          ],
          "attributes": [],
          "catalogs": [],
          "categories": [],
          "childProducts": [],
          "id": "01txx0000006kFYAAY",
          "isActive": true,
          "isAssetizable": true,
          "name": "ARProduct",
          "nodeType": "simpleProduct",
          "productCode": "ARProduct",
          "productComponentGroups": [],
          "productSellingModelOptions": [],
          "productUnitOfMeasures": []
        }
      ],
      "status": {
        "code": "200",
        "errors": [],
        "message": "Successfully fetched Product records."
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Small, 60.0 | 60.0 |
| `count` | Integer | Total count of the products matching the request query. | Small, 60.0 | 60.0 |
| `facets` | [Search Facet](./connect_responses_search_facet_output.htm.md "Output representation of the details of the faceted search.") | Details of the faceted search. This property is applicable if the **Use Indexed Data For Product Listing and Search** toggle from the Product Discovery Settings page from Setup is enabled. | Small, 63.0 | 63.0 |
| `products` | [Product](./connect_responses_product_output.htm.md "Output representation of the product definition.")[] | List of products matching the request query. | Small, 60.0 | 60.0 |
| `status` | [Status](./connect_responses_status.htm.md "Output representation of the status of the request.") | Status of the request. | Small, 60.0 | 60.0 |
