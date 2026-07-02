---
article_id: ind.pricing_calculate_attribute_based_discounts.htm
title: Calculate Attribute-Based Discounts
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_calculate_attribute_based_discounts.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Calculate Attribute-Based Discounts

Determine the price of a product based on the discounts configured for selected price impacting attributes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User

Let's use a scenario involving a large quantity of laptop purchases. We want to add a $10 override for any customer who purchased a laptop with a display resolution over 4K.

Create an Attribute Based Adjustment Record
Create an attribute based adjustment record.
Specify these details.
Price Adjustment Schedule: Standard Price Adjustment Tier
Product: Laptop
Adjustment Type: Override
Adjustment Value: 10
Effective From: 01-01-2025
Product Selling Model: One Time
Click Next.
Set the following condition.
Attribute: Display. (The price impacting attribute will be pre-populated)
Operator: Equals
Value: 4K Built-in Display
Save your changes.
On the Details tab, on the Standard Attribute Based Adjustment page, select Active.
Save your changes.
IMPORTANT We recommend refreshing the Attribute Discount Entries decision table to ensure that the attribute based adjustment records are available.
Create a Constant for a Attribute Based Adjustment Variable
Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
On the Pricing Procedure builder canvas, click .
On the Resource Manager panel, click Add Resource.
In the Add New Resource page, specify these details.
Resource Type: Constant
Resource Name: AttributePAS
Data Type: Text
Default Value: Enter the attribute based adjustment ID from the browser.
You can locate the value of your variable by going to the associated record. For example, to locate a price adjustment schedule ID, open the price adjustment schedule record page. The price adjustment schedule ID is shown in the browser’s URL. 
Save your changes.
Add the Attribute-Based Price Element
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
To add the Attribute-Based Price element, search for and add the Attribute Discount Entries decision table and map these variables.
Input Rule Variables
Price Adjustment Schedule: AttributePAS
Product: Product
Product Selling Model: ProductSellingModel
Effective From: EffectiveFrom
Effective To: EffectiveFrom
Input Variables
Attribute Name: Attribute
Attribute Value: AttributeValue
Quantity: LineItemQuantity
Is Price Impacting: PriceImpactingAttribute
Input Unit Price: ListPrice
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
.
Save your procedure.
Click Simulate to test your procedure.
Provide the following attribute-specific input values.
AttributeValue: 4k Built-in Display
PriceImpactingAttribute: true
Attribute: Display
Click Simulate again.
The price waterfall shows the attribute-based discounts used to calculate the final price of the laptops, confirming that your procedure is working as expected.
