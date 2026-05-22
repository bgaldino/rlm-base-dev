---
article_id: ind.qocal_anchor_with_quantity_commit.htm
title: Anchor Product with Quantity Commitments
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_anchor_with_quantity_commit.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Anchor Product with Quantity Commitments

In a quantity commitment, the customer agrees to consume a specific number of units for a specific resource, for example, 100 GB of storage or 10,000 API calls.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

Customer purchases a commitment product that grants a fixed bucket of units at a lower price per unit.

If the customer consumes more than the committed quantity, the excess usage is charged as overage. For example, if a customer uses 110 GB when they commit to 100 GB. Depending on the configuration, the overage is billed at the standard anchor rate or a special commitment rate.

The commitment acts as a bucket. To make sure that usage draws from the committed bucket first, associate the anchor product that tracks the actual usage with this commitment.

EXAMPLE

Anchor Product—QuantumBit Database

Standard Rate—$1.00 per compute API call

Commitment Offer—if the customer agrees to the Monthly Compute Saver commitment, where they’re committing to 100 compute API calls per month, they get a $50 flat fee. The commitment rate gives them a discount of $0.50 per call.

If the customer uses calls beyond the committed quantity, the original rate of $1 per call applies. For example, if the customer uses 120 calls, they pay $70. For the first 100 calls, they pay $50 and $20 for the 20 overage calls at the standard$1.00 rate.
