---
article_id: ind.product_catalog_assign_attributes_to_a_product_classification.htm
title: Assign Attributes to a Product Classification
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_assign_attributes_to_a_product_classification.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_product_classifications.htm
fetched_at: 2026-09-04
---

# Assign Attributes to a Product Classification

After you create a Product Classification, assign attributes to it. You can assign individual attributes to a product classification or a collection of attributes through attribute categories.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To assign attributes to a product classification:	Manage Product Catalog

Here’s an example. Consider a product classification called “Beds Classification”. There’s an attribute category called “Bed” that has attributes such as material, finish, size, and model name. There’s another attribute category called “General” that has attributes such as Warranty in Months, and Country of Origin. The attributes Availability and Net Quantity don’t belong to any attribute category.

You can assign attributes that belong to the attribute categories “Bed” and “General” to the product classification “Beds Classification”. You can also assign individual attributes “Net Quantity” and “Availability” to the product classification. The product classification “Beds Classification” now has all of these attributes.

To assign attributes, follow these instructions:

From the Product Catalog Management app’s home page, click Product Classifications.
On the Product Classifications list view page, click the product classification to which you want to assign attributes.
Navigate to the Attributes tab.
In the Attributes section, click Assign.
To assign a collection of attributes to the product classification, select Assign Attributes by category. To assign individual attributes to the product classification, select Assign individual attributes.
Click Next.
If you selected Assign Attributes by category, then select one or more attribute categories, and click Assign.
NOTE You can assign only the active attributes of an attribute category to product classifications.
If you selected Assign individual attributes, then select one or more attributes from the Categorized and Uncategorized tabs and click Assign.
NOTE You can assign only active attributes to product classifications.

You can unassign attributes from a product classification. If you unassign an attribute from a product classification, the status of the attribute changes to “Inactive”.

To delete an attribute assigned to a product classification, click  next to the attribute, and click Delete.

To activate an inactive product classification attribute, click Edit, and change the status to Active.

You can preview a product classification to see how it will look and function for your users, if you have the Product Configuration User permission set license.

Considerations While Assigning Attributes to Product Classifications
Here are a few scenarios you can run into when assigning attributes to product classifications.
