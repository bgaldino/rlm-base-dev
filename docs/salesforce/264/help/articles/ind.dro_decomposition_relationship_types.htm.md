---
article_id: ind.dro_decomposition_relationship_types.htm
title: Decomposition Relationship Types
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_decomposition_relationship_types.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator_concepts_and_references.htm
fetched_at: 2026-09-05
---

# Decomposition Relationship Types

Dynamic Revenue Orchestrator (DRO) supports one-to-one, one-to-many, many-to-one, and many-to-many decomposition relationships.

REQUIRED EDITIONS
Available in: Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions

Use a one-to-many relationship to fulfill a commercial product as several technical products. Use a many-to-one relationship to consolidate several commercial products into one technical product.

Set the decomposition scope on the technical product to control how often the fulfillment line item is created.

You can also pick a different technical product based on an attribute value. See Define Execution Rules for a Decomposition Rule.

One-to-One Decomposition

A commercial product maps to exactly one technical product. This link is defined by a decomposition rule, which ensures the commercial product decomposes into that specific technical product.

For example, the QuantumBit Database commercial product decomposes to a Database Provisioning technical product.

Use the Order Line Item decomposition scope so that each commercial product line item produces its own technical product.

One-to-Many Decomposition

A one-to-many relationship decomposes a single commercial product into multiple technical products. Create a separate decomposition rule from the commercial product to each technical product.

For example, the QuantumBit Complete commercial product decomposes to three technical products on the same order:

Order Processing
Provisioning and Activation
Shipping for the PowerSwerve R750 server

You can define an execution rule to base the technical product based on an attribute value. For example, the PowerSwerve R750 decomposes to a 1 TB NLSAS drive when the Storage Tier attribute is Standard, or to an 8 TB NLSAS drive when it's Premium.

Many-to-One Decomposition

A many-to-one relationship consolidates multiple commercial products into a single technical product. Create a decomposition rule from each commercial product to the same technical product.

For example, several QuantumBit hardware products on an order need shipping, but you want only one shipping request.

To get one line item per order, map each product to the technical product, and set its decomposition scope to Order.
To decompose multiple commercial products of the same bundle into one technical product, set the decomposition scope to Bundle.
To decompose commercial products across the account, independent of the bundle, into a single technical product, set the decomposition scope to Account.
Many-to-Many Decomposition

A many-to-many relationship maps multiple commercial products to multiple technical products. It combines one-to-many fan-out with many-to-one consolidation: author a decomposition rule for each commercial product and technical product pair that you need.

For example, the QuantumBit Complete and PowerSwerve R750 commercial products both decompose to the Order Processing and Provisioning and Activation technical products. Set the Decomposition Scope on each technical product to control how the matching commercial products are consolidated.

The relationship type you configure while designing the decomposition defines the possible decomposition. The decomposition result depends on the commercial products present on that specific order and on whether the conditions on the decomposition rules qualify. For example, a many-to-one consolidation occurs only when multiple qualifying commercial products are actually on the same order.
