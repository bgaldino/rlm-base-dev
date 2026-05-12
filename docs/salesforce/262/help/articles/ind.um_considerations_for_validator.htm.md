---
article_id: ind.um_considerations_for_validator.htm
title: Usage Product Validator Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.um_considerations_for_validator.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Usage Product Validator Considerations

The validator checks only the records that are effective and active. Before you use this feature, understand the validation rules, warning thresholds, and the different types of logic that the validator applies.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license
The effectivity validation between the product usage resource and the rate card entry begins from the start date of the product usage resource.
If the time difference between these pairs of records is greater than 12 hours, the validator shows a warning.
Two consecutive product usage resource records for the same usage resource.
Two consecutive rate card entry records associated with a single product usage resource.
Start date of the product usage resource and the start date of the first associated rate card entry.
End date of the product usage resource and the end date of the last associated rate card entry. The validator checks for this gap only if the product usage resource has a defined end date.
NOTE If the usage model type of your product is changed after all the associated objects are created, manually check and update the associated objects before running the validator. If the associated objects aren’t verified, the validator can produce incorrect results.
