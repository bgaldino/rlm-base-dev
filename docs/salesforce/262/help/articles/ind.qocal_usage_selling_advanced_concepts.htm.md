---
article_id: ind.qocal_usage_selling_advanced_concepts.htm
title: Usage Selling Advanced Concepts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_usage_selling_advanced_concepts.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Usage Selling Advanced Concepts

Determine the scope of resource pooling with grant binding, and manage resource consumption and rating using anchors and packs. You can also define drawdown logic, rate applicability rules, and discounted commitment models.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Grant Binding
Grant binding determines how the grants of resources contained in an asset are pooled and consumed. In simpler terms, the binding decides whether a purchased service (like 1,000 text messages) is related to a single asset or shared across a wider group, such as an organization or a specific contract.
Anchor Product with Packs
An anchor product represents the primary usage-based product, such as QuantumBit Database Service. A pack is an add-on product that provides additional quantities of resources or offers different rates for the resources, such as a top-up or booster pack. For a pack to function as a top-up for the anchor, you must either bind the pack to an anchor or bind both the anchor and the pack to the same binding target, such as the same account.
Anchor Product with Token Commitments
A token acts as a virtual currency, such as Flex credits or Salesforce credits. In the token-commitment model, your user purchases a quantity of tokens that has a standard conversion rate to a dollar for each service, such as SMS and data.
Anchor Product with Quantity Commitments
In a quantity commitment, the customer agrees to consume a specific number of units for a specific resource, for example, 100 GB of storage or 10,000 API calls.
Anchor Product with Monetary Commitments
In a monetary commitment, your customer agrees to spend a specific dollar amount, for example, $1,000 per month. Monetary commitment products are used when your customer wants a discount on the overall spend and doesn’t want the discount to be tied to a specific resource type, such as SMS or storage.
Saving Usage Rates for Quotes and Orders
Automatically save current usage rates by generating rate card entries when you save a quote or order. This process helps maintain rate consistency for the duration of the sale, even if the product catalog is updated later.
