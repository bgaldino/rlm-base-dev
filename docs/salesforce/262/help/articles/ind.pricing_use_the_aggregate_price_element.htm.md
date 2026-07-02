---
article_id: ind.pricing_use_the_aggregate_price_element.htm
title: Use the Aggregate Price Element
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_use_the_aggregate_price_element.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Use the Aggregate Price Element

Aggregate and show the price of a group of products based on product categories, product types, or other groups of line items.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time
IMPORTANT When using the Aggregate Price element, be careful not to create pricing loops by incorrectly mapping values in your pricing procedure. For instance, a circular dependency forms when the Net Unit Price is set by Input Unit Price, but then Input Unit Price is changed by an aggregate element that also relies on Net Unit Price. This creates a never-ending loop where Net Unit Price keeps updating, preventing it from settling on a final value and causing performance problems or wrong calculations.

Let's look at a scenario where we group products by their category. We'll add three products: laptops, printers, and Quip software. Laptops and printers will be assigned to the Electronics category, while Quip's category will be Software. Using this data, we'll calculate the aggregate price for each product category.

NOTE
In the Aggregate Price element, the Output and GroupBy tags must belong to the same hierarchical level within the context.
When you use the Aggregate Price element to calculate an average for the Currency data type, the average value can have up to 16 decimal places.
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
Add the Aggregate Price element and specify these variable values.
Group By: ProductCategory
The Group By field sets your grouping criteria by searching for the criteria according to which the aggregation is performed.
Formula: SUM (ItemNetTotalPrice)
This is the aggregation formula used to calculate the pricing.
Output Variable: ItemGroupSummarySubtotal
The output variable contains the context tag that stores the output derived from the aggregation formula. 
To override the pricing output of a variable use the Write Back condition.
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your products and click Simulate again.
Aggregate pricing changes can't be viewed in the waterfall view. However, the JSON output provides insight into how the aggregate prices were calculated based on the product category. Based on our example, the aggregate price of products belonging to the Electronics category is calculated by summing their individual prices ($141,615 + $4,975), resulting in an ItemGroupSummarySubtotal of $146,590. This confirms that your procedure is working as expected.
