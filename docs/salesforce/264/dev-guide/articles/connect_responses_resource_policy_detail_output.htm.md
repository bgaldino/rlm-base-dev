---
page_id: connect_responses_resource_policy_detail_output.htm
title: Resource Policy Detail
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_resource_policy_detail_output.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_responses.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Resource Policy Detail

Output representation of the details of a usage resource policy.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the usage resource policy. | Big, 65.0 | 65.0 |
| `ratingFrequency​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md) | Details of the rating frequency policy. | Big, 65.0 | 65.0 |
| `usageAggregation​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md) | Details of the usage aggregation policy. | Big, 65.0 | 65.0 |
| `usageCommitment​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md) | Details of the usage commitment policy. | Big, 65.0 | 65.0 |
| `usageOverage​Policy` | [Policy Detail](./connect_responses_policy_detail_output.htm.md) | Details of the usage overage policy. | Big, 65.0 | 65.0 |
