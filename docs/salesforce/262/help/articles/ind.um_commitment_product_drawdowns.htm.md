---
article_id: ind.um_commitment_product_drawdowns.htm
title: Commitment Product Drawdowns
source_url: https://help.salesforce.com/s/articleView?id=ind.um_commitment_product_drawdowns.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Commitment Product Drawdowns

In a commitment product, the customer commits to consuming a specific quantity, token amount, or monetary spend in exchange for discounted rates. Commitments are applied by associating the commitment product with an anchor product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license

For commitment-based products, Consumption Management monitors usage relative to the customer’s committed limit rather than deducting consumption from an asset’s wallet balance. Until the customer hasn’t consumed beyond the committed amount, unit, or tokens, the discounted commitment rate applies.

When the customer consumes over the commitment or if the commitment period expires, Consumption Management evaluates the configured policies to determine whether to resume the standard anchor rate, or to keep the discounted rate for the remainder of the billing term.

EXAMPLE A customer purchases a QuantumBit Database anchor product with the standard catalog rate of $10 per GB for DB storage. The customer then commits to consuming 1,000 GB that provides them a 20% discount, lowering the rate to $8 per GB. As DB storage is consumed, Consumption Management performs a drawdown against the 1,000-GB committed limit, rating usage at the discounted $8 price. If usage exceeds 1,000 GB, the resulting overage is billed at either the standard $10 anchor rate or the discounted $8 rate, depending on the defined expiration and commitment policies.
