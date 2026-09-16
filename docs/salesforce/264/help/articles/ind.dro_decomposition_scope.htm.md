---
article_id: ind.dro_decomposition_scope.htm
title: Decomposition Scope
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_decomposition_scope.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_technical_product_in_dro.htm
fetched_at: 2026-09-05
---

# Decomposition Scope

Set the decomposition scope to limit how many instances of a fulfillment order line item appear in fulfillment.

When you create a product, choose from one of these decomposition scopes in the Decomposition Scope field.

Order Line Item
For every order line item that decomposes to the fulfillment order line item, one instance of the fulfillment order line item is created. This scope is the default if you don't select a scope.
Order
A single instance of the fulfillment order line item is created per order. When the scope is set to Order, the fulfillment order line item cannot be assetized.
Bundle
A single instance of the fulfillment order line item is created per bundle within an order.
Account
A single instance of the fulfillment order line item is created across orders from the same account.
Custom
A single instance of the fulfillment order line item is created per scope identifier. See Create Custom Fulfillment Scope Configuration.

Here's an example of Decomposition Scope in action:

Let's say that there's a technical product called Shipping Service. There are lots of commercial products that decompose to Shipping Service, because lots of products require shipping. However, you don't want to fulfill each of those Shipping Service products individually for the same order.

To handle this situation, set the scope of the Shipping Service product to Order. That way, only one instance of the Shipping Service product is created for every order, no matter how many products in the order call for shipping.

WARNING

When you create a bundle, don't make the child product's scope broader than the parent's scope. For example, if the parent's scope is Order Line Item, then don't set the child's scope to Account. From broad to narrow, the scope is Account, Order, Bundle, Order Line Item.
