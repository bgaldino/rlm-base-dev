---
article_id: ind.qocal_amend_renew_end_date_important_considerations.htm
title: Changing Subscription End Dates of Termed Assets Considerations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_amend_renew_end_date_important_considerations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Changing Subscription End Dates of Termed Assets Considerations

Understand the requirements and limitations for modifying subscription end dates during amendments and renewals. Familiarizing yourself with these rules helps you accurately lengthen or shorten a subscription's term to meet evolving customer needs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Term Modification Constraints

Review these critical rules before adjusting a subscription end date.

Product Restrictions: You can’t change the end date on subscriptions containing ramp deals or usage-based products.
Transaction Sequence: A term change amendment serves as the final transaction in the chain before an asset expires.
Isolation Requirements: You can’t perform the amendment within other amendments, renewals, or cancellations.
Date Limits: The system prohibits setting an end date that occurs before the start date of the current amendment, renewal, or cancellation quote or order.
Asset Impact: If a quote line item (QLI) or order line item (OLI) has a positive quantity, the term change applies to all end quantity assets.
Action Categorization: Increasing the subscription term counts as an upsell, while decreasing the term counts as a downsell for the asset action category.
