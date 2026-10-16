---
page_id: connect_requests_preview_approval_input.htm
title: Preview Approval Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_preview_approval_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Advanced Approvals
parent_page: advanced_approvals_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Preview Approval Input

Input representation of the details of the request to preview an approval.

**JSON example**

: 

```
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

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `flowApiName` | String | API name of the auto-launched flow. | Required | 65.0 |
| `objectApiName` | String | API name of the object to preview the approvals for. | Required | 65.0 |
| `recordId` | String | ID of the record to preview the approvals for. | Required | 65.0 |
| `inputParameters` | Map<String, Object> | List of input parameters to preview. | Optional | 67.0 |
