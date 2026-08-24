---
page_id: connect_requests_resume_billing_input.htm
title: Resume Billing Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_resume_billing_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Resume Billing Input

Input representation of the details of the request to resume the billing operation for an
    account or a billing schedule group.

**JSON example**

: 

```
{
    "referenceIds":
    [
        {
          "referenceId": "001DU000001o2UwYAI",
          "resumeDate": "2024-11-27"
        }
    ]
 
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `referenceIds` | [Resume Billing Object Input](./connect_requests_resume_billing_entity_input.htm.md)[] | Input representation of the account or billing schedule group IDs to resume the billing operation for. | Required | 63.0 |
