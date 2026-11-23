---
page_id: connect_responses_pricing_recipe_post_output.htm
title: Pricing Recipe Post
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_post_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Salesforce Pricing
parent_page: pricing_api_responses.htm
fetched_at: 2026-11-23
---

# Pricing Recipe Post

Output representation of the pricing recipe after the API request.

## JSON Example

```
{
isSuccess : true 
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error` | [Pricing Error Response](./connect_responses_pricing_error_response.htm.md "Output representation of the pricing error response.") | Details from the pricing error response. | Small, 60.0 | 60.0 |
| `isSuccess` | Boolean | Indicates whether the response was calculated successfully (`true`) or not (`false`). | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_pricing_recipe_post_output.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
