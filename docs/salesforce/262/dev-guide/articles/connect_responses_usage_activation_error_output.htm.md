---
page_id: connect_responses_usage_activation_error_output.htm
title: Usage Activation Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_usage_activation_error_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Usage Activation Error

Output representation of a single error encountered while activating a usage product or one of its related records.

JSON example
:   ```
    {
      "productUsageResourceId": "0iUxx0000000678",
      "usageResourceId": "0hUxx000000004",
      "message": "Related Unit of measure records is inactive, activate it first.",
      "objectApiName": "ProductUsageGrant",
      "fieldName": "DefaultUnitofMeasure",
      "recordId": "1BXSM000000404f4AA",
      "recordName": "PUG-000000001"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `fieldName` | String | API name of the field that caused the error. | Big, 67.0 | 67.0 |
| `message` | String | Human-readable description of the error. | Big, 67.0 | 67.0 |
| `object​ApiName` | String | API name of the object on which the error occurred. | Big, 67.0 | 67.0 |
| `productUsage​ResourceId` | String | ID of the ProductUsageResource record that links the product and the usage resource for which the error occurred. | Big, 67.0 | 67.0 |
| `recordId` | String | ID of the record that failed activation. | Big, 67.0 | 67.0 |
| `recordName` | String | Name of the record that failed activation. | Big, 67.0 | 67.0 |
| `usage​ResourceId` | String | ID of the usage resource record from the input request for which the error occurred. | Big, 67.0 | 67.0 |
