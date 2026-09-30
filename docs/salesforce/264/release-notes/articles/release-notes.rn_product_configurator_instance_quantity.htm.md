---
article_id: release-notes.rn_product_configurator_instance_quantity.htm
title: Enforce Per-Bundle Product Requirements Regardless of Order Size
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_product_configurator_instance_quantity.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_product_configurator.htm
fetched_at: 2026-09-30
---

# Enforce Per-Bundle Product Requirements Regardless of Order Size

Write constraint rules that validate child product quantities per bundle instance. Previously, when a customer ordered multiple bundles, the constraint engine validated against the total end quantity of child products across all bundles. When you turn on Instance Quantity in Revenue Settings, the engine validates against the per-bundle quantity, so rules that enforce per-bundle quantities succeed.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions of Revenue Management, formerly Revenue Cloud, with the Revenue Cloud Growth or the Revenue Cloud Advanced license.

SEE ALSO
Salesforce Help: Calculate End Quantity and Instance Quantity in Bundled Products
Revenue Management Developer Guide: Proxy Variables with Constraints on Types and Relationships
