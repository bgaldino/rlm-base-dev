---
page_id: connect_requests_consumption_traceabilities_input.htm
title: Consumption Traceabilities Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_consumption_traceabilities_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Consumption Traceabilities Input

Input representation of the details of the liable summary IDs that are used to trace the
consumption.

JSON example
:   ```
    {
      "liableSummaryIds": [
        "1HG000000000001"
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `liableSummaryIds` | String[] | List of liable summary IDs to trace the consumption. | Required | 66.0 |
