---
article_id: ind.pricing_create_constant_resource.htm
title: Create Constant Resources
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_constant_resource.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Create Constant Resources

If your variables lack context tags, create a constant resource to serve as a placeholder for fixed values in your pricing procedures. Constants are used for inputs, outputs, and other values passed from a pricing element.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Salesforce Pricing is enabled
NOTE Salesforce Pricing only supports the creation and use of constant resources.

For example, create a constant for the VolumeBasedAdjustment input variable.

Create a pricing procedure.
On the the Pricing Procedure builder canvas, click .
On the Resource Manager panel, click Add Resource.
Specify the resource type, name, data type, and default values.
When naming constants, use unique identifiers and avoid reserved keywords such as Currency, Number, or Text.
Save your changes.
