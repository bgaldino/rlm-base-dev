---
page_id: connect_requests_user_context_input.htm
title: User Context Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_user_context_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# User Context Input

Input representation of the details with the user context.

**JSON example**

: 

```

    "userContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI",
        "contextId": "e055bb18-d4e8-41c3-881e-0132b9561708"
    }
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `account​Id` | String | ID of the account in a user context. | Optional | 60.0 |
| `contact​Id` | String | ID of the contact in a user context. | Optional | 60.0 |
| `context​Id` | String | ID of the context that represents the created session. | Optional | 60.0 |
