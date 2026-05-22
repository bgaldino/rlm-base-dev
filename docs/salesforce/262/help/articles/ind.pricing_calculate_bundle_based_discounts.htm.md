---
article_id: ind.pricing_calculate_bundle_based_discounts.htm
title: Calculate Bundle-Based Discounts
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_calculate_bundle_based_discounts.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Calculate Bundle-Based Discounts

Determine the price of a product based on the discounts configured for a set of products sold as a bundle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User

Let's create a scenario where customers who purchase the Laptop Pro bundle along with the Printer Bundle receive a special discount, significantly lowering the cost of the Printer Bundle compared to when it's purchased on its own.

Create a Bundle Based Adjustment Record
Create a bundle based adjustment record.
Specify these details.
Root Bundle: Laptop Pro Bundle
Root Bundle Selling Model: One Time
Parent Product: Laptop Pro Bundle
Parent Product Selling Model: One Time
Product: Printer Bundle
Product Selling Model: One Time
Adjustment Type: Override
Adjustment Value: 20
Effective From: 01-01-2025
Price Adjustment Schedule: Standard Bundle Based Adjustment
Save your changes.
On the Details tab, on the Bundle Based Adjustment page, select Active.
Save your changes.
IMPORTANT We recommend refreshing the Bundle Based Adjustment Entries decision table to ensure that the bundle based adjustment records are available for pricing.
Create a Constant for a Bundle Based Adjustment Variable
Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
On the Pricing Procedure builder canvas, click .
On the Resource Manager panel, click Add Resource.
In the Add New Resource page, specify these details.
Resource Type: Constant
Resource Name: BundleBasedAdjustmentId
Data Type: Text
Default Value: Enter the bundle based adjustment ID from the browser.
You can locate the value of your variable by going to the associated record. For example, to locate a price adjustment schedule ID, open the price adjustment schedule record page. The price adjustment schedule ID is shown in the browser’s URL. 
Save your changes.
Add the Bundle-Based Price Element
Now, add the Pricing Setting element and map these variables.
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
To add the Bundle-Based Price element, search for and add the Bundle Based Adjustment Entries decision table and map these variables.
Input Rule Variables
Price Adjustment Schedule: BundleBasedAdjustmentId
Product Selling Model: ProductSellingModel
Effective From: EffectiveFrom
Effective To: EffectiveFrom
Product: Product
Parent Product: MainItemProduct
Parent Product Selling Model: MainItemProductSellingModel
Root Bundle: RootItemProduct
Root Bundle Selling Model: RootItemProductSellingModel
Input Variables
Quantity: LineItemQuantity
Input Unit Price: ListPrice
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your laptop product and click Simulate again.
The price waterfall shows the bundle-based discounts used to calculate the final price of the printer bundle, confirming that your procedure is working as expected.
