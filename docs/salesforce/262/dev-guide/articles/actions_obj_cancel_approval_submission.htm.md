---
page_id: actions_obj_cancel_approval_submission.htm
title: Cancel Approval Submission Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_cancel_approval_submission.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Cancel Approval Submission Action

Cancels an approval submission and all child approval work items
that haven't been completed. You can also add comments about why the approval admin made
the cancellation.

This action also validates if a user has required permissions to cancel an approval submission.
Keep these considerations in mind when you use this invocable action.

- The user must have the Approval Admin user permission.
- The status of the approval submission must be in `In
  progress` or `Suspended`
  status.

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/cancelApprovalSubmission`

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
| approvalSubmissionId | Type  string  Description  Required.  ID of the Approval Submission to be canceled. |
| comments | Type  string  Description  Comments entered by the approval admin about why they canceled the Approval Submission. |

## Outputs

None.

## Example

POST
:   Here's a sample request for the Cancel Approval Submission action.

    ```
    {
      "inputs": [
        {
          "approvalSubmissionId": "9iPxx00000001lhEBA",
          "comments": "Cancellation comments."
        }
      ]
    }
    ```
:   Here's a sample response for the Cancel Approval Submission action.

    ```
    {
      "actionName": "cancelApprovalSubmission",
      "errors": null,
      "invocationId": null,
      "isSuccess": true,
      "outcome": null,
      "outputValues": null,
      "sortOrder": -1,
      "version": 1
    }
    ```
