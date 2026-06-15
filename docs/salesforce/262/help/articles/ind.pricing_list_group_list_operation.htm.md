---
article_id: ind.pricing_list_group_list_operation.htm
title: List Group and List Operation
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_list_group_list_operation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# List Group and List Operation

Efficiently process lists of data and implement complex pricing logic and calculations by enabling filtering, value lookups, and various computations on line items.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS
NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time

The List Group element serves as a container for processing individual line items within a list variable. It's a fundamental step element in the pricing procedure that facilitates iterating through a list and performing operations on its elements. Every list group must begin with a List Filter, which defines the initial criteria for narrowing down the list. Following the List Filter, a List Group can incorporate multiple calculation and lookup table components to further process the refined list.

The List Filter, as the initial element within a List Group, is solely responsible for filtering items in the input list based on predefined conditions, utilizing list variables to establish these criteria.

Let's consider a scenario where you want to set conditions to only give discounts when a customer purchases 50 or more printer bundles. You can also set a limit to stop price calculations once this condition has been met. If your customer purchases less than 50 printer bundles, it doesn’t meet the condition, then the pricing procedure skips this step altogether.

IMPORTANT Only one list filter can exist within a given list group.
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
Add the List Group element.
In the list group, configure the List Operation by setting a condition that a 10% discount on the final price of the printers can only be applied if the user purchased over 50 units.
Filter Condition Requirements: All Conditions Are Met (AND)
Resource: # LineItemQuantity
Operator: Greater Than
Value: 50
Within the list container, add the Formula Based Pricing element and specify these variable values.
Calculation Formula: ItemNetTotalPrice - ( ItemNetTotalPrice * 0.10 )
Output Variable: TotalLineAmount
To stop pricing, within the list container, and under the Formula Based Pricing element, add the Stop Pricing element.
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your printer bundle product and click Simulate again.
The price waterfall shows the formula used to calculate the total cost of the printer bundles with a discount of 10%. You also see that since the condition of over 50 printer bundles were met, the price calculation stopped, confirming that your procedure is working as expected.
IMPORTANT

We recommend adding another filter condition to your List Group element, specifying that the value of the context tag isn’t a null. When pricing is executed on a quote or an order, if the tag doesn’t have a value or is null, the procedure will return an error.

For example, if you add a filter condition to a line item indicating that the line item’s value is 100, then you must add a condition indicating that the line item’s value is not a null value. Your condition would look like this: {LineItem equals isNotNull} AND {LineItem equals 100}.
