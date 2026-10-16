---
article_id: ind.pricing_ensure_price_transparency_using_the_price_tracking_element.htm
title: Ensure Price Transparency Using the Price Tracking Element
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_ensure_price_transparency_using_the_price_tracking_element.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_price_tracking_actions.htm
fetched_at: 2026-09-07
---

# Ensure Price Transparency Using the Price Tracking Element

Verify if your product prices are tracked, monitored, and captured using the Price Tracking element.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User

Let's consider a scenario where an e-commerce channel wants to fetch the LaptopPro Bundle’s tracked maximum price from a transaction. You can use the Price Tracking element to fetch the tracked maximum price for the LaptopPro Bundle along with its price book, product selling model, and currency combination. This can then be displayed or used in evaluations.

Configure a pricing procedure.
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
Add the Manual Discount element and map these variables.
Adjustment Type: AdjustmentType
Adjustment Value: AdjustmentValue
Quantity: LineItemQuantity
Input Unit Price: NetUnitPrice
Add the Price Tracking element.
Under Lookup Table Details, select the Price Book Entries V2 decision table and specify the following details.
Select Get as the Action Type.
Map these input rule variables.
Price Book: PriceBooks
Product: Product
Product Selling Model: ProductSellingModel
Map these output variables.
Saved Min Recorded Price: ItemRecordedPrice
Saved Max Recorded Price: ItemMaxRecordedPrice_std
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your laptop product and click Simulate again.
The price waterfall shows the manual discounts used to calculate the final price of the laptops. However to track the saved recorded price is visible in the JSON format only. 

When a pricing procedure runs or is simulated, every result is saved in the Product Price History Log entity. For each pricing calculation, if the new price is higher than the previously stored maximum price for maximum price tracking, the existing entry in the Product Price History Log entity for that specific product, product selling model, and price book combination is overwritten. This ensures that at the end of each day, only the highest price for a given product and its combination is recorded in the Product Price History Log entity.

The Product Price Range entity then stores this maximum price for a specified duration, specifically for a product, product selling model, and price book combination. This table is the primary source used when fetching price history using the Get or Get & Save actions within the system.
