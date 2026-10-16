---
article_id: ind.pricing_formula_based_pricing.htm
title: Build Pricing Rules with Formula-Based Pricing
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_formula_based_pricing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_element.htm
fetched_at: 2026-09-07
---

# Build Pricing Rules with Formula-Based Pricing

Perform functions and mathematical calculations to generate the price of a product. Solve complex pricing scenarios by defining multiple formulas within a single Formula-Based Pricing element.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
USER PERMISSIONS
NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time

Formula-based pricing offers a dynamic approach to price calculation that moves beyond static price lists and discounts. Businesses can define sophisticated pricing rules by using custom formulas and functions within pricing procedures. By leveraging various factors such as product attributes, customer segments, and real-time market conditions, organizations can create highly flexible and responsive pricing strategies.

Formula-Based Pricing is a powerful tool for implementing complex pricing models. It enables greater adaptability to changing business needs and market dynamics compared to traditional, less agile pricing methods. For supported operators and functions in Formula Based Pricing elements, see Operators and Functions in Expression Sets.

Let’s use the Formula Based Pricing element to calculate the final cost for an order of 5 printers at US $200 each by applying a $40 discount, a 10% delivery charge, a 5% per-unit bulk discount, and a $20 rebate.

NOTE Formula Based Pricing doesn't support derived products on quote line items.
Configure a pricing procedure.
To add the Pricing Setting element, click , and map these variables.
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
Add the Formula-Based Pricing element, specify your formulas, and map the variables.
You can add up to five formulas.
SCENARIO	FORMULA	OUTPUT VARIABLE	FORMULA LOGIC
Apply promotional discount	

(ListPrice * LineItemQuantity) - 40

	ItemNetTotalPrice	Calculates the base price and applies a $40 discount.
Provide bulk purchase discounts	

ItemNetTotalPrice * 0.05

	ItemDiscountAmount	Applies a 5% discount on the net price.
Calculate the base cost and promotional discount	

ItemNetTotalPrice - ItemDiscountAmount

	ItemNetTotalPrice	Calculates the net price of each line item.
Adjust delivery charges	

ItemNetTotalPrice * 0.10

	ItemTotalAdjDistAmount	Adds a 10% delivery charge.
The quantity of the purchased product	LineItemQuantity	ItemProductAmount	Adds item quantities.
Add rebate to the final amount	ItemNetTotalPrice + ItemTotalAdjDistAmount - 20	TotalLineAmount	Applies a flat discount of $20.
To test your procedure, click Simulate. Enter the input values for your printer product, and click Simulate again.
The price waterfall shows the formulas used to apply discounts and determine the price of the printers, confirming your procedure is working as expected.
