---
article_id: ind.qocal_set_up_product_discovery.htm
title: Configure Product Discovery Settings
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_set_up_product_discovery.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Configure Product Discovery Settings

Select the context definition, qualification procedure, and pricing procedure to populate the information that users see when they use Product Discovery. After you enable qualification and pricing procedures for Product Discovery, you can enable or disable them for the Product List, Product Details, or Product Bundle Details components.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To set up product discovery:	

Customize Application system permission

AND

Product Catalog Management Designer permission set

USER PERMISSIONS
NEEDED
To set a default catalog:	Customize Application system permission

Before you begin, complete these tasks.

Create a context definition.
To run qualification rules to evaluate eligibility, create a qualification rule procedure.
To use a pricing procedure to get list prices, make sure that Salesforce Pricing is enabled, and then create a pricing procedure for Product Discovery.
To use a custom flow to browse and add products from quote and order pages in Transaction Management, create a custom flow.
IMPORTANT The qualification procedure and pricing procedure for Product Discovery must use the context definition selected on the Product Discovery Settings page.
From Setup, in the Quick Find box, enter Product Discovery, and then select Product Discovery Settings.
For context definition, select ProductDiscoveryContext or the extended context definition.
To use a qualification procedure for Product Discovery, turn on Qualification Procedure, and then select the qualification procedure.
Only procedures with Product Qualification as the Usage Type appear in the Select Qualification Procedure dropdown. Procedures with Product Category Qualification as the Usage Type aren’t supported. To qualify or disqualify product categories in Product Discovery, add category-level elements to a Product Qualification procedure.
To use a pricing procedure for Product Discovery, turn on Pricing Procedure, and then select the pricing procedure.
To use a custom flow to browse and add products from quote and order pages, in Select a Custom Flow for Browsing and Adding Products in Agentforce Revenue Management, select the custom flow.
The Select a Custom Flow for Browsing and Adding Products setting is available only when Transaction Management is available in your org.
To configure a default catalog for the product list page, select a default catalog.
Configure your search settings.
To find products in catalogs of more than 4 million products, turn on Product Field Search.
Use Product Field Search to search all text-indexed fields of the product object such as product name, description, product code, and custom product fields of type text.
To use indexed product catalog data for product browse and search, turn on Use Indexed Data for Product Listing and Search.
To find your products, you can also search for indexed product fields and attribute values in the catalog.
To help users find their products faster, turn on Guided Product Selection.
Guided Product Selection uses dynamic forms that filter products in the catalog based on user responses.
To use Einstein AI to generate product descriptions, turn on Generate Product Descriptions with Einstein AI.
SEE ALSO
Context Definitions
Guided Product Selection
Manage Qualification Rules for Products in Revenue Cloud
Search Options in Product Catalog Management
Write Product Descriptions with Einstein Generative AI
