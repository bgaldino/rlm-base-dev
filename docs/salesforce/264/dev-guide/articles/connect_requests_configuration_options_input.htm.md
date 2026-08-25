---
page_id: connect_requests_configuration_options_input.htm
title: Configuration Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configuration_options_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configuration Options Input

Input representation for the configuration options.

**JSON example**

: 

```
{
  "configurationOptions": {
    "validateProductCatalog": true,
    "validateAmendRenewCancel": true,
    "executeConfigurationRules": true,
    "addDefaultConfiguration": true
  }
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `addDefault​Configuration` | Boolean | Indicates whether to automatically add default configurations to the order (`true`) or not (`false`). | Optional | 60.0 |
| `execute​Configuration​Rules` | Boolean | Indicates whether the order must adhere to configuration rules during processing (`true`) or bypass them (`false`). | Optional | 60.0 |
| `validate​Amend​Renew​Cancel` | Boolean | Indicates whether to run validations related to amend, renew, or cancel processes (`true`) or not (`false`). | Optional | 60.0 |
| `validate​Product​Catalog` | Boolean | Indicates whether the order must be validated against the product catalog (`true`) or not (`false`). | Optional | 60.0 |
