---
page_id: connect_responses_preview_approval_chain_item_output.htm
title: Preview Approval Chain Item
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_preview_approval_chain_item_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Preview Approval Chain Item

Output representation of the details of an approval chain item for a specific
group.

JSON example
:   ```
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
| `approval​Items` | [Preview Approval Item](./connect_responses_preview_approval_item_output.htm.md "Output representation of the details of a specific approval item with an approval chain.")[] | Details of the approval items. | Small, 65.0 | 65.0 |
