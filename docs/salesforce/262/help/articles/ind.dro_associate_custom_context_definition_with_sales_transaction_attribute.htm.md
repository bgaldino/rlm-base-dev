---
article_id: ind.dro_associate_custom_context_definition_with_sales_transaction_attribute.htm
title: Map Custom Context Definition with Sales Transaction
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_associate_custom_context_definition_with_sales_transaction_attribute.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Map Custom Context Definition with Sales Transaction

To start using a context definition, you must associate the context definition's newly created attribute with the context field in the sales transaction node.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To associate an attribute with a context field:	

DRO Admin User

Prerequisite: Create Custom Context Definition and Map Attribute to Field.

From Setup, in the Quick Find box, enter Context Definition Settings and select it.
From the Sales Transaction Context Definition header, select the newly created context definition.
From the context nodes list, select the SalesTransaction node, and then map the Context field for the Orchestration Group Key field node to the attribute that you created when you defined the context definition. Map other nodes from the custom context definition to the SalesTransaction nodes as required.

After the setup is complete, you can create and process orders by using the new context definition. The orders must contain the grouping key in the field that you mapped to the Orchestration Group Key. For more information on Orchestration Group Keys, see Cross-Plan Dependencies.
