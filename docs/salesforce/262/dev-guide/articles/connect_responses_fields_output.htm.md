---
page_id: connect_responses_fields_output.htm
title: Fields Response
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_fields_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Fields Response

Output representation of the details of the optional fields on the usage-based
selling-related objects.

JSON Example
:   ```
      "fields": {
        "MyCustomDate__c": {
          "displayValue": "2024-09-24",
          "value": "2024-09-24T17:46:30.662Z"
        },
        "MyCustomNumber__c": {
          "displayValue": "20.0",
          "value": 20
        }
      }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `display​Value` | String | Display value of a field. | Big, 63.0 | 63.0 |
| `value` | Object | Value of a field in its original data form. | Big, 63.0 | 63.0 |
