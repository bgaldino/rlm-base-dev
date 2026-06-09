---
page_id: connect_requests_configurator_user_context_input.htm
title: User Context Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_configurator_user_context_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_requests.htm
fetched_at: 2026-06-09
---

# User Context Input

Input representation of the request to get the context details of a user, which are
used for qualification rules.

JSON example
:   ```
        "qualificationContext": {
            "accountId": "001DU000001nHUGYA2",
            "contactId": "003xx00000000D7AAI"
        }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `accountId` | String | ID of the account in a user context. | Optional | 60.0 |
    | `contactId` | String | ID of the contact in a user context. | Optional | 60.0 |
    | `contextId` | String | ID of the context that represents the created session. | Optional | 60.0 |
