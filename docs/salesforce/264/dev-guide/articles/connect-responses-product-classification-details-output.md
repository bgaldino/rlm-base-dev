---
page_id: connect-responses-product-classification-details-output
title: Product Classification Details
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-classification-details-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_product_classification_details_output.htm
fetched_at: 2026-11-25
---

# Product Classification Details

Output representation that contains the details of a single product classification, including its attributes and categories.

## JSON Example

```
{
  "id": "dummyId",
  "name": "Dummy Product Classification",
  "code": "DUMMY_CODE",
  "attributeCategories": [{
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
        }],
  "attributes": [{
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
        }]
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributeCategories` | [Product Classification Attribute Category](./connect-responses-attribute-category-output.md)[] | List of attribute categories applicable to the product classification. | Small, 66.0 | 66.0 |
| `attributes` | [Product Classification Attribute Definition](./connect-responses-attribute-definition-output.md)[] | List of uncategorized attributes applicable to the product classification. | Small, 66.0 | 66.0 |
| `code` | String | Code of the product classification. | Small, 66.0 | 66.0 |
| `id` | String | ID of the product classification. | Small, 66.0 | 66.0 |
| `name` | String | Name of the product classification. | Small, 66.0 | 66.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-classification-details-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
