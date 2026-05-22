---
article_id: ind.product_catalog_configure_filterable_fields_attributes.htm
title: Configure Filterable Fields & Attributes
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_filterable_fields_attributes.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Configure Filterable Fields & Attributes

Specify the fields and attributes that your sales reps can use as filters on the product discovery product list page. By configuring filterable fields and attributes, you help sales reps quickly narrow down search results to find the products they need.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To build and rebuild indexes:	

Manage Product Index and Search

AND

View Product Catalog

Let us explore faceted search by taking an example. The following products and attributes are identified as filterable.

Sun Compound: Powder Weight

Zon Compound: Powder Weight and Gel Quantity

Kyocea Compound Premium: Powder Weight and Gel Quantity

From the Product Catalog Management app’s home page, click Index and Search Configuration.
Click Manage Fields & Attributes tab.
Click Edit.
Select Gel quantity and Powder Widget attributes as Filterable.
You can select a combined total of up to 87 searchable and filterable fields and attributes. There is no specific limit for each type, provided the combined total doesn't exceed 87.
Click Next.
Select the fields and adjust the filter order using the respective arrows. Use the left and right arrows to select or deselect fields. Use the up and down arrows to adjust the filter order. The order that you select is the order in which the facets are displayed on the product discovery product list page.
Save your changes.

You must rebuild the index after you set up, update, or delete the field browse options.

Click Indexes tab and click Rebuild Index.
Select Full Index Rebuild and click Rebuild.
Enable Use Indexed Data for Product Listing and Search.
From Setup, in the Quick Find box, enter Product Discovery Settings and select it.
Enable Use Indexed Data For Product Listing and Search.
