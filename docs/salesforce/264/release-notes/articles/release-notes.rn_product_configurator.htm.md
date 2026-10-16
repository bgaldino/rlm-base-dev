---
article_id: release-notes.rn_product_configurator.htm
title: Product Configurator
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_product_configurator.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Product Configurator

Prevent Constraint Rules Engine from altering specified attributes or relations when it satisfies a constraint. Calculate the quantity of child products per instance of the parent product, rather than the quantity of child products across all bundles.

Prevent Constraint Conflicts When Sharing Attributes and Relations
Prevent the constraint engine from altering specified attributes or relations when it satisfies a constraint. Use the guardrails annotation in a constraint to define protections at the constraint level, instead of on individual attributes and relations. Annotating the constraint prevents conflicts with other constraints that share the same elements.
Enforce Per-Bundle Product Requirements Regardless of Order Size
Write constraint rules that validate child product quantities per bundle instance. Previously, when a customer ordered multiple bundles, the constraint engine validated against the total end quantity of child products across all bundles. When you turn on Instance Quantity in Revenue Settings, the engine validates against the per-bundle quantity, so rules that enforce per-bundle quantities succeed.
Optimize Performance for Revenue Management (Release Update)
This update optimizes the Configuration API to speed up processing times in Product Configurator. Enable the test run in a sandbox environment to confirm that the optimizations work with your setup. This update is available starting in Winter ’27.
Let Constraint Rules Assign Child Product Quantities in Bundles
The Constraint Instance Quantity setting directs the constraint engine to calculate child product instance quantities automatically. Use the allowQuantityChange annotation on a constraint model relationship to let constraint rules write the instance quantities of child products. For example, write a rule that sets a child product's quantity based on an attribute of the parent product.
Updates in Default Product Configurator Flow
The Default Product Configurator flow has new attributes. If you cloned the Default Product Configurator flow before Winter ’27, manually map the new attributes in your customized flow, or clone the default flow and apply your customizations again.
Changed Object in Product Configurator
Do more with the updated ProductConfigurationFlow object in Product Configurator.
Changed Connect REST API in Product Configurator
Control what the Configuration API returns by specifying only the fields that your Configurator screen needs. The Configuration API now returns a targeted set of fields in the configurator response.
