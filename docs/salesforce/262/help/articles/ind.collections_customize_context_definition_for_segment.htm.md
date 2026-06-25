---
article_id: ind.collections_customize_context_definition_for_segment.htm
title: Clone and Customize the Prebuilt Context Definition for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_context_definition_for_segment.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_customize_bre_components_to_determine_segment.htm
fetched_at: 2026-06-21
---

# Clone and Customize the Prebuilt Context Definition for Collections and Recovery

To pass the context of a Collection Plan record to related Business Rules Engine components to determine the collection plan segment, clone and customize the prebuilt context definition, CollectionPlanSegmentContext.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To clone and customize context definitions:	Context Service Admin
From Setup, in the Quick Find box, find and select Context Definitions.
Click the dropdown arrow next to the CollectionPlanSegmentContext context definition, and then select Clone.
Enter a name and save the definition.
The predefined node and its fields are cloned.
Edit the custom context definition that you cloned.
Click the Custom Definitions tab.
Click the dropdown arrow next to the cloned context definition, and click Edit.
If necessary, modify the context definition details, and then click Next.
If necessary, modify the predefined attributes under the Collection node.
Click Add Attributes.
Specify the attribute details such as attribute name, type, data type, display name, and description.
Click Next.
Under the Collection node, add or modify context tags, if necessary.
Save your changes.
To persist data by transferring extracted data from cache to collection plan record fields, map the cloned context definition's node and its fields to the Collection Plan object fields.
Click the cloned context definition.
Click Map Data.
On the Mapping Intent Details tile, select at least one Mapping Intent operation.
To begin the mapping, click Map.
You’re directed to Context Mapping’s builder page to begin mapping your nodes and attributes. You can map the Collection Plan fields to the predefined and user-defined fields.
Map the context definition's node with the Collection Plan object, and map the node attributes with the collection plan fields.
Add the context mapping
Save your changes.
To activate your context definition, click the dropdown arrow next to the context definition that you cloned and customized, and select Activate.
