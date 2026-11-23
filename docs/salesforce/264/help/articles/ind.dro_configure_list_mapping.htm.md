---
article_id: ind.dro_configure_list_mapping.htm
title: Configure List Mapping
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_list_mapping.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_define_field_and_attribute_mapping.htm
fetched_at: 2026-11-23
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

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_configure_list_mapping.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
