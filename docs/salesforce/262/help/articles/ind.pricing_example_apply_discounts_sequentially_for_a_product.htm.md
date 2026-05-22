---
article_id: ind.pricing_example_apply_discounts_sequentially_for_a_product.htm
title: "Example: Apply Discounts Sequentially for a Product"
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_example_apply_discounts_sequentially_for_a_product.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Example: Apply Discounts Sequentially for a Product

In this scenario, let's apply discounts to the laptop sequentially. The first discount is calculated from the list price, and each subsequent discount is applied to the previously discounted price.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create pricing procedures:	Salesforce Pricing Design Time

Implementing this discount involves a few key steps.

Create price adjustment tier records.
Create custom or use existing Salesforce objects to hold your price adjustment data.
Define decision tables, setting criteria (like product, price adjustment tiers) and their adjustments (types and values).
Map these custom decision tables to the org’s pricing recipe.
Create a procedure output resolution record to build a strategy to calculate discounts sequentially.
Use the Price Adjustment Matrix to calculate these discounts.
Create Price Adjustment Tier Records

Since we’re creating a custom decision table using the Price Adjustment Tier Salesforce object to hold your price adjustment data, create a few price adjustment tiers to apply your discounts.

Create a price adjustment tier record.
Specify these details.
Price Adjustment Schedule: Standard Price Adjustment Tier
Product: Laptop
Tier Type: Amount
Tier Value: 100
Lower Bound: 10
Upper Bound: 20
Effective From: 01-03-2025
Product Selling Model: One Time
Click Save & New.
Create another price adjustment tier record with these details.
Price Adjustment Schedule: Standard Price Adjustment Tier
Product: Laptop
Tier Type: Amount
Tier Value: 150
Lower Bound: 21
Upper Bound: 40
Effective From: 01-03-2025
Product Selling Model: One Time
Click Save & New.
Create a third price adjustment tier record with these details.
Price Adjustment Schedule: Standard Price Adjustment Tier
Product: Laptop
Tier Type: Amount
Tier Value: 200
Lower Bound: 41
Effective From: 01-03-2025
Product Selling Model: One Time
Save your changes.
Close the tabs for the new price adjustment tiers that you just created.
On the Details tab, on the Standard Price Adjustment Tier page, select Active.
Save your changes.
Create a Custom Decision Table

Each attribute value on a line item must resolve to a single unique row in the decision table. Salesforce Pricing doesn't support retrieving multiple outputs for the same attribute value. Set up your decision table to map each specific input value to only one discount entry.

From the App Launcher, search for and select Lookup Tables .
Select Decision Table.
Specify these details.
Enter a name and then press Tab to autopopulate the API Name. For our example, we’re calling the decision table, Procedure Output Resolution.
Select Pricing as the application usage.
Select Advanced as the decision table type.
Click Save & Next.
Specify these decision table details.
Source Object: Price Adjustment Tier.
Set the following condition.
Set the source object field as Product2Id and the operator as Equals.
Set another condition for the name.
Set the source object field as Name and the operator as Equals.
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
Configure Lookup Relationships for Multi-Value Attributes

To apply multiple discounts to a single line item, you must establish a relationship between your transaction object and your adjustment data.

From Setup, in the Quick Find box, find and select Object Manager.
From Object Manager, find and select the object holding your adjustment data (e.g., Price Adjustment Tier).
Under Fields & Relationships, create a custom field with the Lookup field type.
Select your primary transaction object (e.g., Quote Line Item) as the reference object. This mapping allows a single line item to associate with multiple adjustment records.
In your Context Definition, create a node to represent the adjustment object.
Complete the Context Mapping to link the fields from your adjustment object to the context attributes.
Map these new context tags to the variables in your Pricing Procedure to allow the engine to retrieve the list of values.
On a record's Related tab, verify that you can associate multiple adjustment records with one line item.
In the Pricing Procedure, click Simulate. The engine should now resolve all associated values for the line item and apply the discounts according to your sequence.
Map the Variables in Your Custom Decision Table
From Setup, in the Quick Find box, find and select Pricing Recipes.
Choose the pricing recipe that you want to modify. For our example, select NGPDefaultRecipe.
On the Price Adjustment Matrix tab, click Modify.
Select the custom decision table created by you. Here, select Procedure Output Resolution.
Map the following variables.
AdjustmentValue: TierValue
AdjustmentType: AdjustmentType
Save your changes.
Create a Procedure Output Resolution Record
From the App Launcher, find and select Price Management.
From the app navigation menu, select Procedure Output Resolution.
Click New.
Specify these details.
Name: Sequential_Pricing
Pricing Element: Price Adjustment Matrix
Resolution Formula: SEQUENCE(TierValue)
Activate your procedure output resolution record.
Save your changes.
Create a Constant for a Resolution Strategy
Create a pricing procedure. To create a pricing procedure, follow the first 5 steps in Configure Your Pricing Procedure.
On the Pricing Procedure builder canvas, click .
On the Resource Manager panel, click Add Resource.
In the Add New Resource page, specify these details.
Resource Type: Constant
Resource Name: ResolutionStrategySequence
Data Type: Text
Default Value: Sequential_Pricing. This is the procedure output resolution record that you created in the step above.
Save your changes.
Use the Price Adjustment Matrix Element to Apply Discounts Sequentially
Click to add the Pricing Setting element and map these variables.
Input Variables
Line Item: LineItem
Output Variables
Price Waterfall: price_water_fall
Net Unit Price: NetUnitPrice.
Subtotal: ItemNetTotalPrice
Add the List Price element to fetch the base price of the product.
Under Lookup Table Details, select the Price Book Entries V2 decision table and map these variables.
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
Under Lookup Table Details, select the Procedure Output Resolution decision table. This is the custom decision table that we created.
Select Enable Output Resolution.
Map these variables.
Input Rule Variables
Product: Product
Price Adjustment Tier Name: Contributor
We’ve mapped the price adjustment tier name variable to a generic tag called Contributor to track the price adjustment tier records. If you want to define a custom tag, you can edit your context definition and add a tag and map it accordingly.
Input Variables
Quantity: LineItemQuantity
Input Unit Price: ListPrice
Resolution Variables
Resolution Strategy: ResolutionStrategySequence
Use As List: Price Adjustment Tier Name
IMPORTANT If you want to select multiple rows for a line item, the input rows in the selected decision table should have at least one column with unique values. The value in that column is what we’ll use in tag associated with the Use As List resolution variable.
Click and select Include in Output.
Finally, set your preferences to view pricing information, profile access, and rank information.
Save your procedure.
Click Simulate to test your procedure. Enter the input values for your laptop product and click Simulate again.
The price waterfall shows that the pricing engine has sequentially applied all the discounts associated with different price adjustment tiers for the Laptop product, confirming that your procedure is working as expected.
