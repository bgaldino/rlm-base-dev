---
article_id: ind.dro_configure_list_mapping.htm
title: Configure List Mapping
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_list_mapping.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Configure List Mapping

Use list mapping to set up pairs of source and destination values. For example, a list of cities that pair with post code values. When the source value is a city name, the target receives the post code of that city. Configure list mapping from the Fields & Attribute Mapping section of a decomposition rule.

REQUIRED EDITIONS
Available in: Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To configure a list mapping:	

Fulfillment Designer

OR

DRO Admin

Before you begin, review the initial mapping set up steps in Define Field and Attribute Mapping.

Create a Field & Attribute Mapping within a Decomposition Rule.
For Mapping Type, select List Mapping.
Select New List.
You can also use an existing list.
NOTE If you use an existing list, then any change you make for this mapping affects all other mappings that use the same list.
Name the list and click Add Row.
In the source product column, click  and enter a value that you expect to be in the source product.
NOTE Boolean attribute types don't work with list mapping.
Add more rows as required. Don't add duplicate source values to a list.
Save your work.
EXAMPLE

A source commercial product has the attribute Speed with two values: Fast and Ultra Fast.

The target technical product has a Bandwidth attribute with two values: 50 Mbps and 100 Mbps.

Create a mapping so that if the source product has a Speed value of Fast, then the target product has a Bandwidth value of 50 Mbps. And if the Speed is Ultra Fast, then the Bandwidth is 100 Mbps.

When a user submits an order with a speed attribute of Fast, the Broadband attribute gets the value of 50 Mbps.
