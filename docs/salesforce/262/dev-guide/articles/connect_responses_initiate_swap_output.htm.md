---
page_id: connect_responses_initiate_swap_output.htm
title: Initiate Swap Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_initiate_swap_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Initiate Swap Response

Output representation of the request to initiate a swap action.

JSON example
:   ```
    {
      "salesTransactionId": "0Q09Q000005IkEPSA0"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `salesTransactionId` | String | ID of the sales transaction that’s created by the swap action. | Small, 66.0 | 66.0 |
