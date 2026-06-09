---
page_id: connect_resources_create_billing_schedules.htm
title: Create Billing Schedules for Orders (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_billing_schedules.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Create Billing Schedules for Orders (POST)

Generate billing schedules for orders by using context
service.

Special Access Rules
:   The org must have the standard billing context definition with the target mapping.
    This context definition is available in orgs with Billing enabled. Additionally, you
    need the Create Billing Schedules From Billing Transactions API permission set and the
    Context Service Runtime permission set to use this API.

    See these [requirements](https://help.salesforce.com/s/articleView?id=ind.billing_schedules_create.htm&language=en_US "HTML (New Window)") to learn
    more about the configuration prerequisites.

Resource
:   ```
    /commerce/invoicing/billing-schedules/actions/create
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/billing-schedules/actions/create
    ```

Available version
:   62.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
            "billingTransactionIds": [ "801xx000003H1H9AAK"]
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `billing​Transaction​Ids` | String[] | ID of the billing transaction. This property value is the ID of the order if the source of the billing request is for the Order object.  If the order product associated with the specified order ID doesn't have an associated billing treatment ID, the API considers the default billing treatment ID. The generated billing schedule group has the default billing treatment ID.  The API supports only one billing transaction ID in the input. | Required | 62.0 |

Response body for POST
:   [Context-Aware Billing
    Schedule](./connect_responses_context_aware_billing_schedule_output.htm.md "Output representation of the context-aware billing schedule.")
