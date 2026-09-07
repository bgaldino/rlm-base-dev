---
article_id: ind.pricing_use_the_discount_spread_service_element.htm
title: Use the Discount Distribution Service Element
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_use_the_discount_spread_service_element.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_discount_spread_service.htm
fetched_at: 2026-09-07
---

# Use the Discount Distribution Service Element

To calculate discounts that can be spread evenly across all line items or specifically across a subsection of line items, use the Discount Distribution Service element.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To create pricing procedures:	Salesforce Pricing Design Time

Let’s look at a scenario where we are applying a $300 discount equally across a laptop and a printer on their net unit price.

NOTE To configure header adjustments that apply discounts to an entire quote or order using the Discount Distribution Service element, see Header Adjustments Overview.
Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
Click to add the Pricing Setting element and map these variables.
Input Variables
Line Item: LineItem
Output Variables
Price Waterfall: price_water_fall
Net Unit Price: NetUnitPrice.
Subtotal: ItemNetTotalPrice
Remember, Discount Distribution Service doesn't support derived products on quote line items, so don't map your Is Derived variable.
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
Add the Discount Distribution Service element.
IMPORTANT You can only add the Rounding Values and Aggregate Price element after the Discount Distribution Service element in a pricing procedure.
Select the line items that must be eligible for a discount. In our example, we aren't selecting any because we want all input line items in the quote to be considered for calculation.
If you've selected either of the options, this is how the procedure would read the information.
Lookup Table	

Discounts are distributed across all line items based on the decision table you select to retrieve data from.


Define participating conditions	

Discounts are applied to quotes based on the conditions you set. For example, you could set a condition to apply discounts to quotes where the product category is Electronics and the product's Net Unit Price doesn't exceed $150.

Map these variables.
Input Variables
Header Discount Type: HeaderDiscountType
Header Discount Value: HeaderDiscountValue
Header Distribution Logic: HeaderDistributionLogic
Header Distribution Type: HeaderDistributionType
List Price: ListPrice
Quantity: LineItemQuantity
Line Item: Lineitem
Input Unit Price: ListPrice
Minimum Net Unit Price: MinimumNetUnitPrice
Output Variables
Discount Value: LineItemDiscountValue
Distribution Type: LineItemDistributionType
Discount Type: LineItemDiscountType
Net Unit Price: NetUnitPrice
Subtotal: ItemNetTotalPrice
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure.
Specify the input values for a laptop and printer along with the header discount details which is a $300 discount that must be equally or proportionally applied across all line items.
Test your input values by specifying the discount distribution logic as Equals and click Simulate again.
Now, change your input values by specifying the discount distribution logic as Proportionate and click Simulate again.

Now, let's use the same scenario to learn how floor limits are set and how you can store the remainder amount for future use. Go back to the Discount Distribution Service element and select Set floor price limit. Here, under the Floor Price Limit section, select Store remainder amount and map the TotalRemainderAmount tag to the Total Remainder Amount variable.

Let's simulate this scenario. In your input value, change the HeaderDiscountValue as $900 instead of $300.

Upon simulation, since we've provided floor prices (the Minimum Net Unit Price) for the printer and laptop, after applying discounts equally across the products, you'll see a remainder amount after the system honors their floor prices. This remainder amount value is then written back to the TotalRemainderAmount tag.
