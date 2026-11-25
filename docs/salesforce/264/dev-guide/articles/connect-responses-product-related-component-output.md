---
page_id: connect-responses-product-related-component-output
title: Product Related Component
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-related-component-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_product_related_component_output.htm
fetched_at: 2026-11-25
---

# Product Related Component

Output representation of the product-related component.

## JSON Example

```
"productRelatedComponent": {
      "childProductId": "01tT1000000F0YyIAK",
      "childSellingModelId": "0jPT10000004CAfMAM",
      "doesBundlePriceIncludeChild": true,
      "id": "0dST100000000rgMAA",
      "isComponentRequired": false,
      "isDefaultComponent": false,
      "isExcluded": false,
      "isQuantityEditable": true,
      "maxQuantity": 3,
      "minQuantity": 1,
      "parentProductId": "01tT1000000F0afIAC",
      "parentSellingModelId": "0jPT10000004CAfMAM",
      "productClassificationId": "11BRO00000000222AA",
      "productRelationshipTypeId": "0yoT1000000002WIAQ",
      "quantity": 1,
      "quantityScaleMethod": "Proportional",
      "quoteVisibility": "Quote Document Only",
      "sequence": 1
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `child​Product​Id` | String | Lookup to the child product in the bundle. | Small, 60.0 | 60.0 |
| `child​Selling​ModelId` | String | ID of the child product selling model record. | Small, 60.0 | 60.0 |
| `does​Bundle​PriceInclude​Child` | Boolean | Indicates whether the price of the bundle includes the child product (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `id` | String | ID of the record. | Small, 60.0 | 60.0 |
| `isComponent​Required` | Boolean | Indicates whether the component is required in the bundle (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isDefault​Component` | Boolean | Indicates whether to select the component in the bundle group by default (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isExcluded` | Boolean | Indicates whether the component is excluded in the bundle group (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `is​Quantity​Editable` | Boolean | Indicates whether to allow changes to the quantity of the component in the bundle (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `max​Quantity` | Double | Maximum quantity of the product in the opportunity, quote, or order line item. | Small, 60.0 | 60.0 |
| `min​Quantity` | Double | Minimum quantity of the product in the opportunity, quote, or order line item. | Small, 60.0 | 60.0 |
| `parent​Product​Id` | String | Lookup to the parent product. | Small, 60.0 | 60.0 |
| `parent​Selling​ModelId` | String | ID of the product selling model record. | Small, 60.0 | 60.0 |
| `product​Classification​Id` | String | ID of the product classification record. | Small, 60.0 | 60.0 |
| `productInstance​Reuse` | String | Reserved for future use. | Small, 62.0 | 62.0 |
| `product​Relationship​TypeId` | String | ID of the product relationship type record. | Small, 60.0 | 60.0 |
| `quantity` | Double | Quantity of the child products. | Small, 60.0 | 60.0 |
| `quantity​Scale​Method` | String | Method to scale the quantity of the child product in relation to the quantity of the parent. Valid values are `Constant` or `Proportional`. | Small, 60.0 | 60.0 |
| `quote​Visibility` | String | Specifies whether a quote line item must be shown on the transaction line editor or quote document. Valid values are `Always`, `Transaction Line Editor Only`—Specifies whether to show a quote line item on quote editor only, `Quote Document Only`—Specifies whether to show a quote line item on quote proposal only, or `Never`. The API returns this property only if the CoreCPQ permission set is available. | Small, 64.0 | 64.0 |
| `sequence` | Integer | Order in which the child products are displayed. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-product-related-component-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
