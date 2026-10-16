---
article_id: ind.um_create_a_usage_product_grant_binding_policy.htm
title: Create Usage Product Grant Binding Policy
source_url: https://help.salesforce.com/s/articleView?id=ind.um_create_a_usage_product_grant_binding_policy.htm&type=5&release=264
release: 264
release_name: Winter '27
area: usage
parent_article: ind.um_configure_usage_records.htm
fetched_at: 2026-09-07
---

# Create Usage Product Grant Binding Policy

Define the association between a usage resource’s grant with a sellable product.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create usage product grant binding policies:	Usage Management Designer
IMPORTANT The binding target can't be changed after the order is activated and assetized. If you configure the wrong binding target for your policy, you must redesign the product from scratch. Verify your choice before activating any orders that use this policy. For guidance on selecting a binding target and understanding how consumption is aggregated across shared grants, see Grant Binding.
From the App Launcher, find and select Usage Product Grant Binding Policies.
Click New.
Enter a name.
Select a sellable product.
Select a grant binding type.
	
Self	Apply the product's usage grant to a single asset so that each purchased product tracks its consumption independently. This is the default for anchor and pack product configurations.
Target	Share usage grants across multiple assets, such as an account, contract, or custom object. This binding type requires an associated grant binding target.
Select a grant binding target if the grant binding type is Target.
	
Product	A sellable product within the Revenue Management to which the grant is to be associated.
Custom	An external product outside the Revenue Management to which the grant is to be associated.
Contract	A specific agreement or service contract within Revenue Management to which the usage grant is to be associated.
Account	A customer or organization within Revenue Management to which the usage grant is to be associated.
Save your changes.
