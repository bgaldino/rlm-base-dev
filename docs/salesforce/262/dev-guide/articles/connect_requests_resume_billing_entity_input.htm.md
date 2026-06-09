---
page_id: connect_requests_resume_billing_entity_input.htm
title: Resume Billing Object Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_resume_billing_entity_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Resume Billing Object Input

Input representation of the details such as the ID of the account or billing schedule
group along with the effective date. These details are used to start the billing
operation.

JSON example
:   ```
    {
        "referenceIds":
        [
            {
              "referenceId": "001DU000001o2UwYAI",
              "resumeDate": "2024-11-27"
            }
        ]
     
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `referenceId` | String | ID of the account or billing schedule group to resume the billing operation for. | Required | 63.0 |
    | `resumeDate` | String | Date when the billing operation is resumed. If a date isn’t specified, the default value is today’s date. The billing operation starts immediately and any future suspension dates aren’t applicable. | Required | 63.0 |
