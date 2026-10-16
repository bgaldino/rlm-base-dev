---
article_id: release-notes.rn_product_configurator_allowQuantityChange.htm
title: Let Constraint Rules Assign Child Product Quantities in Bundles
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_product_configurator_allowQuantityChange.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_product_configurator.htm
fetched_at: 2026-09-30
---

# Let Constraint Rules Assign Child Product Quantities in Bundles

The Constraint Instance Quantity setting directs the constraint engine to calculate child product instance quantities automatically. Use the allowQuantityChange annotation on a constraint model relationship to let constraint rules write the instance quantities of child products. For example, write a rule that sets a child product's quantity based on an attribute of the parent product.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

How: In a CML constraint model, add @(allowQuantityChange = true) to a relationship declaration. Then write constraint rules in the parent type that assign the instance quantity of child products in that relationship. To use the allowQuantityChange annotation, turn on Constraint Instance Quantity in Revenue Settings. Set the split annotation to false for the child product in the relationship.

SEE ALSO
Revenue Management Developer Guide: allowQuantityChange Annotation
Enforce Per-Bundle Product Requirements Regardless of Order Size
