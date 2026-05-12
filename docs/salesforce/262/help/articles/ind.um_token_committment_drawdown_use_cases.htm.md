---
article_id: ind.um_token_committment_drawdown_use_cases.htm
title: Token Commitment Drawdown Use Cases
source_url: https://help.salesforce.com/s/articleView?id=ind.um_token_committment_drawdown_use_cases.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Token Commitment Drawdown Use Cases

The relationship between commitments and anchors, and how their consumption is processed varies depending on the binding target and the number of active products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
One Commit to One Anchor

A customer has a token commitment bound directly to an anchor product.

If the commitment is active and unexhausted, the consumption process draws directly from the committed tokens.
If the commitment is active but exhausted, the consumption process applies the rate available for the anchor product or the commit rate, as specified in the commitment policy.
One Commitment to Multiple Anchors

A customer buys a token commitment product and binds it to an account. The account has multiple assets (Asset A, Asset B, and Asset C) pooling their usage.

If the commitment is active and unexhausted, the consumption process draws directly from the committed tokens. However, because multiple assets are associated with the same product, they’re sorted in ascending order by their Asset Billing End Date.
If the commitment is active but exhausted, the consumption process applies the rate available for the anchor product or the commit rate, as specified in the commitment policy.
If there’s a conflict between end dates, the asset with the highest resource rate draws down first to minimize the overall cost of overages.
