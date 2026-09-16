---
article_id: ind.pricing_limits.htm
title: Salesforce Pricing Limits
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_limits.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_salesforce_pricing.htm
fetched_at: 2026-09-07
---

# Salesforce Pricing Limits

Review the default limits for Salesforce Pricing’s components and their usage. To modify the set default values, ask your Salesforce administrator to raise a support ticket.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.
Discovery Procedures
VALUE	DEFAULT	MINIMUM	MAXIMUM
The number of discovery procedures in an org	2000	1	10000
The duration that a discovery procedure can remain active	10 seconds	1 second	60 seconds
Pricing Procedures
VALUE	DEFAULT	MINIMUM	MAXIMUM
The number of pricing procedures in an org	2000	1	10000
The duration that a pricing procedure can remain active	1 minute	1 second	2 minutes
Pricing Elements
VALUE	DEFAULT	MINIMUM	MAXIMUM
The number of pricing elements in a discovery procedure	50	2	100
The number of pricing elements in a pricing procedure	200	2	200
The duration that a pricing element can remain active	60 seconds	4 milliseconds	80 seconds
The number of mappings the Map Line Item element can have	70	-	100
The number of context tag mappings the Assignment element can have	20	-	50
Price Impacting Attributes
VALUE	DEFAULT	MINIMUM	MAXIMUM
The number of price impacting attributes that can be associated with a product in an org	25	1	50
Contributing Products or Assets
VALUE	DEFAULT	MINIMUM	MAXIMUM
The number of products that can be associated with a contributing product in an org	40	1	

50

This limit is the total number of contributors for a derived product. Both Transactional and Non Transactional


The number of assets that can be associated with a contributing asset in an org	-	-	50
Other Limitations
Pricing procedures don't support the children of sibling nodes for any context definition. For example, in the Sales Transaction context, children or descendants of a sibling node, Sales Transaction Item aren’t supported.
Pricing element functionality is restricted to context tags at the Transaction Item and Transaction Header levels. Descendant and sibling node attributes are unsupported.
For values of the Number data type that are 10,000,000 or greater, the Connect REST API returns standard decimal notation instead of scientific notation. For example, the API returns 10000000 instead of 1.0E7. Additionally, standard decimal values do not include a trailing .0. For example, the API returns 10000000 instead of 10000000.0.
The Invocable Headless API returns values smaller than 0.000001 in scientific notation, while other Connect REST API endpoints return them in standard decimal notation
For stored values with trailing zeros, the API always returns the value at its full stored precision. For example, as 10.000 instead of trimming the zeros to 10.0.
