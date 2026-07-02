---
article_id: ind.qocal_cumulative_quantity_contract_pricing.htm
title: Calculate Cumulative Quantity Pricing for Contractual Discounts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_cumulative_quantity_contract_pricing.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Calculate Cumulative Quantity Pricing for Contractual Discounts

Motivate larger purchases by aggregating product quantities across transactions and active assets to apply accurate negotiated price or discount tiers. This approach combines quantities from quote lines with existing active assets to make sure that the system applies the correct tier based on total purchase volume over time.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To use cumulative quantity pricing:	Sales Pricing Design Time User permission

Cumulative pricing is designed to work with contract-based volume and tier pricing methods.

IMPORTANT For active orders or assets, cumulative pricing requires Contract Pricing Volume or Tiered Discounts. However, you can use it independently when simulating a pricing procedure.
From the App Launcher, find and select Pricing Procedures.
Select Default Pricing Procedure.
If you’ve created a custom pricing procedure, select that procedure.
Select the Volume Discount or Tier Discount element.
Select Use Cumulative Pricing.
Map the correct input and output variables in your pricing procedure.
Save your changes and activate the pricing procedure. Alternatively, if you want step-by-step instructions on creating a custom pricing procedure to perform cumulative pricing calculations, see Calculate Volume or Tiered Discounts With Cumulative Pricing.
Update your Contract page layout with the Pricing Schedule component to view and negotiate contractual pricing..
In Setup, search for and select the Contract object in the Object Manager.
Select Lightning Record Pages, and then the Contract Record Page.
Select Edit, then select Tabs on the page layout of the Lightning App Builder.
Select Add Tab, select the new tab, and select the Pricing Schedule tab label.
Click Done, then select the new Pricing Schedule tab on the Lightning App Builder.
Drag the Contract Pricing Schedule component from the Standard Components section to the new tab and save.
Return to the Contract page and select the Pricing Schedule tab.
Create contract pricing for a product by using the Pricing Schedule.
Create contract-based volume tiers for a product.
Select New or view existing Product Pricing Tiers.
Select Edit Tiers under Adjustment Value to change tiers.
Activate the contract and refresh the Contract Pricing decision tables.
On the Contract Details tab, set the Aggregation Strategy field to Cumulative. If you don’t set this field, the system prices each line item individually without cumulative quantity.
Create a quote.
Add the contract number to the Pricing Contract field on the quote to apply contract pricing.
Add at least two quote line items for the same product with a matching product selling model (PSM) and unit of measure (UOM).
The system aggregates the total purchase quantity across matching quote lines and applies the tiers cumulatively. The quote’s Net Unit Price updates to the aggregated cumulative tier price.

When you set the Aggregation Strategy to Cumulative, the transaction system uses these rules to aggregate quantity:

Aggregates quantities based on transaction line items with a matching product, PSM, and UOM.
Bundle lines that meet the same matching criteria.
Active assets on the account that meet the same matching criteria.
