---
article_id: ind.pricing_considerations_for_migrating_attribute_based_adjustments.htm
title: Considerations for Migrating Attribute-Based Adjustments
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_considerations_for_migrating_attribute_based_adjustments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Considerations for Migrating Attribute-Based Adjustments

To prevent hash mismatch issues when you migrate attribute-based adjustment records across Salesforce orgs, follow this process.

Always deploy records in the following order:

Attribute Based Adjustment Rules
Attribute Adjustment Conditions
Attribute Based Adjustments

Migration and batching guidance

When migrating records by using Data Loader or APIs, move all Attribute Adjustment Condition records for the same parent Attribute Based Adjustment Rule in one batch.
Do not split child condition records for the same parent rule across parallel batches. Parallel insertion can produce hash conflicts and can prevent adjustments from being applied.
If you use bulk processing, keep parent-child dependencies intact and preserve sequence. Child records must be inserted after their parent records.

Validation guidance

There is no single automated validation that checks all migrated records at once. Validate migrated records in the Pricing Operations Console before completing deployment.

Troubleshooting

In some cases, adjustments do not apply after migration even when record configuration appears correct and the decision table is refreshed. This can happen when there's a hash mismatch. To troubleshoot and resolve a hash mismatch:

Compare the hash generated in Revenue Cloud Ops Console and the hash value of the Attribute Adjustment Conditions record. If the hashes don't match, the records are out of sync.
To fix the mismatch, open any affected Attribute Adjustment Condition record and save it without making any changes. Saving the record regenerates the parent hash.

After saving, run a validation transaction to confirm the adjustment is applied as expected.
