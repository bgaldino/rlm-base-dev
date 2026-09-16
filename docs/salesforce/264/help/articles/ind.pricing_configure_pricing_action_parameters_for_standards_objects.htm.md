---
article_id: ind.pricing_configure_pricing_action_parameters_for_standards_objects.htm
title: Configure Pricing Parameters for Standard Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_configure_pricing_action_parameters_for_standards_objects.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_get_ready_to_create_pricing_actions.htm
fetched_at: 2026-09-07
---

# Configure Pricing Parameters for Standard Objects

To ensure that the standard pricing action button functions properly, define pricing parameters that connect it to a context definition, the context's mapping, and the pricing procedure for calculating product prices.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To create pricing parameters:	

Salesforce Pricing Admin

IMPORTANT This prerequisite is only applicable to the objects that have the standard pricing actions. The objects are Quote, Order, Contract, Case, and Opportunity.
From Setup, in the Quick Find box, enter Pricing Action Parameters, and then select Pricing Action Parameters.
On the Pricing Action Parameters page, click New.
Specify these details.
Select the object name. 
The list of objects displayed here are the standard objects supported by Salesforce Pricing (Quote, Order, Contract, Case, Opportunity).
Select the context definition. 
You must select an extended context definition. This context definition must have nodes, attributes, and tags. To extend base context definition, see Context Definitions.
Select context mapping. 
Map the tags to the correct Salesforce objects. To prevent pricing calculation errors, select a mapping that matches your target object type.
Select the pricing procedure that performs the pricing policies.
Set the date range. The Effective From date specifies the date and time from when the pricing parameter is applied to an object. The Effective To date is optional.
Save your changes.
