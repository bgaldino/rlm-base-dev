---
article_id: ind.product_catalog_product_discovery_component_properties.htm
title: Product Discovery Component Properties
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_product_discovery_component_properties.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Product Discovery Component Properties

Use the Product Discovery component properties to show only the information and options that your users need.

REQUIRED EDITIONS
View supported products and editions.

Here’s a table that lists all the properties and their descriptions. Keep in mind that the available properties vary across components.

PROPERTY NAME	DESCRIPTION	LIGHTNING APP BUILDER	PRODUCT LIST CONTAINER FLOW COMPONENT	PRODUCT LIST PAGE FLOW COMPONENT
Account ID	Enter the ID of the account that you want to show products for.	No	Yes	Yes
Record ID	Enter the ID of the product catalog that you want to list products for.	No	Yes	Yes
Run qualification procedure	Enable the property if you want the qualification procedure selected on the Product Discovery Settings page to run for the component.	Yes	Yes	Yes
Run pricing procedure	

This setting works only when Salesforce Pricing is enabled.

Enable the setting if you want the pricing procedure selected on the Product Discovery Settings page to run for the component.

	Yes	Yes	Yes
Let users configure products	

Enable the property to configure products from the Browse Catalogs quick action from quote and order pages.

	Yes	Yes	Yes
Let users enter the quantity	Enable the property for users to enter a quantity.	Yes	Yes	Yes
Let users select multiple products	Enable the property if you want to allow users to select multiple products.	Yes	Yes	Yes
Page Size	Enter the number of products that the page loads by default. When a user reaches the end of the list, the next set of products are loaded.	Yes	Yes	Yes
Add Products To	

Use this setting only if record types aren’t enabled for the object.

Select the object that a user can add products to. For example, if you select Quote in the Add Products To field, then users see the Add to Quote and Add Selections to Quote buttons.

The list of objects that appear depends on the availability of other products. For example, the Quote and Order options appear in the dropdown list only if Transaction Management is available in your Salesforce org.

	Yes	Yes	Yes
Supported Views	Select how products appear for users. If you select List and Tile views, users can switch between these views.	Yes	Yes	Yes
Default View	

If you select List and Tile Views in Supported Views, specify the default view.

When a user refreshes the page or starts a new session, the view returns to the default view.

	Yes	Yes	Yes
Tile View Type	

If you select tile view, specify the type of tile view.

The basic tile shows only the image, name, and description.

The detailed tile shows the image, name, and description along with other information such as pricing, configuration options, product selling model, and additional fields based on the configured properties.

	Yes	Yes	Yes
Display Fields	Select up to 3 additional standard or custom fields that you want to show.	Yes	Yes	Yes
Custom Action Label	Enter an action label for the product list page to add products to your record page.	Yes	No	Yes
Context Data Input Array	Enter the apex class of the list of records that determine product eligibility and calculate product prices.	No	Yes	Yes
Select catalogs from the product list page	Enable the property so that users can select and move between catalogs.	Yes	Yes	Yes
Show guided product selection	

The functionality provided in this setting is available only if users have enabled Guided Product Selection.

Enable this property to provide users access to Guided Product Selection. Users can answer questions to show specific products according to their requirements.

	Yes	Yes	Yes
Show smart product selection	

The functionality provided in this setting is available only if users have enabled Smart Product Selection.

Enable this property to use AI capabilities to show relevant products to users when they browse product catalogs.

	No	Yes	Yes
View Cart	Enable the property so that users can view the selected products in the cart.	No	Yes	No
Product Catalog Id	Enter the ID of the product catalog that you want to list products for.	Yes	Yes	Yes
Product Catalog Name	Enter the name of the product catalog that you want to list products for.	Yes	Yes	Yes
Object API Name	Enter the API name of the transaction record object, such as Quote or Order.	Yes	Yes	Yes
Group Transaction Id	Enter the ID of the specific group within a transaction (e.g., a Quote Group) to which products should be added.	Yes	Yes	Yes
Group Transaction Name	Enter the name of the transaction group to which products should be added.	Yes	Yes	Yes
Discover Products Context	Enter the Apex class that defines the context for product discovery to tailor the list based on specific business logic.	Yes	Yes	Yes
Transient Line Save Flow	Enable this property if the component is being used within a Transient Line Save flow to manage temporary line item records.	Yes	Yes	Yes
Run Qualification Procedure	Enable the property if you want the qualification procedure selected on the Product Discovery Settings page to run for the component.	Yes	Yes	Yes
Configure Products	Enable the property if you want to allow users to configure products from the Browse Catalogs quick action from quote and order pages.	Yes	Yes	Yes
Configure Quantity	Enable the property if you want to allow users to enter a product quantity.	Yes	Yes	Yes
Select Multiple Products	Enable the property if you want to allow users to select multiple products simultaneously.	Yes	Yes	Yes
View Product Image	Enable this property if you want product images to be visible to users in the list or tile views.	Yes	Yes	Yes
View Product Prices	Enable this property if you want users to see the list price for products in the list.	Yes	Yes	Yes
View Cart	Enable the property so that users can view the selected products in the cart.	Yes	Yes	Yes
Number of Products	Enter the number of products that the page loads by default. The minimum is 12 and the maximum is 100.	Yes	Yes	Yes
Tile View Label	Specifies the tile variant. Supported values are Basic Tile and Detailed Tile.	Yes	Yes	Yes
Additional Fields	Select up to 3 additional standard or custom fields from the Product2 object that you want to show in the list.	Yes	Yes	Yes
Maximum Values per Facet	Enter the maximum number of filter values (facet values) that a user can see within a single filter category.	Yes	Yes	Yes
Maximum number of Facets	Enter the maximum number of filter categories (facets) available to the user for narrowing down products.	Yes	Yes	Yes
Show Message Bar	Enable this property to display a bar at the top of the page showing error, warning, and info messages from configuration rules.	Yes	Yes	Yes
Recommended Products	Enable this property to display a tab for recommended products based on the Configuration Rules on the current transaction.	Yes	Yes	Yes
NOTE When you create an apex class to create additional context data for your records, you must configure it in the Context Data Input Array property of your product list component.
