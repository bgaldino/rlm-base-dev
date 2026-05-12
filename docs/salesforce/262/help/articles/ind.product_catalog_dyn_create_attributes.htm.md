---
article_id: ind.product_catalog_dyn_create_attributes.htm
title: Create Product Attributes in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_dyn_create_attributes.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Create Product Attributes in Agentforce Revenue Management

Create attributes to capture the characteristics or properties of products. You can define details such as attribute name, label, data type while creating an attribute.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create dynamic attributes:	Manage Product Catalog
From the Product Catalog Management app’s home page, click Attributes.
From the Attribute Definitions list view, click New.
In the New Attribute Definition window, enter these field values:
For Label enter the attribute label that runtime systems can use as a display name for the attribute.
For Source System ID, enter a unique identifier for the attribute in an external system that stores the attribute definitions.
For Data Type, select the type of data that the attribute holds. If you select Picklist, select a picklist from the Picklist field.
If this attribute is a required attribute, select Required. You can override this property when you assign the attribute to a product classification, or when a product inherits the attribute.
To activate an attribute select Active.
You can assign only active attributes to Product Classifications and Attribute Categories.
NOTE Before you deactivate any attribute, ensure that it isn’t in use in any Products or Product Classifications.
Enter a description for the attribute.
Enter a description for the attribute value.
Enter a Default Help Text. This field can store useful information for runtime users.
Save your changes.
