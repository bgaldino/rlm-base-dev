---
page_id: connect_responses_product_classification_details_collection_output.htm
title: Product Classification Details Collection
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_product_classification_details_collection_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_catalog_management_api_responses.htm
fetched_at: 2026-06-09
---

# Product Classification Details Collection

Output representation that contains a collection of product classification details along
with any processing errors.

JSON example
:   ```
    {
      "success": false,
      "errors": [
        {
          "errorCode": "INSUFFICIENT_ACCESS",
          "message": "Insufficient access rights on cross-reference ID"
        }
      ],
      "productClassifications": [
        {
          "id": "dummyId",
          "name": "Dummy Product Classification",
          "code": "DUMMY_CODE",
          "attributeCategories": [
            {
              "attributes": [
                {
                  "attributeNameOverride": "Dummy_Attribute__c",
                  "code": "ATTR_CODE_1",
                  "dataType": "String",
                  "defaultValue": "default",
                  "description": "A dummy attribute for demonstration.",
                  "developerName": "Dummy_Attribute",
                  "displayType": "Text",
                  "helpText": "Help text for dummy attribute",
                  "id": "attrId1",
                  "isConfigurable": true,
                  "isHidden": false,
                  "isPriceImpacting": false,
                  "isReadOnly": false,
                  "isRequired": false,
                  "isValueCloneable": true,
                  "label": "Dummy Attribute Label",
                  "maximumCharacterCount": 100,
                  "maximumValue": "100",
                  "minimumCharacterCount": 1,
                  "minimumValue": "1",
                  "name": "Dummy Attribute",
                  "sequence": 1,
                  "status": "Active",
                  "stepValue": "1"
                }
              ],
              "code": "GENERAL",
              "id": "catId1",
              "name": "General"
            }
          ],
          "attributes": [
            {
              "attributeNameOverride": "Dummy_Attribute__c",
              "code": "ATTR_CODE_1",
              "dataType": "String",
              "defaultValue": "default",
              "description": "A dummy attribute for demonstration.",
              "developerName": "Dummy_Attribute",
              "displayType": "Text",
              "helpText": "Help text for dummy attribute",
              "id": "attrId1",
              "isConfigurable": true,
              "isHidden": false,
              "isPriceImpacting": false,
              "isReadOnly": false,
              "isRequired": false,
              "isValueCloneable": true,
              "label": "Dummy Attribute Label",
              "maximumCharacterCount": 100,
              "maximumValue": "100",
              "minimumCharacterCount": 1,
              "minimumValue": "1",
              "name": "Dummy Attribute",
              "sequence": 1,
              "status": "Active",
              "stepValue": "1"
            }
          ]
        }
      ]
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Product Catalog Management Error](./connect_responses_p_c_m_error_output.htm.md "Output representation that contains error details, including error codes and messages.")[] | List of errors encountered during the processing of the API request. | Small, 66.0 | 66.0 |
| `productClassifications` | [Product Classification Details](./connect_responses_product_classification_details_output.htm.md "Output representation that contains the details of a single product classification, including its attributes and categories.")[] | List of product classification detail records that match the requested product classification IDs. | Small, 66.0 | 66.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or has failed (`false`). | Small, 66.0 | 66.0 |
