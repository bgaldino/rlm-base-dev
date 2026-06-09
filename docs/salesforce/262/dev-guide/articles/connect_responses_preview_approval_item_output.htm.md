---
page_id: connect_responses_preview_approval_item_output.htm
title: Preview Approval Item
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_preview_approval_item_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Preview Approval Item

Output representation of the details of a specific approval item with an approval
chain.

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
| `additional​Fields` | Map<String, String> | Details of any additional fields in the approval workflow. | Small, 65.0 | 65.0 |
| `approval​ConditionName` | String | Details of the configured conditions in the approval workflow. | Small, 65.0 | 65.0 |
| `assignedTo` | String | Name of the assignee that the approval request is assigned to. | Small, 65.0 | 65.0 |
| `assigneeType` | String | Type of assignee. | Small, 65.0 | 65.0 |
| `assigneeDetails` | Map<String, Object> | Includes the details of an assignee, such as ID, name, type, API name, and email. | Small, 65.0 | 65.0 |
| `dependencies` | String[] | Specifies dependencies among approval steps, which are entry conditions based on the status of a previous step within the same stage. | Small, 65.0 | 65.0 |
| `level` | Integer | Hierarchy level of the approval item. | Small, 65.0 | 65.0 |
| `object​ApiName` | String | API name of the object to preview the approval for. | Small, 65.0 | 65.0 |
| `objectId` | String | ID of the object to preview the approval for. | Small, 65.0 | 65.0 |
| `parents` | String[] | Details of the parent step. | Small, 65.0 | 65.0 |
| `stage` | Map<String, String> | Includes the API name and label. | Small, 65.0 | 65.0 |
| `status` | String | Status of the approval request. | Small, 65.0 | 65.0 |
| `stepApi​Name` | String | API name of the step. | Small, 65.0 | 65.0 |
