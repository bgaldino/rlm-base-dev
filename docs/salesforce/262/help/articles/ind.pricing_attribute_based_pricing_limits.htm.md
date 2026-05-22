---
article_id: ind.pricing_attribute_based_pricing_limits.htm
title: Attribute-Based Pricing Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_attribute_based_pricing_limits.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pricing
fetched_at: 2026-05-12
---

# Attribute-Based Pricing Limits

Keep these guidelines in mind when configuring attribute-based adjustments.

When you configure adjustments by using numeric data types (Number, Currency, Percentage) or number picklists, the pricing engine automatically stores whole numbers with a decimal (for example, 10 is stored as 10.0). For the configurator to successfully match the attribute and apply the discount at run time, the input value must explicitly include the ‘.0’. If you pass a whole number without the decimal, the adjustment doesn't apply.
While attribute-based pricing supports picklists for all other data types, you can't use a picklist with a Boolean data type (for example, mapping custom text like "Available" or "N/A" to true or false values). If you try to save an adjustment configured with a Boolean picklist, you get a design-time error. Instead, create an attribute of type Checkbox or Boolean.
When configuring price-impacting attributes, use only attributes that belong directly to the selected product classification (or subclassification). While attributes inherited from a parent product classification can appear in the configuration UI, selecting them causes a validation error when you save the adjustment.
