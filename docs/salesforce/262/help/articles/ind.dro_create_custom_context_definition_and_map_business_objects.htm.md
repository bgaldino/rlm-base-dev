---
article_id: ind.dro_create_custom_context_definition_and_map_business_objects.htm
title: Create Custom Context Definition and Map Business Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_create_custom_context_definition_and_map_business_objects.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Create Custom Context Definition and Map Business Objects

Extend a standard context definition where you want to inherit all the standard components such as nodes, attributes, and mappings. Then add components to the extended context definition based on your business requirements.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management
USER PERMISSIONS NEEDED
To extend a standard definition and to map attributes to fields:	

DRO Admin User

Prerequisite: Enable permission for context service users.

To make sure that your nodes and attributes are updated with the right input data, create a mapping structure for your context definition. After you create your context definition, search for objects, and click the node and attribute icons that you want to connect to the object fields to start mapping.

From Setup, in the Quick Find box, enter Context Definitions and select it.
For the SalesTransactionsContext record, click , and select Extend.
Enter a name for the context definition, and click Next.
Save your changes.
On the Custom Definition tab, open the new context definition.
For the OrderEntitiesMapping record, click , and select Clone.
Save the new mapping by entering a name and for the new mapping record, click , and then select Edit sObject Mapping.
To set this mapping as your default mapping, select Mark as default, and then click Map.
The page shows the mapping attributes on the left, and the entity fields on the right.
Delete these field mappings between the Sales Transaction node and the Order object by using the Delete icon: Order, OrderAction, OrderItem, OrderItemAttribute, OrderItemDetail, OrderItemGroup, OrderItemRecipient, OrderItemRelationship, and OrderItemTaxLineItem.
In the Connect Objects section on the right, click Add, find and select the business process object that you want to orchestrate, and save your changes.
To map the Sales Transaction node attributes with the new business process object fields, click a mapping attribute, and then click the field that you want to map the attribute to.
IMPORTANT You must delete the default mapping where the OrderID attribute of the FulfillmentTransaction node is mapped to the OrderID field in the FulfillmentOrder object. Then, if the FulfillmentOrder object already has a field that references the business object, map the FulfillmentTransaction node's OrderID attribute to that field. Otherwise, create a custom field on the FulfillmentOrder object and map the OrderID attribute to that field.
For information on the expected context structure and mapping from sales transactions to objects like order and quote, see Dynamic Revenue Orchestrator Context.
For information on mapping sales transactions to your business process object, see Extend Sales Transaction Context Definition.
Save the mapping changes. On the mapping details page, click Activate.
From Setup, in the Quick Find box, enter Context Definition Settings and select it.
In the Sales Transaction Context Definition section, select the new context definition and configure the context nodes that are used to orchestrate the business process.
Save your changes.
SEE ALSO
Configure Procedure Plan Definition for Business Process Orchestration
