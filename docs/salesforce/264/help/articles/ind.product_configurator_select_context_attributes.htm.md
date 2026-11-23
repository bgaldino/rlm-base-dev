---
article_id: ind.product_configurator_select_context_attributes.htm
title: Select Context Attributes to Improve Configurator Performance
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_select_context_attributes.htm&type=5&release=264
release: 264
release_name: Winter '27
area: configurator
parent_article: ind.product_configurator_set_up_flow.htm
fetched_at: 2026-11-23
---

# Select Context Attributes to Improve Configurator Performance

Select specific context attributes that you want the Configuration API to query and return, instead of it returning all of them by default. Your selection narrows the query and the response to the data that your configurations need, so Product Configurator responds faster, even for large transactions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
USER PERMISSIONS NEEDED
To create and edit a product configuration flow:	Product Configurator

If you don't select any context attributes, the Configuration API continues to query all context attributes. Your existing flows keep working with the same performance as before.

From Setup, in the Quick Find box, enter Flow, and then select Flows.
Open your product configurator flow.
Edit the screen element and select the Product Configurator Data Manager component.
For the Context Definition attribute, select the context definition that defines the data structure for the Configuration API to query. The context definition determines which context nodes and attributes you can select.
For the Context Node attribute, select a context node that contains context attributes for the Configuration API to query. You can select context attributes from multiple nodes as needed. Your selections persist when you switch nodes.
In the Context Attributes section, from the Available Attributes list, select the context attributes that you want the Configuration API to query. To improve performance, select only the attributes that you need.
NOTE Context attributes that are essential to the user interface functionality are preselected and locked.
Repeat steps 5 and 6 for every context node that you want to select attributes from.
Save your changes and activate the flow.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.product_configurator_select_context_attributes.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
