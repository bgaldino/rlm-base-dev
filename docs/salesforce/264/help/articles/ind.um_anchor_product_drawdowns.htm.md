---
article_id: ind.um_anchor_product_drawdowns.htm
title: Anchor Product Drawdowns
source_url: https://help.salesforce.com/s/articleView?id=ind.um_anchor_product_drawdowns.htm&type=5&release=264
release: 264
release_name: Winter '27
area: usage
parent_article: ind.um_buckets_and_drawdowns.htm
fetched_at: 2026-09-07
---

# Anchor Product Drawdowns

An anchor product is the base purchase, such as a basic mobile plan that offers 4,000 text messages. When this anchor product is sold, the initial entitlement of 4,000 text messages is granted and is placed into a child bucket.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license

This child bucket is linked to a parent bucket, which serves as an overarching wallet showing the total balance of that resource across the account. When text messages are consumed, Consumption Management deducts the consumed units directly from the anchor's child bucket.

EXAMPLE When a customer purchases a Basic Mobile Plan anchor product that offers 4,000 text messages, the initial entitlement of 4,000 units is granted and placed into a child bucket. As text messages are consumed during the billing cycle, Consumption Management performs a drawdown to deduct the consumed units directly from this child bucket.
