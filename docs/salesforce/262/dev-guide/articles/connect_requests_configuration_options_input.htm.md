---
page_id: connect_requests_configuration_options_input.htm
title: Configuration Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configuration_options_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Configuration Options Input

Input representation for the configuration options.

JSON example
:   ```
    {
      "configurationOptions": {
        "validateProductCatalog": true,
        "validateAmendRenewCancel": true,
        "executeConfigurationRules": true,
        "addDefaultConfiguration": true
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `addDefault​Configuration` | Boolean | Indicates whether to automatically add default configurations to the order (`true`) or not (`false`). | Optional | 60.0 |
    | `execute​Configuration​Rules` | Boolean | Indicates whether the order must adhere to configuration rules during processing (`true`) or bypass them (`false`). | Optional | 60.0 |
    | `validate​Amend​Renew​Cancel` | Boolean | Indicates whether to run validations related to amend, renew, or cancel processes (`true`) or not (`false`). | Optional | 60.0 |
    | `validate​Product​Catalog` | Boolean | Indicates whether the order must be validated against the product catalog (`true`) or not (`false`). | Optional | 60.0 |
