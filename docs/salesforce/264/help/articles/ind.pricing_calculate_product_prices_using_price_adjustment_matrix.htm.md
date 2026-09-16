---
article_id: ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm
title: Calculate Product Prices Using Price Adjustment Matrix
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_calculate_product_prices_using_price_adjustment_matrix.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_add_the_price_adjustment_matrix_element.htm
fetched_at: 2026-09-07
---

# Calculate Product Prices Using Price Adjustment Matrix

Let's look at a scenario where we want to apply custom percentage-based discounts using the Price Adjustment Matrix element.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User
Create a Custom Decision Table
From the App Launcher, search for and select Lookup Tables .
Select Decision Table.
Specify these details.
Enter a name and then press Tab to autopopulate the API Name. For our example, we’re calling the decision table, Price Adjustment Matrix Entries.
Select Pricing as the application usage.
Select Advanced as the decision table type.
Click Save & Next.
Specify these decision table details.
Source Object: Price Adjustment Tier.
Set the following condition.
Set the source object field as Name and the operator as Equals.
Set another condition for the ID.
Set the source object field as Id and the operator as Equals.
Ensure that the Condition Type is set to All conditions are met (AND).
Specify the result details.
Source Object Field: TierValue.
Column Name: TierValue.
Source Object Field: AdjustmentType.
Column Name: AdjustmentType.
Click Save & Next.
Click Save & Next again.
Click Finish.
Activate your decision table.
Map the Variables in Your Custom Decision Table
From Setup, in the Quick Find box, find and select Pricing Recipes.
Choose the pricing recipe that you want to modify. For our example, select NGPDefaultRecipe.
On the Price Adjustment Matrix tab, click Modify.
Select the custom decision table created by you. Here, select Price Adjustment Matrix Entries.
Map the following variables.
AdjustmentValue: TierValue
AdjustmentType: AdjustmentType
When creating price adjustment tier records with AdjustmentType = Percentage, enter the percentage as a whole number. For example, enter 10 for a 10% discount (not 0.10 or 10%).
Save your changes.
Use the Price Adjustment Matrix Element
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
Add the Price Adjustment Matrix element.
The input rule variables shown below are specific to this example. Your variables will differ based on the source objects you selected in your custom decision table and the conditions and results you configured.
Under Lookup Table Details, select the Price Adjustment Matrix Entries decision table and map these variables.
Input Rule Variables
Product: Product
Price Book: PriceBooks
Product Selling Model: ProductSellingModel
Input Variables
Quantity: LineItemQuantity
Input Unit Price: ListPrice
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your product and click Simulate again.
