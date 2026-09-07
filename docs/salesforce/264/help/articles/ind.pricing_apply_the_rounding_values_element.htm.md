---
article_id: ind.pricing_apply_the_rounding_values_element.htm
title: Use the Rounding Values Element
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_apply_the_rounding_values_element.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_rounding_values.htm
fetched_at: 2026-09-07
---

# Use the Rounding Values Element

Use the Rounding Values element to ensure that the output of any pricing element in a pricing procedure is rounded to the specified decimal place.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User

Let's consider a scenario where you want to set conditions to only give discounts when a customer purchases 50 or more printer bundles, and you're calculating the discounts using a formula. For this example, let's set ItemNetTotalPrice to be rounded down to the first decimal point.

IMPORTANT In a multicurrency organization, the user's personal currency setting determines the currency code used during rounding operations, not the currency code parameter passed in the procedure context.
Create a Constant for the Precision Variable
Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
On the Pricing Procedure builder canvas, click .
On the Resource Manager panel, click Add Resource.
In the Add New Resource page, specify these details.
Resource Type: Constant
Resource Name: PrecisionVariable
Data Type: Number
Decimal Places: 2
Default Value: 1. This value specifies that the product's price should be rounded to one decimal place.
Save your changes.
Add the Rounding Values Element
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
Add the List Group element.
In the list group, configure the List Operation by setting a condition that a 10% discount on the final price of the printers can only be applied if the user purchased over 50 units.
Filter Condition Requirements: All Conditions Are Met (AND)
Resource: # LineItemQuantity
Operator: Greater Than
Value: 50
Within the list container, add the Formula Based Pricing element and specify these variable values.
Calculation Formula: ItemNetTotalPrice - ( ItemNetTotalPrice * 0.10 )
Output Variable: TotalLineAmount
Outside the list container, add the Rounding Values element and specify these variables.
Fixed Input Variables
Precision: PrecisionVariable
Rounding Rules and Variables
Input Variable: ItemNetTotalPrice
Rounding Rule: Round Down.
Output Variable: ItemNetTotalPrice
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your printer bundle product and click Simulate again.
The price waterfall shows the formula used to calculate the total cost of the printer bundles with a discount of 10%. You can also see that the rounded price has been applied to the Net Amount to the first decimal.
