---
article_id: ind.um_define_a_product_usage_grant.htm
title: Create a Product Usage Grant
source_url: https://help.salesforce.com/s/articleView?id=ind.um_define_a_product_usage_grant.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Create a Product Usage Grant

Define the details of a grant associated with a resource, product, or service, such as the granted quantity, renewal and rollover policy, and the grant's validity period.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create product usage grants:	Usage Management Designer
From the App Launcher, find and select Product Usage Grants.
Click New.
Enter a unique label for the usage grant.
Select a product usage resource.
Select a drawdown order.
	
Expiring First	Process the consumption of usage resources from the entitlements with the expiration date closest to the current date. This is the default value.
Granted First	Process the consumption of usage resources from the entitlements that were granted first in the set of granted entitlements.
Granted Last	Process the consumption of usage resources from the entitlements that were granted last in the set of granted entitlements.
Enter the quantity in units associated with the grant or commitment.
Select a type.
	
Grant	A discount can be negotiated for the usage resource when the usage resource is associated with an anchor product.
Commit	

A discount can be negotiated for the usage resource when the associated anchor product is committed for a specific quantity, spend, or tokens.

If you select Commit, the usage resource to be associated must be of the Commit category.
Select a unit of measure class.
Select ‌the default unit of measure for the selected unit of measure class.
Select a value that indicates whether the overage is chargeable.
Select a status.
	
Draft	Indicates that this record is still open for modifications. This is the default value.
Active	Indicates that Usage Management is using this record for resource consumption calculations and you can make limited modifications.
Inactive	Indicates that the record is not in use.
If necessary, select a usage definition product and a product selling model.
If necessary, select a refresh policy and a rollover policy.
Select a validity period unit and enter a correspoding validity period term.
Select an effective start date.
Save your changes.
