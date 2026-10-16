---
article_id: ind.product_catalog_configure_search_options.htm
title: Configure Searchable Fields & Attributes
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_search_options.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_index_and_search_of_product_catalog.htm
fetched_at: 2026-09-04
---

# Configure Searchable Fields & Attributes

Specify the indexed fields and attributes you want to be searchable by sales reps and customers to find relevant products.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To build and rebuild indexes:	

Manage Product Index and Search

AND

View Product Catalog

From the Product Catalog Management app’s home page, click Index and Search Configuration.
Click Manage Fields & Attributes tab.
Click Edit.
To enable users search for products by a specific field, choose the Searchable option next to that field.
Select the required fields in the Filterable column.
Only Picklist and Boolean fields can be filterable.
Click Next.
Select the fields and adjust the filter order using the respective arrows: use the left and right arrows to select or deselect fields, and the up and down arrows to adjust the filter order.
Save your changes.

You must rebuild the index after you set up, update, or delete the field browse options.

To rebuild the index after you update the field browse options:

Click Indexes tab and click Rebuild Index.
Select Full Index Rebuild and click Rebuild.
Search Limitations

Standard or custom fields on the Product object can be ‌searchable. Additionally, you can make the fields that are common to the Product Attribute Definition object and Product Classification Attribute objects ‌searchable.

You can select a combined total of up to 87 searchable and filterable fields and attributes. There is no specific limit for each type, provided the combined total doesn't exceed 87.

You can't make fields of these data types searchable:

Geolocation
Lookup Relationship
External Lookup Relationship
Auto Number
Formula
Checkbox
Date
Date/Time
Time
Text Area (Rich)
Text (Encrypted)

You can't make dynamic attributes of these data types searchable:

Checkbox
Date
Date/Time
Time
Use Indexed Data for Product Listing and Search

To use indexed information when users browse and search for products, enable the Use Indexed Data For Product Listing and Search setting.

REQUIRED EDITIONS
USER PERMISSIONS
NEEDED
To enable using indexed data from product listing and search:	
Customize Application system permission
Product Catalog Management Designer permission set

From Setup, in the Quick Find box, enter Product Discovery Settings and select it.
Enable Use Indexed Data For Product Listing and Search.
