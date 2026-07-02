---
article_id: ind.rm_external_objects_used_in_rate_management.htm
title: External Objects Used in Rate Management
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_external_objects_used_in_rate_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# External Objects Used in Rate Management

Rate management is part of a larger suite of products under Agentforce Revenue Management. Because these products are closely integrated, rate management uses several objects that belong to other products within Industries and Agentforce Revenue Management.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license

Here’s the list of the external objects used in Rate Management and their descriptions.

OBJECT	DESCRIPTION
Usage Resource	An entitlement or service that’s granted with the product sold to your customer. Typically, usage resources are consumables, such as data storage or computing power. Customers are charged based on the quantity that they use over the granted limit or specified period.
Product	Any item or service sold to your customer. To create products, see Products.
Product Classification	A template that you use to create similar products. Typically, products that are based on a product classification inherit all attributes of the product classification. To create product classifications, see Product Classifications.
Attribute Definition	A product has characteristics or properties known as attributes. You can use attributes to determine or calculate discounts. To create attributes, see Dynamic Attributes.
Attribute Based Adjustment	An attribute-based discount for a product within a date range. See Attribute Based Adjustments.
Product Selling Model	Define how you sell your products through product selling models. You can sell products one time or through subscription plans. To create a product selling model, see Product Selling Model.
Unit of Measure Class	A standard unit of measure dimension, such as currency, volume, or length.
Unit of Measure	A unit of measure that rates are defined in, such as USD or EUR.
Price Book	A list of products and their prices. See Manage Price Books.

To view the list of objects that rate management supports, see the Rate Management object documentation.

In addition to other Industries and Agentforce Revenue Management objects, Rate Management relies on the use of decision tables. Decision tables are complex lookup tables that read business rules with multiple inputs and return multiple outputs. See Decision Table.
