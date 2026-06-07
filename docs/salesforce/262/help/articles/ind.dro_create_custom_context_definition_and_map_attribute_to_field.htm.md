---
article_id: ind.dro_create_custom_context_definition_and_map_attribute_to_field.htm
title: Create Custom Context Definition and Map Attribute to Field
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_create_custom_context_definition_and_map_attribute_to_field.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Create Custom Context Definition and Map Attribute to Field

Extend a standard definition that you want to inherit all the standard components such as nodes, attributes, and mappings. Then customize the extended definition based on your requirements by adding components to it.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To extend a standard definition:	

DRO Admin User

Prerequisite: Enable Permission for Context Service Users.

To make sure that your nodes and attributes are updated with the right input data, create a mapping structure for your context definition. After you create your context definition, search for objects, and click the node and attribute icons that you want to connect to the object fields to start mapping.

From Setup, in the Quick Find box, enter Context Definitions and select it.
For the SalesTransactionsContext record, click , and select Extend.
Enter a name for the context definition, and click Next.
Under the Sales Transaction node, add an attribute by entering a name, type, and data type. For example, with a Cross Plan dependency scope, enter OrchestrationGroupKey, INPUT OUTPUT , and String respectively.
Click Next, and save your changes.
On the Custom Definition tab, open the newly created context definition to view its details.
On the Map tab, for the mapping record that you want to associate with a field, click , and then select Edit.
To set this mapping as your default mapping, select Mark as default, and then click Map.
The page shows the mapping attributes on the left, and the entity fields on the right.
Click a mapping attribute, and then click the field that you want to map the attribute to.
A line is drawn between the two items to show the mapping.
Save the mapping changes. On the mapping details page, click Activate.
SEE ALSO
Map Custom Context Definition with Sales Transaction
