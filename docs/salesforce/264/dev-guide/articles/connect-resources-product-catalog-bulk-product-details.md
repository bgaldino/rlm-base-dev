---
page_id: connect-resources-product-catalog-bulk-product-details
title: Bulk Product Details (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-product-catalog-bulk-product-details.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-resources
legacy_page_id: connect_resources_product_catalog_bulk_product_details.htm
fetched_at: 2026-11-25
---

# Bulk Product Details (POST)

Retrieve details for multiple products.

**Resource**

```
/connect/pcm/products/bulk
```

**Resource Example**

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect/pcm/products/bulk
```

**Available Version:** 61.0

**HTTP Methods:** POST

**Request Body for POST**

**JSON Example**

```
{
  "correlationId": "cbfabffb-093f-45b3-8c2d-88b4acbd4867",
  "productIds": [
    "01tT1000000F0afIAC",
    "01tT1000000F0afIAC"
  ],
  "uptoLevel": 1,
  "language": "french",
  "additionalFields": {
    "Product2": {
      "fields": [
        "code__c"
      ]
    },
    "ProductAttributeDefinition": {
      "fields": [
        "scope"
      ]
    }
  }
}
```

This example shows a sample request to fetch data from Enterprise Product Catalog.

```
{
  "productIds": [
    "01tLT000009vGXfYAM"
  ],
  "catalogSystems": [
    "epc"
  ],
  "additionalFields": {
    "AttributeDefinition": {
      "fields": [
        "OptOutAssetization",
        "OptOutDecompositionAction",
        "OptOutSupplementalAction"
      ]
    }
  }
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `additional​Fields` | Map<String, [Additional Fields Input](./connect-requests-product-catalog-additional-fields-input.md)> | Map of object and list of additional standard or custom fields to be included in the response. The supported objects are Product2 and ProductAttributeDefinition. If the fields defined for the ProductAttributeDefinition object aren’t available for the ProductClassificationAttr object, then the API request fails. If the Dynamic Revenue Orchestrator permission is enabled, then this property supports AttributeDefinition as key with these supported values: `OptOutAssetization`, `OptOutDecompositionAction`, or `OptOutSupplementalAction`. | Optional | 61.0 |
| `catalogSystems` | String[] | Name of the catalog system. Valid values are `epc`—Enterprise Product Catalog or `pcm`—Product Catalog Management. Although this property accepts a list, you can pass only one value. If you don’t specify a value, the default behavior is to fetch data from the `pcm` catalog. | Optional | 66.0 |
| `correlation​Id` | String | Unique token to track and associate related events or transactions across different components of the application. If unspecified, a Universally Unique Identifier (UUID) is generated. | Optional | 61.0 |
| `language` | String | Custom language that you can specify to get translated data for the fields of an object that’s enabled for translation. See [Translate Product and Product Category Data](https://help.salesforce.com/s/articleView?id=ind.product_catalog_translate_product2_and_productcategory_data.htm). | Optional | 64.0 |
| `product​Ids` | String[] | List of product IDs that details must be returned for. If any product ID is blank, invalid, or not found, then the request is processed with valid and available product IDs. | Required | 61.0 |
| `upto​Level` | Integer | Hierarchy level to follow to return the product details. For a bundle, this property determines the number of levels of child components to be returned. You can specify up to a hierarchy level of 1. If unspecified, the default level is the full bundle hierarchy. | Optional | 61.0 |

**Response Body for POST:** [Products Output](./connect-responses-products-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-product-catalog-bulk-product-details.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
