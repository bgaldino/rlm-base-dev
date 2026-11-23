---
article_id: ind.pricing_create_constant_resource.htm
title: Create Constant Resources
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_create_constant_resource.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_get_ready_to_build_pricing_procedures.htm
fetched_at: 2026-11-23
---

# Create Constant Resources

If your variables lack context tags, create a constant resource to serve as a placeholder for fixed values in your pricing procedures. Constants are used for inputs, outputs, and other values passed from a pricing element.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
NOTE Salesforce Pricing only supports the creation and use of constant resources.

For example, create a constant for the VolumeBasedAdjustment input variable.

Create a pricing procedure.
On the the Pricing Procedure builder canvas, click .
On the Resource Manager panel, click Add Resource.
Specify the resource type, name, data type, and default values.
When naming constants, use unique identifiers and avoid reserved keywords such as Currency, Number, or Text.
Save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.pricing_create_constant_resource.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
