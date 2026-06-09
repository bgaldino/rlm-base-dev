---
page_id: connect_responses_cpq_base_bulk_details_output.htm
title: Bulk Product Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_cpq_base_bulk_details_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_responses.htm
fetched_at: 2026-06-09
---

# Bulk Product Details

Output representation of the response that contains the details of multiple
products.

JSON example
:   ```
    {
      "apiStatus": {
        "messages": [],
        "statusCode": "FetchedDetailsSuccessfully"
      },
      "contextId": "c68c7c7e85f3ea5b0e7bcfefc0f2dba9bbd24bfe2f4240ca589af50e473e2242",
      "correlationId": "de9a674c-1807-438c-ac78-2c96f4655325",
      "result": [
        {
          "additionalFields": [],
          "attributeCategories": [],
          "attributes": [],
          "catalogs": [],
          "childProducts": [],
          "id": "01txx0000006ivJAAQ",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "iPhone12",
          "nodeType": "simpleProduct",
          "prices": [
            {
              "currencyIsoCode": "USD",
              "isDefault": false,
              "isSelected": true,
              "price": 100,
              "priceBookEntryId": "01uxx0000008zUkAAI",
              "priceBookId": "01sxx0000005qxxAAA",
              "pricingModel": {
                "id": "0jPxx000000009hEAA",
                "name": "OneTime",
                "pricingModelType": "OneTime"
              }
            },
            {
              "currencyIsoCode": "USD",
              "isDefault": true,
              "isSelected": false,
              "price": 15,
              "priceBookEntryId": "01uxx0000008zUmAAI",
              "priceBookId": "01sxx0000005qxxAAA",
              "pricingModel": {
                "frequency": "Months",
                "id": "0jPxx000000009iEAA",
                "name": "Monthly",
                "occurrence": 1,
                "pricingModelType": "TermDefined"
              }
            }
          ],
          "productClassification": {},
          "productCode": "iPhone12",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iOxx00000000EfEAI",
              "productId": "01txx0000006ivJAAQ",
              "productSellingModel": {
                "id": "0jPxx000000009iEAA",
                "name": "Monthly",
                "pricingTerm": 1,
                "pricingTermUnit": "Months",
                "sellingModelType": "TermDefined",
                "status": "Active"
              },
              "productSellingModelId": "0jPxx000000009iEAA"
            },
            {
              "id": "0iOxx00000000EgEAI",
              "productId": "01txx0000006ivJAAQ",
              "productSellingModel": {
                "id": "0jPxx000000009hEAA",
                "name": "OneTime",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPxx000000009hEAA"
            }
          ],
          "productSpecificationType": {
            "name": "ProdSpecRecType1",
            "productSpecificationRecordType": {}
          },
          "qualificationContext": {
            "isQualified": true
          }
        },
        {
          "additionalFields": [],
          "attributeCategories": [],
          "attributes": [],
          "catalogs": [],
          "childProducts": [],
          "id": "01txx0000006ivLAAQ",
          "isActive": true,
          "isAssetizable": true,
          "isSoldOnlyWithOtherProds": false,
          "name": "iPhone13",
          "nodeType": "simpleProduct",
          "prices": [
            {
              "currencyIsoCode": "USD",
              "isDefault": true,
              "isSelected": false,
              "price": 1520,
              "priceBookEntryId": "01uxx0000008zUpAAI",
              "priceBookId": "01sxx0000005qxxAAA",
              "pricingModel": {
                "id": "0jPxx000000009hEAA",
                "name": "OneTime",
                "pricingModelType": "OneTime"
              }
            },
            {
              "currencyIsoCode": "USD",
              "isDefault": false,
              "isSelected": false,
              "price": 152,
              "priceBookEntryId": "01uxx0000008zUqAAI",
              "priceBookId": "01sxx0000005qxxAAA",
              "pricingModel": {
                "frequency": "Months",
                "id": "0jPxx000000009iEAA",
                "name": "Monthly",
                "occurrence": 1,
                "pricingModelType": "TermDefined"
              }
            }
          ],
          "productClassification": {},
          "productCode": "iPhone13",
          "productComponentGroups": [],
          "productSellingModelOptions": [
            {
              "id": "0iOxx00000000EbEAI",
              "productId": "01txx0000006ivLAAQ",
              "productSellingModel": {
                "id": "0jPxx000000009iEAA",
                "name": "Monthly",
                "pricingTerm": 1,
                "pricingTermUnit": "Months",
                "sellingModelType": "TermDefined",
                "status": "Active"
              },
              "productSellingModelId": "0jPxx000000009iEAA"
            },
            {
              "id": "0iOxx00000000EeEAI",
              "productId": "01txx0000006ivLAAQ",
              "productSellingModel": {
                "id": "0jPxx000000009hEAA",
                "name": "OneTime",
                "sellingModelType": "OneTime",
                "status": "Active"
              },
              "productSellingModelId": "0jPxx000000009hEAA"
            }
          ],
          "productSpecificationType": {
            "name": "ProdSpecRecType1",
            "productSpecificationRecordType": {}
          },
          "qualificationContext": {
            "isQualified": true
          }
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `api​Status` | [API Status](./connect_responses_api_status_output.htm.md "Output representation of the API status.")[] | Status of the API request. | Small, 61.0 | 61.0 |
| `context​Id` | String | ID of the context. | Small, 61.0 | 61.0 |
| `correlation​Id` | String | Unique identifier of the request. | Small, 61.0 | 61.0 |
| `result` | Any response body | Result that contains the details of products. | Small, 61.0 | 61.0 |
| `user​Context` | [User Context](./connect_responses_user_context_output.htm.md "Output representation of the user context details.")[] | User context details. For example, account ID or contact ID. | Small, 61.0 | 61.0 |
