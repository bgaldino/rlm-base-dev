---
page_id: connect-responses-preview-approval-chain-item-output
title: Preview Approval Chain Item
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-preview-approval-chain-item-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Advanced Approvals
parent_page: advanced-approvals-api-responses
legacy_page_id: connect_responses_preview_approval_chain_item_output.htm
fetched_at: 2026-11-25
---

# Preview Approval Chain Item

Output representation of the details of an approval chain item for a specific group.

## JSON Example

```
{
  "approvalChainItems": [
    {
      "approvalChainName": "FINANCE",
      "approvalItems": [
        {
          "stepApiName": "CPIFC",
          "approvalConditionName": "Payment Term Greater Than 90 Days",
          "assignedTo": "005XX000001ABCQYA4",
          "assigneeType": "User",
          "assigneeDetails": {
            "id": "005XX000001ABCQYA4",
            "name": "Sam Smith",
            "type": "User",
            "apiName": "",
            "email": "sam.smith@example.com"
          },
          "objectId": "0Q0bsOgSBEhlexWC3Q",
          "objectApiName": "Quote",
          "status": "Approved",
          "stage": {
            "apiName": "stage101",
            "label": "Stage 101"
          },
          "dependencies": [],
          "parents": [],
          "level": 1,
          "additionalFields": {
            "reviewedBy": "005CVxhW4MBIUbPYUX",
            "isEligibleForSmartApproval": true,
            "smartApprovalBasisWI": "000000000000000",
            "isAutoReviewed": false
          }
        },
        {
          "stepApiName": "CPIFC2",
          "approvalConditionName": "Payment Term Greater Than 90 Days",
          "assignedTo": "00GXX000001XYZA2A4",
          "assigneeType": "Group",
          "assigneeDetails": {
            "id": "00GXX000001XYZA2A4",
            "name": "Admin Group",
            "type": "Group",
            "apiName": "Admin_Group",
            "email": "admin.group@example.com"
          },
          "objectId": "0Q0bsOgSBEhlexWC3Q",
          "objectApiName": "Quote",
          "status": "In Progress",
          "stage": {
            "apiName": "stage101",
            "label": "Stage 101"
          },
          "dependencies": [
            "CPIFC"
          ],
          "parents": [
            "CPIFC"
          ],
          "level": 2,
          "additionalFields": {
            "reviewedBy": "00GvUUtUVGmTDUHU34",
            "isEligibleForSmartApproval": true,
            "smartApprovalBasisWI": "000000000000000",
            "isAutoReviewed": false
          }
        }
      ]
    }
  ],
  "flowOrchestrationDefinitionVersionId": "0jEDU0000001nZm",
  "status": "Success"
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `approvalChain​Name` | String | Name of the approval chain. | Small, 65.0 | 65.0 |
| `approval​Items` | [Preview Approval Item](./connect-responses-preview-approval-item-output.md)[] | Details of the approval items. | Small, 65.0 | 65.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-preview-approval-chain-item-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
