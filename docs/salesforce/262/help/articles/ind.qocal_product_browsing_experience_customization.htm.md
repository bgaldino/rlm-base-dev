---
article_id: ind.qocal_product_browsing_experience_customization.htm
title: Product Discovery Lightning Components
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_product_browsing_experience_customization.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Product Discovery Lightning Components

Product Discovery provides Product List, Product Details, Product Bundle Details, and Product Attribute Details components that you can add to pages on supported Salesforce Lightning Apps and Experience Cloud sites. To provide easy access to these components, some Salesforce Apps also use a tailored version of these components.

REQUIRED EDITIONS
View supported products and editions.
Product Discovery Lightning Components
COMPONENT	DESCRIPTION	SUPPORTED PAGES
Product List	Shows products, product categories, product eligibility, and pricing. Users can search and filter products.	Catalog
Product Details	Shows product images, price, and description. Users can select a buying option, select quantity, and configure and add products.	Product
Product Bundle Details Component	Shows products in a bundle along with their quantity and pricing information.	Product
Product Attribute Details Component	Shows product attributes. Users can specify attribute values.	Product

Some apps also use tailored versions of Product Discovery components. For example, in the Revenue Lifecycle Management app, the View Catalogs quick action on account record pages and the Browse Catalogs quick action on quote and order use tailored versions of these components.

Considerations When Adding Product Discovery Components

In Salesforce Lightning Service Console, you can add Product Discovery components only to the supported pages. In Experience Cloud sites, you can add these components to any page.

In Salesforce Lightning Service Console, you can add Product Discovery components only to supported end user apps. For example, you can add components to the Agentforce Revenue Management app.
In console apps, when your users click the View Catalogs quick action on account pages to open a catalog page, the account ID is passed to the catalog page. Product Discovery considers this account information to determine the eligibility of the products shown on the catalog page. However, in standard apps, the account ID isn’t passed to the catalog page. See How Are Console Apps Different from Standard Apps?
SEE ALSO
Create and Configure Lightning Experience Record Pages
Locate the Unique ID of a Record in Salesforce
