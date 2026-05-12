---
article_id: ind.product_catalog_set_up_objects_for_pcm.htm
title: Set Up Objects for Product Catalog Management
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_set_up_objects_for_pcm.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Set Up Objects for Product Catalog Management

To complete the setup of Product Catalog Management, adjust the page layout and field access on the product catalog objects.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management
Update the Attribute Definition Page Layout.
From the Object Manager for Attribute Definition, go to Page Layouts.
Click on Attribute Definition Layout.
Drag and drop the related lists to your Attribute Definition page layout.
Related Product Attribute Definitions
Related Product Classifications
Update the Category Page Layout.
From the Object Manager for Category, go to Page Layouts.
Click New button and create a page layout.
Click the name of the new category page layout you created. Add these related lists:
Product Category Qualifications
Product Category Disqualifications
Products
Click Page Layout Assignment button and assign the new layout to System Admin and Standard User.
Save your changes.
Update the Product Page Layout.
From the Object Manager for Product, go to Page Layouts.
Click on Product Layout.
Drag and drop these fields to your product page layout.
Configure During Sale
Based On
Availability Date
Discontinued Date
End Of Life Date
Product SKU
Display URL
Sell Only With Other Products
Is Assetizable
Product Type
Specification Type
Add these related lists to your product page layout.
Categories
Product Selling Model Option
Inherited Attributes
Overridden Inherited Attributes
Product Qualifications
Product Disqualifications
Child Components
Overridden Bundle Components
Overridden Product Component Attributes
Product Component Group
Overridden Product Component Groups
Click on Record Types.
Create these Record Types: Commercial and Technical.
Make them available for all profiles.
Set Commercial as the default record type.
When creating a record type, use the same product layout for all record types.
Update the Product Classification Page Layout.
From the Object Manager for Product Classification , go to Page Layouts.
Click on Product Classification Layout.
Drag and drop the Parent Product Classifiaction field.
Add theses related lists to your product classification page layout
Inherited Attributes
Overridden Inherited Attributes
