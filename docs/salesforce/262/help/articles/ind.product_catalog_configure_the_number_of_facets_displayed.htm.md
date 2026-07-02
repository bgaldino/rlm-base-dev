---
article_id: ind.product_catalog_configure_the_number_of_facets_displayed.htm
title: Configure the Number of Facets Displayed
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_the_number_of_facets_displayed.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Configure the Number of Facets Displayed

You can now define a facet limit to control the number of dynamic facets shown on your Product Discovery list page. In addition, you can also define the number of values shown for each facet. This feature overrides the default display, ensuring only the specified number of facets are visible.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To build and rebuild indexes:	

Manage Product Index and Search

AND

View Product Catalog

Before You Begin:

Check if the CommercesearchHighFacetlimit permission is set to true or false. If the permission is set to true, you can show a maximum of 35 facets. If the permission is set to false, you can show a maximum of 10 facets.

From Setup, in the Quick Find box, enter Flows and select it.
Select Discover Products.
In the flow builder, select Product List screen element.
Select Product List Page Container component. Update the Maximum number of Facets and Maximum Values per Facet fields to specify the number of facets and values per facet respectively. 
Save the changes.
