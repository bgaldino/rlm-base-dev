---
article_id: ind.um_pack_product_drawdowns.htm
title: Pack Product Drawdowns
source_url: https://help.salesforce.com/s/articleView?id=ind.um_pack_product_drawdowns.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Pack Product Drawdowns

Pack products are add-ons purchases that supplement an existing anchor product, such as adding a temporary international roaming pack or extra data.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license

When a pack is added, it doesn’t overwrite the anchor product. Instead, Consumption Management creates a child bucket for the pack's specific grants. This new child bucket accumulates into the same parent bucket as the anchor product. The parent bucket now reflects the combined total of both the anchor and the pack.

In this instance, the parent bucket now has multiple child buckets to choose from. Therefore, Consumption Management uses the Drawdown Order you specified to decide the bucket to deduct the consumption from first.

EXAMPLE A customer determines during an existing plan cycle that their anchor plan's 4,000 text messages are insufficient and purchases a temporary add-on pack for 2,000 additional units. Consumption Management creates a second child bucket for the new grant, linking it to the anchor’s parent bucket with a total aggregated balance of 6,000 units. As the add-on pack is set to expire at the end of the week, the default Expiring First drawdown order ensures that usage is deducted from the 2,000-message pack first.
