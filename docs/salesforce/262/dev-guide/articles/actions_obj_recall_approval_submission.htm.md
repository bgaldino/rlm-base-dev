---
page_id: actions_obj_recall_approval_submission.htm
title: Recall Approval Submission Action
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/actions_obj_recall_approval_submission.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_invocable_actions_parent.htm
fetched_at: 2026-06-09
---

# Recall Approval Submission Action

Recall an approval submission that isn't completed. You can also add
comments that the submitter or approval admin made the recall.

This action also validates if a user has required permissions to recall an approval
submission. Keep these considerations in mind when you use this invocable
action.

- The user must have the Approval Admin user permission.
- The user must also be a submitter of this approval submission.
- The status of the approval submission must be in `In
  progress` or `Suspended`
  status.

This action is available in API version 62.0 and later.

## Supported REST HTTP Methods

URI
:   `/services/data/v67.0/actions/standard/recallApprovalSubmission`

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
| approvalSubmissionId | Type  string  Description  Required.  ID of the approval submission to be recalled. |
| comments | Type  string  Description  Comments entered by the approval admin or approval submitter about why they recalled the approval submission. |

## Outputs

None.

## Example

POST
:   Here's a sample request for the Recall Approval Submission action.

    ```
    {
      "inputs": [
        {
          "approvalSubmissionId": "9iPxx00000001lhEBA",
          "comments": "Recall comments."
        }
      ]
    }
    ```
:   Here's a sample response for the Recall Approval Submission action.

    ```
    {
      "actionName": "recallApprovalSubmission",
      "errors": null,
      "invocationId": null,
      "isSuccess": true,
      "outcome": null,
      "outputValues": null,
      "sortOrder": -1,
      "version": 1
    }
    ```
