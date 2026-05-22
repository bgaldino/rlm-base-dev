---
article_id: ind.product_catalog_create_catalog_categories_and_subcategories.htm
title: Create Catalog Categories and Subcategories
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_catalog_categories_and_subcategories.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create Catalog Categories and Subcategories

Organize and group products in your catalog by creating catalog categories and catalog subcategories. Assign products to more than one catalog category and subcategory.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create catalog categories and subcategories:	Manage Product Catalog

Use the Categories tab for a hierarchical view of categories. To create a product category, follow these instructions:

From the Product Catalog Management app’s home page, click Catalogs.
From the catalogs list view page, click the catalog that you want to create a catalog category for. 
Click Categories.
Click Create Category.
In the New Category window, enter these field values:
Enter a name and description for the catalog category.
The Catalog field is auto-populated with the catalog name.
Select a parent category for the catalog category.
If the category you’re creating is the first category in the hierarchy, leave the parent category field blank.
To show the catalog category as a navigational breadcrumb at runtime, select Show In Menu.
This functionality isn't available in the Product Discovery user interface, however, the Product Discovery APIs can access this field.
Enter the sort order of the category in the hierarchy.
The sort order determines the order in which the categories are shown to users as part of the purchase flow.
Enter a category code.
Save your changes.
You can create more categories from the Categories tab. To update the category order, click Sort .
To add a subcategory, click  next to the category and click Add Subcategory.
Enter a name, description, code, and sort order for the subcategory.
The Catalog and Parent Category fields populate automatically.
To show the subcategory as a navigational breadcrumb at runtime, select Show In Menu.
Save your changes.
To reorganize the order in which subcategories appear under a category, click  next to a category and click Update Subcategory Order.
Drag and drop the subcategories into the order you want.
Save your changes.
SEE ALSO
Assign Products to Categories and Subcategories
