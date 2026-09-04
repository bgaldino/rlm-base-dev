---
article_id: ind.product_configurator_make_product_names_editable.htm
title: Make Product Names Editable in Product Option Cards
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_make_product_names_editable.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_set_up_flow.htm
fetched_at: 2026-09-04
---

# Make Product Names Editable in Product Option Cards

Give sales reps access to edit product names from the product option cards during bundle configurations.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create and edit a product configuration flow:	Product Configurator
To change field accessibility:	Customize Application AND Manage Profiles and Permission Sets

If you cloned the Default Product Configurator flow after Winter ’27, product names are read-only by default. To make them editable, grant edit access to the Custom Product Name field on the transaction line item objects and set the Read-Only Product Name flow attribute to false in your custom product configurator flow. Only child product names are editable.

Provide Edit Access to the Custom Product Name Field

Set field-level security on the Custom Product Name field on the Quote Line Item and Order Product (OrderItem) objects. Product Configurator shows the edit icon next to the product name on an option card only to users who have edit access to this field.

Go to the object management settings of the Quote Line Item and Order Product objects, and edit the field-level security of the Custom Product Name field.

Select Visible and deselect Read-Only for user profiles of that require edit access.

See Modify Field Access Settings.

Set the Read-Only Product Name Flow Attribute
From Setup, in the Quick Find box, enter Flow, and then select Flows.
Open your product configurator flow.
Edit the screen element and select the Product Configurator Option Groups component.
To enable editing of product names on option cards, for the Read-Only Product Name attribute, select {!$GlobalConstant.False}.
Save your changes and activate the flow.
