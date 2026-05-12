---
article_id: ind.qocal_create_contract_prices_or_discounts_manually.htm
title: Manage Contract Prices or Discounts Manually
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_contract_prices_or_discounts_manually.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Manage Contract Prices or Discounts Manually

Sales reps manually specify contract prices or discounts when they create a contract. When you create contract item prices and price adjustment schedules, the system applies the negotiated pricing and discounts to future business transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To use Contract Pricing:	Salesforce Pricing Design Time User

Before you create pricing schedules, review these considerations.

Review the start and end dates for products to make sure that they are within the contract's date range.
Select a product selling model that is available in the price book for the product you’re adding.
Manage Pricing Schedule by Using the Contract Pricing Schedule Component

To manage all products and their pricing schedules in one view, use the Contract Pricing Schedule component.

NOTE The Contract Pricing Schedule component is available on contract pages only if an admin adds the component to the pages.
From the App Launcher, find and select Contracts.
Open a contract.
On the Pricing Schedule tab, search for and add a product.
NOTE You can’t add multiple instances of a product with the same product selling model to a contract.
Enter the discount type, discount value, and start date.
Enter any additional details, such as the end date, if needed.
Save your changes.
Click  next to the product and select View.
On the Contract Item Price subtab, enter a product selling model.
Save your changes and close the subtab.
Activate the contract.
Manage Pricing Schedule by Using the Contract Item Prices Related List

To manage the pricing schedule for each product separately, use the Contract Item Prices related list.

From the App Launcher, find and select Contracts.
Open a contract.
In the Contract Item Prices related list, select New.New.
Enter the item, product selling model, and start date.
IMPORTANT Don’t add an item that has the same product selling model, start date, and end date as an existing item in the contract.
To enter pricing not based on volume, enter the discount type and value, or the contract price.
Save your changes.
To use volume-based pricing, create contract item price adjustment tiers.
On the Contract Item Prices related list, click the entry in the Name column.
Select an adjustment method.
Open the Contract Item Price Adjustment Tiers related list.
Click New.
Select a tier type, and then enter the lower bound, upper bound, and tier values.
Save your changes.
Create more tiers.
Similarly, create additional contract item price records.
Activate the contract.
