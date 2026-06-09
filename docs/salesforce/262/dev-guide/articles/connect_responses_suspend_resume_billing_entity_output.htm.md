---
page_id: connect_responses_suspend_resume_billing_entity_output.htm
title: Suspend Resume Billing Object
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_suspend_resume_billing_entity_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Suspend Resume Billing Object

Output representation of the details of accounts and billing schedule groups, which are
suspended or resumed for billing operations, along with the status of the API
request.

JSON example
:   ```
    {
        "result":{
            {
            "referenceId": "1",
            "isSuccess": true,
            "errorcode": null,
            "errorMessage":null
            }
        }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode` | String | Code indicating the type of error. | Big, 63.0 | 63.0 |
| `errorMessage` | String | Message stating the reason for the error, if any. | Big, 63.0 | 63.0 |
| `isSuccess` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Big, 63.0 | 63.0 |
| `referenceId` | String | ID of the account or billing schedule group that the suspend or resume billing request is initiated for. | Big, 63.0 | 63.0 |
