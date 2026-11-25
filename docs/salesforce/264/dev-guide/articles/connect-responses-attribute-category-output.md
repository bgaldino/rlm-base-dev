---
page_id: connect-responses-attribute-category-output
title: Attribute Category
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-attribute-category-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_attribute_category_output.htm
fetched_at: 2026-11-25
---

# Attribute Category

Output representation of the attribute category.

## JSON Example

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
          "name": "build and make",
          "sequence": 1
    }
]
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `attributes` | [Attribute Definition](./connect-responses-attribute-definition-output.md)[] | List of categorized attributes associated with the product | Small, 60.0 | 60.0 |
| `code` | String | Code of the attribute category | Small, 60.0 | 60.0 |
| `id` | String | ID associated with the attribute category | Small, 60.0 | 60.0 |
| `name` | String | Name of the attribute category. If data translation is set up and specified in the org, the translated description is available. | Small, 60.0 | 60.0 |
| `sequence` | Integer | Display order of the attribute category in a product’s details | Small, 68.0 | 68.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-attribute-category-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
