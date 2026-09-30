---
article_id: release-notes.rn_um_new_and_changes_objects.htm
title: New and Changed Objects in Usage Management
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_um_new_and_changes_objects.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_um_usage_management.htm
fetched_at: 2026-09-30
---

# New and Changed Objects in Usage Management

Review the fields that are removed in Usage Management and update your integrations to use the corresponding objects.

REMOVED: The UsageAggregationPolicy, ChargeForOverage, RatingFrequencyPolicy, and DrawdownOrder fields on the existing TransactionUsageEntitlement object are deprecated in API version 65.0 and will be removed in a future version
Instead, use the BindingObjectUsageResourcePolicy object.
REMOVED: The UsageResourceBillingPolicy field on the UsageResource object is removed
Deprecated in API version 65.0, the UsageResourceBillingPolicy field on the UsageResource object is removed in API version 67.0 and later. Instead, use the ProductUsageResourcePolicy or UsageResourcePolicy object.
REMOVED: The UsageResource and Product fields on the RatingFrequencyPolicy object are removed
Deprecated in API version 65.0, the UsageResource and Product fields on the RatingFrequencyPolicy object are removed in API version 67.0 and later. Instead, use the ProductUsageResourcePolicy or UsageResourcePolicy object.
REMOVED: The OverageChargeable field on the ProductUsageGrant object is removed
Deprecated in API version 65.0, the OverageChargeable field on the ProductUsageGrant object is removed in API version 67.0 and later. Instead, use the UsageOveragePolicy object.
