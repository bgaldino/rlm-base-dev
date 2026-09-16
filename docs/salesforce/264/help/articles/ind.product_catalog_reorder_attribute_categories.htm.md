---
article_id: ind.product_catalog_reorder_attribute_categories.htm
title: Reorder Attribute Categories and Attributes
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_reorder_attribute_categories.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_dynamic_attributes.htm
fetched_at: 2026-09-04
---

# Reorder Attribute Categories and Attributes

Control the order in which attribute categories and attributes appear when reps configure products. Organize attributes into a logical sequence that matches your business process instead of relying on alphabetical order.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To reorder attributes or attribute categories:	Manage Product Catalog

Attribute categories and their attributes appear to reps in the order that you set. Reorder them to match your business process rather than relying on the default alphabetical order.

From the Product Catalog Management app's home page, click Product Classifications or Products.
From the list view, select the product classification or product that you want to reorder attributes for.
Go to the Attributes tab.
Click the Quick Action menu, and then select Reorder Attribute Categories.
In the Reorder Attribute Categories window, drag a row to rearrange attribute categories by using its drag handle. The other categories renumber automatically.

If a product classification or product has only one attribute category, you can't reorder that category.

All attributes within a category must use the same category sequence across every record in the classification hierarchy, and that sequence must match on the associated product record.

Click Next to proceed to attribute-level sequencing.
In the Reorder Attributes window, drag a row to your preferred position by using its drag handle. The other attributes renumber automatically. Expand categories to manage attributes independently and reorder uncategorized attributes the same way.
NOTE If a category has only one attribute, you can't rearrange it independently. Reordering an inherited attribute turns it into an override attribute. If you later delete that override attribute, make sure that its original inherited sequence doesn't conflict with the display order of any other attribute. Uncategorized attributes appear in the Uncategorized section. Because they lack a category sequence, reorder them individually.
Save your changes. If you assign a new attribute to a product classification, refresh your browser before you reorder attributes again.
