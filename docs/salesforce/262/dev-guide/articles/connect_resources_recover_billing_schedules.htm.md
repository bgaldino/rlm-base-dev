---
page_id: connect_resources_recover_billing_schedules.htm
title: Billing Schedule Recovery List (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_recover_billing_schedules.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Billing Schedule Recovery List (POST)

Recover the latest generated invoice associated with the billing
schedules in the `Error` or `Processing` status.

Billing schedules include critical details such as the amount to be billed, next billing date,
and status. An invoice can be associated with one or more billing schedules. When an invoice
is generated or posted, the billing schedules are updated to reflect the accurate state of
the invoice. The billing schedules associated with an invoice are marked in the `Error` status if any of the invoicing processes have errors.
Use this API to recover the invoice associated with the billing schedules in the `Error` or `Processing`
status.

Special Access Rules
:   You need the Manage Errors Using Invoice Error Recovery API permission set to use this
    API.

Resource
:   ```
    /commerce/invoicing/billing-schedules/collection/actions/recover
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/billing-schedules/collection/actions/recover
    ```

Available version
:   62.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
          {
            "billingScheduleIds": ["44bDU00000000XXYAY"]
          }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `billing​Schedule​Ids` | String[] | IDs of the billing schedules to recover the invoice for. You can recover one billing schedule per API request. | Required | 62.0 |

Response body for POST
:   [Billing Schedule
    Recovery List](./connect_responses_billing_schedule_recovery_list_output.htm.md "Output representation of the recovered details of the billing schedules and associated invoice.")
