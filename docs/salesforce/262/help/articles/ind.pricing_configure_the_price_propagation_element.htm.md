---
article_id: ind.pricing_configure_the_price_propagation_element.htm
title: Configure the Price Propagation Element
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_configure_the_price_propagation_element.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Configure the Price Propagation Element

Define the formulas and execution sequence for your hierarchical pricing logic by using the Price Propagation element.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
USER PERMISSIONS NEEDED
To create, update, and delete pricing procedures:	Salesforce Pricing Design Time User
Define a context definition that specifically supports the nested group hierarchy structure within your quotes (for example, Sales Transaction Context).
Configure the necessary context mappings to link your pricing procedure to your data.
Configure Propagation Rules and Nodes
Open an existing pricing procedure or create a new one.
NOTE If you're using an existing procedure, make sure it doesn't already contain a price propagation, derived price, or promotion element.
Click  to add the Pricing Setting element, select Enable Propagation, and map your common variables (if not already configured).
In the Price Setting element, under Propagation Setting, select Configure Propagation Rules.
In the Configure Propagation Table window, select one of these options:
Configure a new table: Select this to define your nodes, joins, and formulas from scratch. Proceed with the steps below.
Select a template: Select the Map sales SalesTransactionItem to SalesTransactionGroup template. This template is based on the predefined Sales Transaction Context and automatically maps SalesTransactionItem records to the SalesTransactionGroup.
Select Add Nodes and select these attributes.
SalesTransactionItem:
ItemDiscountPercentage
ListPrice
ItemUnitCost__std
ItemNetTotalPrice
ItemTotalMarginAmount__std
SalesTransactionItemGroup
SalesTransactionGroup:
GroupDiscount__std
SummarySubtotal
GroupTotalMarginAmount__std
GroupSource
Under Join Nodes, define the parent-child relationship between your data levels so the procedure knows how to propagate values.
Mapping Type: Parent-Child
Parent Key: GroupSource
Child Key: SalesTransactionItemGroup
Node Identifier: Select a unique identifier (like Line Item Tag) to track these calculations in the execution logs.
Select Merge Attributes and specify these attributes.
Attribute Name: Merged_header_1
Merged Condition: Not Null
Attribute 1: GroupTotalMargin_std
Attribute 2: ItemTotalMargin_std
Define Logic for Horizontal Propagation
To define your pricing logic, select Edit Attributes.
Define your Horizontal Formulas for line-level calculations.
Select the column you want to calculate (for example, Net Unit Price).
Enter the formula (for example, UnitCost + MarginAmount).
Enter a sequence number (for example, 1, 2) to tell the procedure which formula to run first.
Configure the Use Zero for Null Values setting.
If enabled, null inputs are treated as 0 and the formula proceeds to the next step.
If disabled, any formula with a null argument is skipped.
NOTE

The Sequence field cannot be empty or negative, and two fields cannot share the same sequence number.

The system does not auto-adjust sequences. If you change the sequence of one formula, you must manually update the sequence numbers for all other formulas to ensure the correct order.

Define Logic for Ascending Propagation
Define your Ascending Propagation to roll up values to the parent.
Create a merged attribute (for example, Merge Total Cost).
Select the aggregation function Sum.
Specify the child field to roll up ( for example, Sum(!Child.ItemTotalCost)).
If needed, add up to three conditions to filter the child items included in the calculation (for example, SellingModelType = 'One Time'). All specified conditions must be met for a line item to be included. Items that don't match the criteria or contain null values in the specified fields are excluded from the rollup.
Save the propagation rules.
Add the Price Propagation Element
Add the Price Propagation element.
Save and activate the procedure.
