---
page_id: connect_responses_sales_transaction_context_output.htm
title: Sales Transaction Context
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_sales_transaction_context_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Sales Transaction Context

Output representation of the context details that are associated with a sales
transaction.

JSON example
:   ```
    {
      "contextDetails": {
        "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708",
        "isBuiltInTransaction": true
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `contextId` | String | ID of the context that’s created for a session of the sales transaction. | Small, 63.0 | 63.0 |
| `isBuiltIn​Transaction` | Boolean | Indicates whether a new context ID is created for the sales transaction (`true`) or not (`false`). If the `contextId` property isn’t specified, the Place Sales Transaction API generates it. | Small, 63.0 | 63.0 |
