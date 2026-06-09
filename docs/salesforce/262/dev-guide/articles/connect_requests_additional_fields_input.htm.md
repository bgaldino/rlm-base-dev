---
page_id: connect_requests_additional_fields_input.htm
title: Additional Fields Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_additional_fields_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-06-09
---

# Additional Fields Input

Input representation of the additional standard or custom fields to include in the
response.

JSON example
:   ```
      "additionalFields" : {
        "Product2" : {
        "fields" : ["CustomField1__c","StandardField1"]
    }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `fields` | String[] | List of additional standard or custom fields to include in the response. | Optional | 61.0 |
