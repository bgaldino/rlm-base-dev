---
page_id: connect_requests_execution_settings_input.htm
title: Execution Settings Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_execution_settings_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Execution Settings Input

Input representation of the execution settings for a ramp deal.

**JSON example**

: 

```
  "executionSettings": {
       "executePricing": true,
       "executeConfigRules": false
   }
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `execute​ConfigRules` | Boolean | Indicates whether to run configuration rules (`true`) or not (`false`). The default value is `true`. | Optional | 62.0 |
| `execute​Pricing` | Boolean | Indicates whether to run pricing request (`true`) or not (`false`). The default value is `true`. | Optional | 62.0 |
