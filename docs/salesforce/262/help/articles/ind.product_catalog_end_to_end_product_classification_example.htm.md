---
article_id: ind.product_catalog_end_to_end_product_classification_example.htm
title: Explore Product Classification with an Example
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_end_to_end_product_classification_example.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Explore Product Classification with an Example

Streamline the creation of a car product template by engineering a product classification hierarchy. Create a parent classification to automatically share attributes with child subclassifications, and curate valid options for specific models to reduce data entry errors.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To create a product classification:	Manage Product Catalog

Imagine your company, Autz, sells cars. Start by creating a parent classification for all vehicles. This structured template automatically shares attributes with child subclassifications for specific types, such as Sedans and SUVs

Define the Picklist

Create a picklist to store the available engine sizes.

From the Product Catalog Management app’s home page, click Picklists Classifications.
Click New.
Enter the name Engine Type and data type as Text.
Set the status to Active.
Save your changes.
Click the Related tab.
In the Attribute picklist values section, click New.
Create the first value. Enter the name as 2.5 L, code as 2.5 L, value as 2.5, and set the status to Active.
Save your changes.
Repeat steps 7 through 9 to create values for 3.5 L and 4.0 L.
Repeat the procedure to create a second picklist named Color with values Red, White, Blue, and Black.
Create the Attributes

Now, create the attribute definitions and reference the picklists you built.

From the Product Catalog Management app’s home page, click Attributes .
On the Attribute Definitions list view page, click New.
Enter the label as Engine Type, data type as Picklist.
Select the Engine Type picklist that you created.
Select Active.
Save your changes.
Repeat steps 1 through 6 to create the Color attribute, linking it to the Color picklist.
Define the Car Template

First, create a parent classification for all cars that contains a few common attributes. This classification acts as a reusable template for any vehicle you create.

From the Product Catalog Management app’s home page, click Product Classifications.
On the Product Classifications list view page, click New.
Enter the name Cars and a unique code.
Set the status to Active.
Save your changes.
Map Characteristics to the Template

Assign the attributes created earlier to the template. These attributes will automatically cascade down to any subclassification that you create later.

From the Product Catalog Management app’s home page, click Product Classifications.
Select the Cars classification.
Go to the Attributes tab. In the Attributes section, click Assign.
Select Assign individual attributes.
Find the Engine Type and Color attributes and click Assign.
Save your changes.

The Cars classification is equipped with both attributes, containing all available picklist values.

Derive Specialized Models

Create specific models (subclassifications) based on the template. These models inherit the Engine Type and Color attributes automatically.

From the Product Catalog Management app’s home page, click Product Classifications.
Click the Subclassification tab, and then click New.
In the New Product Classification page, enter the name as Sedan and a unique code.
Set the parent product classification to Cars and the status to Active.
Save your changes.

Repeat this step to create a second subclassification named SUV with the code SUV.

Customize Attributes for Specific Models

Customize the inherited attributes to set specific defaults for each model. For the Sedan, set the standard engine size.

From the Product Classifications list, select the Sedan subclassification.
Go to the Attributes tab.
Next to the inherited Engine Type attribute, click the action menu and select Configure.
In the Default Value field, select 2.5 L.
Save your changes.
Curate Available Options for Each Model

Finally, ensure data accuracy by restricting which options are valid for each model. For example, a Sedan should not be available with a 4.oL engine or in Black color.

Restrict Engine Types for Sedans.
From the Product Classifications list, select the Sedan subclassification.
Go to the Attributes tab.
Select Include or Exclude Picklist Values from the dropdown menu next to Engine Type.
Deselect 4.0 L.
Save your changes.
Restrict colors for sedans.
From the Product Classifications list, select the Sedan subclassification.
Go to the Attributes tab.
Select Include or Exclude Picklist Values from the dropdown menu next to Color.
Deselect Black.
Save your changes.
Configure the SUV model.
Repeat the steps to configure the SUV subclassification to meet its unique requirements.
From the Product Classifications list, select the SUV subclassification.
Exclude 2.5 L and 3.5 L from the Engine Type attribute, leaving only 4.0 L option.
Click the dropdown next to Colors and select Include or Exclude Picklist Values.
Exclude White from the Color attribute.
Save your changes.

You have successfully engineered a product classification hierarchy. Any product record created by using the Sedan classification automatically inherits a restriction to 2.5 L or 3.5 L engines and won’t offer Black as a color option, significantly reducing manual data entry errors. Similarly, any product record created by using the SUV classification automatically inherits a restriction to a 4.0 L engine and won’t offer White as a color option.
