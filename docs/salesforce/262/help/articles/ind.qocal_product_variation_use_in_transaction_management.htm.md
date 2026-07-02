---
article_id: ind.qocal_product_variation_use_in_transaction_management.htm
title: Add Product Variations in Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_product_variation_use_in_transaction_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Add Product Variations in Quotes and Orders

Sales reps can search for and add specific product variations to a quote or order by using Browse Catalog or Quick Add. After adding a variation, such as color or size, the side panel includes its attributes. Sales reps can switch to a different variation by using the change action.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
Sales reps use of product variations in quotes and orders:	Product Catalog Management Viewer

Reference these Product Catalog Management resources to turn on the product variation feature and set up product variation records.

Turn On Product Variants
Create a Variation Attribute Set in Product Catalog Management
Create a Variation Parent
Create a Variation Product

Optionally, you can set up the Quick Add and Browse catalog search that requires that each product variation has a defined product selling model, price book entry, and category.

After your Salesforce admin completes catalog setup, sales reps can add, view, and modify product variations in their quotes and orders.

Considerations for Adding Product Variations
Keep these considerations in mind for product variations when managing and selling assets.
Add a Product Variation by Using Browse Catalog
Create or open a quote or order.
Click Browse Catalog and select a price book.
Select a variation parent product.
Click View Options to open the Product Detail Page.
Select an attribute set. For example, Color: Green, Size: 10.
Enter the quantity and click Save and Exit to create a line item on the quote or order with the selected variation.
To Quick Add a Product Variation
To add a product variation in the Sales Transaction Line Editor, use the Quick Add search bar to search for a product by name.
Variation products show in the results. Variation parents are filtered out and don’t appear.
Select the variation to add.
Confirm that the line item attributes are added by clicking the product, and review the attributes listed in the side panel’s Attributes tab. This information is read-only.
Change a Variation Product
To change a variation product on an existing quote or order, click the row-level action dropdown on the Sales Transaction Line Editor and select Change.
Select the new attribute set and save your changes.
NOTE The change action deletes the original line item and creates a new line item. New variation line items don’t have any discounts, promotions, or adjustments from the original line item carried over. Have sales reps reapply any discounts or promotions after a change action.
