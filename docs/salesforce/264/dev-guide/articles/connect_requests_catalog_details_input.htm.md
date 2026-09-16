---
page_id: connect_requests_catalog_details_input.htm
title: Catalog Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_catalog_details_input.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Catalog Details Input

Input representation of the request to get the catalog details.

**JSON example**

: 

```
{
  "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
  "userContext": {
     "accountId": "001xx0000000001AAA",
     "contactId": "003xx00000000D7AAI"
  }
}
```

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 60.0 |
| `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md) | User context details. For example, account ID or contact ID. | Optional | 60.0 |
