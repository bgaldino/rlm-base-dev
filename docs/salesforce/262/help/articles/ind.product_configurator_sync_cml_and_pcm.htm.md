---
article_id: ind.product_configurator_sync_cml_and_pcm.htm
title: Sync Constraint Models with Product Definitions
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_sync_cml_and_pcm.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Sync Constraint Models with Product Definitions

Sync product definition changes from Product Catalog Management (PCM) to the constraint modeling language (CML) for a constraint model, to make sure that the CML reflects the latest product definition.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license

In Constraint Builder, use the Sync button to update the product’s CML. Syncing updates data for product components, attributes, and attribute values. This table shows configuration changes in PCM and the result in the constraint model CML when you sync the changes.

CHANGE IN PRODUCT CATALOG MANAGEMENT	RESULT IN CONSTRAINT MODEL CML
Product Component Changes	 
Delete a child product from a bundle	Relation and associations for the relation for the child product are removed from the bundle
Change product cardinality	Cardinality for the product is changed
Set product as required	Cardinality for the product is updated
Attribute Changes	 
Delete a product attribute	Attribute variable is removed
Set attribute to inactive	Attribute variable is removed from the attribute domain
Attribute Value Changes	 
Delete attribute value	Attribute value is removed
Create attribute value	Attribute value is added to the attribute domain
Update default attribute value	If the default value annotation exists in the CML, the default value is updated
Set attribute value to inactive	Attribute value is removed from the attribute domain
Default attribute value added	Default attribute value is added to the attribute domain.
Default attribute value removed	Default attribute is removed from the attribute domain

These changes in PCM don’t sync to the constraint model CML.

Constraint, require, or exclude keywords that contain outdated attribute or product usage
An attribute inside a parent type
Relations inside a virtual container
Product component groups
A product added to or removed from a product class
Changes to attributes or attribute values defined under a product class
Product context tags and their values
Newly added components or attributes
