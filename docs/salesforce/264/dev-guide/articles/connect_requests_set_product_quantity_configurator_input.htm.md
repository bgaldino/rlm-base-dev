---
page_id: connect_requests_set_product_quantity_configurator_input.htm
title: Product Quantity Set Configurator Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_set_product_quantity_configurator_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Product Quantity Set Configurator Input

Input representation of the request to set the quantity of a product.

**JSON example**

: 

```
{
    "configuratorOptions": {
        "executePricing": true,
        "returnProductCatalogData": true,
        "qualifyAllProductsInTransaction": true,
        "validateProductCatalog": true,
        "validateAmendRenewCancel": true,
        "executeConfigurationRules": true,
        "addDefaultConfiguration": true
    },
    "qualificationContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI"
    },
    "contextId": "008d27d7-e004-4906-a949-ee7d7c323c77",
    "quantity": 20,
    "transactionLinePath": "Quote.QuoteLineItem.Quantity"
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `configurator​Options` | [Configurator Options Input](./connect_requests_configurator_options_input.htm.md) | List of the configuration options to execute. | Optional | 60.0 |
| `context​Id` | String | ID of the context object that’s being considered. | Required | 60.0 |
| `qualification​Context` | [User Context Input](./connect_requests_configurator_user_context_input.htm.md) | Context details that are used for the qualification rules. | Optional | 60.0 |
| `quantity` | Integer | Value of the product quantity. | Required | 60.0 |
| `transaction​Line​Path` | String[] | Path to the line item where the update to the quantity is applied. For example, Quote.QuoteLineItem.Quantity. | Required | 60.0 |
