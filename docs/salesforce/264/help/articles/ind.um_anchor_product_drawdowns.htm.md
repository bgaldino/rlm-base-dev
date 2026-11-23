---
article_id: ind.um_anchor_product_drawdowns.htm
title: Anchor Product Drawdowns
source_url: https://help.salesforce.com/s/articleView?id=ind.um_anchor_product_drawdowns.htm&type=5&release=264
release: 264
release_name: Winter '27
area: usage
parent_article: ind.um_buckets_and_drawdowns.htm
fetched_at: 2026-11-23
---

# Anchor Product Drawdowns

An anchor product is the base purchase, such as a basic mobile plan that offers 4,000 text messages. When this anchor product is sold, the initial entitlement of 4,000 text messages is granted and is placed into a child bucket.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license

This child bucket is linked to a parent bucket, which serves as an overarching wallet showing the total balance of that resource across the account. When text messages are consumed, Consumption Management deducts the consumed units directly from the anchor's child bucket.

EXAMPLE When a customer purchases a Basic Mobile Plan anchor product that offers 4,000 text messages, the initial entitlement of 4,000 units is granted and placed into a child bucket. As text messages are consumed during the billing cycle, Consumption Management performs a drawdown to deduct the consumed units directly from this child bucket.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.um_anchor_product_drawdowns.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
