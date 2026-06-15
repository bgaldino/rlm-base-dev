---
page_id: actions_obj_blng_send_dunning_email.htm
title: Send Dunning Email Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_blng_send_dunning_email.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Send Dunning Email Action

Run an orchestration that sends dunning
process emails for collection plans to recover overdue revenue and notify customers
about amounts still due.

Specify the collection plan for the dunning emails. Optionally, specify the email
template by name or by ID. The action triggers an orchestration that sends dunning
process emails for a collection plan based on your configured timeline.

This action is available in API version 67.0 and later.

## Special Access Rules

The Send Dunning Email action is available in Enterprise, Unlimited, and
Developer Editions of Revenue Cloud.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/blngSendDunningEmail`

Formats
:   JSON, XML

HTTP Methods
:   POST

Authentication
:   `Authorization:
    Bearertoken`

## Inputs

| Input | Details |
| --- | --- |
| collection​PlanId | Type  string  Description  Required. ID of the collection plan record for dunning emails. |
| emailTemplate​NameOrId | Type  string  Description  Email template name or ID to use for the reminder email. If not specified, the default email template is used. |

## Outputs

| Output | Details |
| --- | --- |
| isDunning​EmailSent | Type  boolean  Description  Indicates whether the dunning email related to the collection plan was sent (`true`) or not (`false`). |
| additional​Information | Type  string  Description  Additional information to be passed on with the response. |

## Example

POST
:   This sample request is for the Send Dunning Email action.

    ```
    {
      "inputs": [
        {
          "collectionPlanId": "0PLxxxxxxxxxxxxxxx",
          "emailTemplateNameOrId": "Dunning_Reminder_Template"
        }
      ]
    }
    ```
:   This sample response is for the Send Dunning Email action.

    ```
    [
      {
        "actionName": "blngSendDunningEmail",
        "errors": null,
        "invocationId": null,
        "isSuccess": true,
        "outcome": null,
        "outputValues": {
          "isDunningEmailSent": true,
          "additionalInformation": null
        },
        "sortOrder": -1,
        "version": 1
      }
    ]
    ```
