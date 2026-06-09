---
page_id: actions_obj_process_consumption_overages.htm
title: Process Consumption Overages Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_process_consumption_overages.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Process Consumption Overages Action

Process consumption overages for the usage summary records with
`SummaryComplete` status. This action uses the
entitlement service to process the overages.

This action is available in API version 63.0 and later.

## Special Access Rules

The Process Consumption Overages action is available in Enterprise, Developer,
and Unlimited Editions where Usage Management is enabled. To use this action, you
need the Usage Management Run Time User permission.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/processConsumptionOverages`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization: Bearer
    token`

## Inputs

| Input | Details |
| --- | --- |
| usageRatableSummaryId | Type  string  Description  Required.  ID of the usage ratable summary record that contains the consumption details, and is used to calculate consumption overages and create usage entitlement entry records. |

## Outputs

None.

## Example

POST
:   This example shows a sample request for the Process Consumption Overages
    action.

    ```
    {
      "inputs": [
        {
          "usageRatableSummaryId": "3ttDU00000000iZYAQ"
        }
      ]
    }
    ```

    This example shows a sample response for the Process Consumption Overages
    action.

    ```
    {
      "actionName": "processConsumptionOverages",
      "errors": null,
      "isSuccess": true
    }
    ```

#### See Also

- [*Salesforce Help*: Permission Set Licenses, Personas, and User Permissions for
  Usage Management](https://help.salesforce.com/s/articleView?id=ind.um_usage_management_psls_and_personas.htm&language=en_US "Salesforce Help: Permission Set Licenses, Personas, and User Permissions for
         Usage Management - HTML (New Window)")
