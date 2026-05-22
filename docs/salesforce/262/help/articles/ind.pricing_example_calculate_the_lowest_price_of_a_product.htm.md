---
article_id: ind.pricing_example_calculate_the_lowest_price_of_a_product.htm
title: "Example: Calculate the Lowest Price of a Product"
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_example_calculate_the_lowest_price_of_a_product.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Example: Calculate the Lowest Price of a Product

Let’s determine the lowest price of a product using the List Price element.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create pricing procedures:	Salesforce Pricing Design Time
Create a Procedure Output Resolution Record
From the App Launcher, find and select Price Management.
From the app navigation menu, select Procedure Output Resolution.
Click New.
Specify these details.
Name: BestPrice
Pricing Element: List Price
Resolution Formula: MIN(ListPrice)
Activate your procedure output resolution record.
Save your changes.
Create a Constant for a Resolution Strategy
Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
On the Pricing Procedure builder canvas, click .
On the Resource Manager panel, click Add Resource.
In the Add New Resource page, specify these details.
Resource Type: Constant
Resource Name: ResolutionStrategyMinPrice
Data Type: Text
Default Value: BestPrice. This is the procedure output resolution record that you created in the step above.
Save your changes.
Use the List Price Element to Calculate the Lowest Price
Add the Pricing Setting element and map these variables.
Input Variables
Line Item: LineItem
Output Variables
Price Waterfall: price_water_fall
Net Unit Price: NetUnitPrice.
Subtotal: ItemNetTotalPrice
Add the List Price element to fetch the base price of the product.
Under Lookup Table Details, select the Price Book Entries V2 decision table
Select Enable Output Resolution.
Map these variables.
Input Rule Variables
Product: Product
Price Book: PriceBooks
Product Selling Model: ProductSellingModel
Input Variables
Quantity: LineItemQuantity
Output Variables
List Price: ListPrice
Subtotal: ItemNetTotalPrice
Resolution Variables
Resolution Strategy: ResolutionStrategyMinPrice
Use As List: Price Book
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your laptop product and click Simulate again.
The price waterfall shows that the pricing engine has looked through all the available price books in the org and found the best (minimum) price for the Laptop product, confirming that your procedure is working as expected.
