---
article_id: ind.product_catalog_extend_productdiscoverycontext_context_definition.htm
title: Extend the ProductDiscoveryContext Context Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_extend_productdiscoverycontext_context_definition.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Extend the ProductDiscoveryContext Context Definition

To add the nodes, attributes, mappings, and tags for your qualification procedure, extend the ProductDiscoveryContext context definition.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS
NEEDED
To extend context definitions:	Context Service Admin

Product Catalog Management provides a Product Discovery Context Definition template for you. However, you can't edit this out-of-the-box template. Instead you must extend the context definition to make a version that you can customize.

NOTE

Extend context definitions instead of cloning them. When you extend a context definition, you can use the Sync option to easily upgrade the extended definitions to their latest version. Extending a context definition also ensures that all the mandatory mappings are preserved.

Before you extend the built-in context definition, check to see if there's an extended context definition you can use. Some organizations already have a customizable context definition called BrowseProductsCtxDefinition. If so, you can simply customize the existing context definition.

To extend the Product Discovery Context Definition, follow these instructions:

From Setup, in the Quick Find box, enter Context Service, and then select Context Definitions.
On the Standard Definitions tab, click  corresponding to ProductDiscoveryContext, and then select Extend.
See Extend Context Definition.
Enter a name, ensure that ProductDiscoveryContext is selected in the Inherited From field, and click Next.
If you don’t need to map the attributes in the CategoryProduct node to Product object fields, use the default mapping. To map the attributes in the CategoryProduct node to Product object fields, create a custom mapping.
On the Map Data tab, click Add Mapping.
Enter a name and description.
Ensure that the Automatic Salesforce object mapping and the Mark as Default checkboxes are deselected.
On the Mapping Intent Details page, ensure that Association, Hydration, Persistence, and Translation are selected.
Click Map.
Map CategoryProduct attributes to Product fields.
Save the changes.
On the Map Data tab, from the Context Definition dropdown of the new mapping, select Input Mapping.
Click Generate All Mappings.
In the Generate all mappings? window, click Retain and Generate.
Save the changes.
Click  corresponding to ProductDiscoveryMapping, and then click Edit.
Deselect Mark as Default.
Click  corresponding to the new mapping, and then click Edit.
Select Mark as Default.
Add the nodes and attributes that are required for qualification or disqualification of products and categories.
See Create Context Definitions.
IMPORTANT To use object mapping, make sure that the node has an “id” attribute and a corresponding unique tag.
Map the nodes and attributes to the corresponding entities and fields.
See Add Context Mapping.
Activate the context definition.

Update the context definition in:

Product Discovery Pricing Procedures
Qualification Rule Procedure
Product Discovery Settings
SEE ALSO
Trailhead Module: Context Service Basics
