---
article_id: ind.product_catalog_create_a_variation_attribute_set_in_product_catalog_management.htm
title: Create a Variation Attribute Set in Product Catalog Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_create_a_variation_attribute_set_in_product_catalog_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create a Variation Attribute Set in Product Catalog Management

Group product attributes, such as size or color, into an attribute set to apply them to products efficiently. Because a product can have multiple attributes, applying a set to one or more products rather than assigning individual attributes provides consistency across products.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create a variation attribute set:	Manage Product Catalog

To create an attribute set, first create the individual product attributes, and then group them. For example, if your variation parent is a phone that uses the attributes color, memory, and display. Grouping these attributes means that you only assign a single attribute set to the product instead of three separate attributes.

NOTE
You can include up to 5 variation attributes in an attribute set.
You can't modify an attribute set after adding it to a product.
Create a product attribute set.
From the object management settings for product attributes, go to Fields and Relationships.
Click New.
Select Picklist, and then click Next.
Enter the details.
Enter a name. For example, color.
Select Enter values, each value separated by a new line.
Enter the attribute values. For example, red, green, and blue.
Click Next.
Set field-level security for the picklist field, and then click Next.
Save your work.

To create more product attributes, repeat step 1.

Create a variation attribute set.
From the Product Catalog Management home page, click Variation Attribute Set.
Click New.
Enter the details.
Enter a name. For example, phone specifications.
Select the fields that you want to add to the attribute set. For example, select color and memory.
For Group By, select None.
Save your work.
SEE ALSO
Create a Variation Parent
Create a Variation Product
