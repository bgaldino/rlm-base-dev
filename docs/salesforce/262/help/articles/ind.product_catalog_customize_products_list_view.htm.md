---
article_id: ind.product_catalog_customize_products_list_view.htm
title: Customize Product Discovery in Lightning App Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_customize_products_list_view.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Customize Product Discovery in Lightning App Builder

Add product discovery components to supported pages and customize them to show only the information and options that your users need. For example, customize the Product List component to show additional fields that your users are interested in.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To add and customize components:	Customize Application

When you customize pages on Salesforce Lightning Service Console, you can add components to only the supported pages.

The Product List component is supported only on catalog pages.
The Product Details, Product Bundle Details, and Product Attribute Details are supported only on product pages.

When you customize Experience Cloud sites, make sure that you create sites by using one of these templates.

Build Your Own (Aura)
Customer Service
Customer Account Service
Open the page editor.
If you’re using the Salesforce Lightning Service Console, open the supported page, and then from Setup, click Edit Page to open the Lightning App Builder.
If you’re using Experience Cloud sites, open Experience Builder and select the page that you want to add the component to. See Find Your Way Around Experience Builder.
From the Components panel, drag the component onto the page.
If you’re using Experience Builder, enter the record ID, if necessary.
The Record Id field is populated with {!recordId} by default.
If you add a component to a supported page and want the Record Id value to be automatically populated at run time based on the user-selected catalog, retain {!recordId} as the value.
If you add the component to any other page, enter the unique ID of a catalog in the Record Id field. See Locate the Unique ID of a Record in Salesforce.
To view the properties pane, click the component.
Specify the values for the properties.
Save your changes.
SEE ALSO
Activate Lightning Experience Record Pages
Product Discovery Component Properties
