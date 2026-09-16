---
page_id: connect_requests_config_rule_options_input.htm
title: Configuration Rule Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_config_rule_options_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: connect_requests_config_rule_input.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Configuration Rule Options Input

Input representation of the details of the configuration rule options.

**JSON example**

: 

```
{
  "ruleOptions": {
    "isUpdateContextRequired": false
  }
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `isUpdateContextRequired` | Boolean | Indicates whether context update is required with the capability to automatically add or delete a product and its components (`true`) or not (`false`). If Place Sales Transaction API is invoked with configuration enabled, set this property to `false` to avoid any redundant execution of context logic. | Optional | 67.0 |
