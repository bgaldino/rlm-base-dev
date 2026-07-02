---
page_id: connect_resources_resume_billing.htm
title: Resume Billing (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_resume_billing.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Resume Billing (POST)

Resume billing for billing schedule groups or an account that’s
currently on hold.

Resource
:   ```
    /commerce/invoicing/actions/resume-billing
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/actions/resume-billing
    ```

Available version
:   63.0

HTTP methods
:   POST

Request body for POST
:   JSON example
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
        | `referenceIds` | [Resume Billing Object Input](./connect_requests_resume_billing_entity_input.htm.md "Input representation of the details such as the ID of the account or billing schedule group along with the effective date. These details are used to start the billing operation.")[] | Input representation of the account or billing schedule group IDs to resume the billing operation for. | Required | 63.0 |

Response body for POST
:   [Suspend Resume
    Billing](./connect_responses_suspend_resume_billing_output.htm.md "Output representation of the list of accounts and billing schedule groups, which are suspended or resumed for billing operations.")
