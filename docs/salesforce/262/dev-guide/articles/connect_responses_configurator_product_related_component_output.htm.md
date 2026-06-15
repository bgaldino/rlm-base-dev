---
page_id: connect_responses_configurator_product_related_component_output.htm
title: Configurator Product Related Component
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_product_related_component_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configurator Product Related Component

Output representation of the product related component in a product
configuration.

JSON example
:   ```
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
               "quantityScaleMethod": "Proportional",
               "quoteVisibility": "Quote Document Only"
             }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `child​ProductId` | String | ID of the child product in the bundle. | Small, 60.0 | 60.0 |
| `child​Selling​ModelId` | String | ID of the child product selling model record. | Small, 60.0 | 60.0 |
| `doesBundle​Price​IncludeChild` | Boolean | Indicates whether the price of the bundle includes the child product (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `id` | String | ID of the product related component. | Small, 60.0 | 60.0 |
| `isComponent​Required` | Boolean | Indicates whether the component is required in the bundle (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isDefault​Component` | Boolean | Indicates whether to select the component in the bundle group by default (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `isQuantity​Editable` | Boolean | Indicates whether to allow changes to the quantity of the component in the bundle (`true`) or not (`false`). | Small, 60.0 | 60.0 |
| `max​Quantity` | Double | Maximum quantity of the product in the opportunity, quote, or order line item. | Small, 60.0 | 60.0 |
| `min​Quantity` | Double | Minimum quantity of the product in the opportunity, quote, or order line item. | Small, 60.0 | 60.0 |
| `parent​ProductId` | String | ID of the parent product. | Small, 60.0 | 60.0 |
| `parent​Selling​ModelId` | String | ID of the parent product selling model record. | Small, 60.0 | 60.0 |
| `product​Classification​Id` | String | ID of the product classification record. | Small, 60.0 | 60.0 |
| `product​Component​GroupId` | String | ID of the product component group. | Small, 60.0 | 60.0 |
| `product​Relationship​TypeId` | String | ID of the product relationship type record. | Small, 60.0 | 60.0 |
| `quantity` | Double | Quantity of the child products. | Small, 60.0 | 60.0 |
| `quantity​Scale​Method` | String | Method to scale the quantity of the child product in relation to the quantity of the parent. Valid values are:   - `Constant` - `Proportional` | Small, 60.0 | 60.0 |
| `quote​Visibility` | String | Specifies whether a quote line item must be shown on the transaction line editor or quote document. Valid values are:   - `Always` - `Transaction Line Editor   Only`—Specifies whether to show a quote line item on quote editor   only. - `Quote Document Only`—Specifies   whether to show a quote line item on quote proposal only. - `Never`   The API returns this property only if the CoreCPQ permission set is available. | Small, 64.0 | 64.0 |
| `sequence` | Integer | Order in which the child products are displayed. | Small, 60.0 | 60.0 |
