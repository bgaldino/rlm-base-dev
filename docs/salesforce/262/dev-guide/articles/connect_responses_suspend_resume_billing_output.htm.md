---
page_id: connect_responses_suspend_resume_billing_output.htm
title: Suspend Resume Billing
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_suspend_resume_billing_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Suspend Resume Billing

Output representation of the list of accounts and billing schedule groups, which are
suspended or resumed for billing operations.

JSON example
:   ```
    {
        "result":{
            {
                "referenceId": "001DU000001o2UwYAI",
                "success": true,
                "errorcode": null,
                "errorMessage":null
            },
            {
                "referenceId": "001DU000001o2UuYAI",
                "success": false,
                "errorcode": "INVALID_API_INPUT",
                "errorMessage":"Billing is already suspended for 9Wsxx000000006TCAQ."
            }
        }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `result` | [Suspend Resume Billing Object](./connect_responses_suspend_resume_billing_entity_output.htm.md "Output representation of the details of accounts and billing schedule groups, which are suspended or resumed for billing operations, along with the status of the API request.")[] | Details of the accounts or billing schedule groups that the suspend or resume billing request is initiated for. | Big, 63.0 | 63.0 |
