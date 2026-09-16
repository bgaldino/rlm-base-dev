---
article_id: ind.pricing_add_list_price_element.htm
title: Fetch the List Price of a Product
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_add_list_price_element.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_element.htm
fetched_at: 2026-09-07
---

# Fetch the List Price of a Product

To get the base price of a product for pricing procedure execution, use the List Price element. The list price serves as a starting point for calculating the final price before applying any discounts or adjustments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS
NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User

An organization might have different prices for the same product, depending on scenarios such as sales territories or sales cycles. These various list prices for products are tracked as price book entries within a price book.

In a pricing procedure, the list price of a product or line item is fetched from the Price Book Entries decision table. If you are calculating the derived price of a product, fetch the list price from the Price Book Entries V2 decision table.

NOTE If the decision table doesn't return a match for a line item, the List Price element retains the values that preceding elements calculated for output variables, such as List Price and Subtotal. The element doesn't reset these values to zero.

Let's explore using the List Price element in a pricing procedure:

Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
Click to add the Pricing Setting element and map these variables.
Input Variables
Line Item: LineItem
Output Variables
Price Waterfall: price_water_fall
Net Unit Price: NetUnitPrice.
Subtotal: ItemNetTotalPrice
Add the List Price element to fetch the base price of the product.
Under Lookup Table Details, select the Price Book Entries decision table and map these variables.
Input Rule Variables
Product: Product
Price Book: PriceBooks
Product Selling Model: ProductSellingModel
Input Variables
Quantity: LineItemQuantity
Output Variables
List Price: ListPrice
Subtotal: ItemNetTotalPrice
Simulate and activate your pricing procedure.
