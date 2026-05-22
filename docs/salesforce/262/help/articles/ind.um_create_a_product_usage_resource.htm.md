---
article_id: ind.um_create_a_product_usage_resource.htm
title: Create a Product Usage Resource
source_url: https://help.salesforce.com/s/articleView?id=ind.um_create_a_product_usage_resource.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Create a Product Usage Resource

Associate existing usage resources with products, with a limit of one token resource per product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To create product usage resource:	Usage Management Designer
From the App Launcher, find and select Product Usage Resource.
Click New.
Select a product created with a usage model type.
Select a usage resource related to the selected product.
Select the effective start date and end date.
The Usage Resource isn't part of the product after the effective end date.
Select a status.
	
Draft	Indicates that the record is still open for modifications. This is the default value.
Active	Indicates that Usage Management is using this record for resource consumption calculations and you can make limited modifications.
Inactive	Indicates that the record isn't in use.
If necessary, select Optional.
The Optional checkbox is applicable only when the selected product is one of the commitment usage model types. Selecting the checkbox indicates that the usage resource is optional and may or may not be included in the commitment-based product.
If necessary, select a token resource.
This token resource is used to charge the selected usage resource.
Save your changes.
