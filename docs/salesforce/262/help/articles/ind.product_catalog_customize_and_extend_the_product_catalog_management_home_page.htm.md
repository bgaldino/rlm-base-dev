---
article_id: ind.product_catalog_customize_and_extend_the_product_catalog_management_home_page.htm
title: Customize and Extend the Product Catalog Management Home Page
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_customize_and_extend_the_product_catalog_management_home_page.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Customize and Extend the Product Catalog Management Home Page

Manage attributes, products, catalogs, and rules on the Product Catalog Management app’s home page. Your admin can use the Lightning App Builder to customize and extend the home page for your users.

REQUIRED EDITIONS
View supported products and editions.
USER
PERMISSIONS NEEDED
To customize the Lightning App Builder Home page:	Manage Product Catalog
From the Product Catalog Management Home page, click Setup, and then click Edit Page.
In the Lightning App Builder, drag the Tabs standard component from the palette on the left, and drop it on the Lightning App Builder Canvas area in the middle.
Add and customize tabs as necessary. See Add and Customize Tabs on Lightning Pages Using the Lightning App Builder.
Drag the Grid (2) component onto the customized tab. Customize the number of grid columns, their width, and padding in the right panel.
Drag the Object Quick Links (3) component onto the grid columns.
In the panel on the right, enter the title, description, and Object API name for the object whose tile will appear on the Home Page. Keep the tile title and description short so that an increased grid column count doesn't impact readability. To determine the object API name, follow these steps:
In Lightning Experience, from Setup, open Object Manager, and search for the object that you want to add to the home page.
Copy the API name for that object and paste it in the Lightning App Builder.
In this example, the admin has added Account and Cases objects in the Grid columns.
Save your changes. 
As a Salesforce Admin, check that the intended users have appropriate access (create, read, update, and delete) to the object that you’ve added to the custom tile. 

To see the additional tab groups and any customizations you’ve made in your production home page, click Activate.

You can customize tabs such as Catalogs, Products, Attributes, and Rules in Product Catalog Management. You can also customize their grid components and object link components as necessary.

SEE ALSO
Lightning App Builder
