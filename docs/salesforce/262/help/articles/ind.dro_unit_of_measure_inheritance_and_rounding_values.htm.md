---
article_id: ind.dro_unit_of_measure_inheritance_and_rounding_values.htm
title: Unit Of Measure Inheritance and Rounding Values
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_unit_of_measure_inheritance_and_rounding_values.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Unit Of Measure Inheritance and Rounding Values

During decomposition, the fulfillment order product inherits the unit of measure from the related technical product. During technical assetization, the fulfillment asset inherits the unit of measure from the corresponding fulfillment order line item.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Quantity values are rounded off in both fulfillment order line items and fulfillment assets, based on the Dynamic Revenue Orchestrator's (DRO) Unit Of Measure (UOM) scale and rounding rules. See Decimal Quantity Support in Product Catalog Management.

When multiple commercial products with different UOMs decompose into a single technical product that uses the Aggregate quantity calculation method, the system sums up the quantity values of the commercial products without converting them to the technical product's UOM. The summed quantity is then applied to the fulfillment order product.

IMPORTANT

Make sure that you convert all quantities of each commercial product to match the corresponding technical product's UOM before you submit the order to DRO.
