---
page_id: connect_resources_preview_approvals.htm
title: Preview Approval (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_preview_approvals.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_business_apis_rest_references.htm
fetched_at: 2026-06-09
---

# Preview Approval (POST)

Preview the approval levels of a record and associated level details,
approval chains, approvers, and conditions before you submit the record for an
approval.

For example, a sales rep working on a quote can preview the approval levels for a
quote before submitting the quote for approval.

Resource
:   ```
    /connect/advanced-approvals/approval-submission/preview
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/connect/advanced-approvals/approval-submission/preview
    ```

Available version
:   65.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "flowApiName": "QuoteApprovals",
          "objectApiName": "Quote",
          "recordId": "0Q0DU0000005HZC0A2",
          "inputParameters": {
            "approverComments": "Submitted for approval",
            "requestType": "Standard"
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `flowApiName` | String | API name of the auto-launched flow. | Required | 65.0 |
        | `objectApiName` | String | API name of the object to preview the approvals for. | Required | 65.0 |
        | `recordId` | String | ID of the record to preview the approvals for. | Required | 65.0 |
        | `inputParameters` | Map<String, Object> | List of input parameters to preview. | Optional | 67.0 |

Response body for POST
:   [Preview
    Approval](./connect_responses_preview_approval_output.htm.md "Output representation of the details of a preview approval request.")
