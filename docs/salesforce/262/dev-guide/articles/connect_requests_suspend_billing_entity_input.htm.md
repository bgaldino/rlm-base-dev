---
page_id: connect_requests_suspend_billing_entity_input.htm
title: Suspend Billing Object Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_suspend_billing_entity_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Suspend Billing Object Input

Input representation of the details such as the ID of the account or billing schedule
group along with the effective dates. These details are used to suspend the billing
operation.

JSON example
:   ```
    {
        "referenceIds": 
        [
            {
                "referenceId": "001DU000001o2UwYAI",
                "suspendDate": "2024-11-27",
                "resumeDate": "2024-12-27"
            }
        ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `referenceId` | String | ID of the account or billing schedule group to suspend the billing operation for. | Required | 63.0 |
    | `resumeDate` | String | Date until when the account or billing schedule group is suspended for billing. | Required | 63.0 |
    | `suspendDate` | String | Date when the account or billing schedule group is suspended for billing. | Required | 63.0 |
