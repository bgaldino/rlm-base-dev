---
article_id: ind.product_catalog_configure_decimal_support_for_unit_level_prices.htm
title: Configure Decimal Support for Unit-Level Prices
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_configure_decimal_support_for_unit_level_prices.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pcm
parent_article: ind.product_catalog_set_up_product_catalog_management.htm
fetched_at: 2026-09-04
---

# Configure Decimal Support for Unit-Level Prices

Improve pricing accuracy by configuring up to six decimal places for unit-level rate and currency fields. Show precise values for unit prices, list prices, and discounts across product discovery, quote, and order pages. Standard summary and total fields retain their default decimal settings.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To configure decimal support:	Product Catalog Management Designer
From Setup, in the Quick Find box, enter Revenue Settings, and then select Revenue Settings.
Turn on Decimal Places for Unit Price.
Enter the number of decimal places to show in unit-level price fields. The default is 2. Supported values are 2 through 6.
EXAMPLE :

How this setting works:

Trailing zeros are removed: If a price doesn't need the extra decimal places, the system will not pad it with zeros. For example, 2.85 is shown as 2.85, not 2.8500000.
Editing vs. Viewing: When you click a price field to edit it, you see the full, exact value stored in the database. When you click out (view mode), the system applies your decimal display setting.
Nearest rounding rule: If the actual value in your database has more decimal places than your configured Decimal Value the shown number rounds to the nearest decimal (rounding up or down as appropriate).

How the prices appear when the Decimal Value is six.

How This Setting Works
ACTUAL VALUE	DISPLAY VALUE	EXPLANATION
88.12	88.12	No trailing zeros: The system doesn't add extra zeros to reach six decimal places.
88.1	88.10	Minimum decimals enforced: The system requires a minimum of two decimal places, so a zero is added.
88.123456	88.123456	Exact match: The value has exactly six decimal places.
88.1234567	88.123457	Round up: The seventh decimal is seven, so the sixth decimal rounds up.
88.1234564	88.123456	Round down: The seventh decimal is four, so the sixth decimal remains the same.

Here's a list of fields that support the extended decimal value for unit prices, list prices, and discounts across product discovery, quote, and order pages.

Supported Fields
PAGE	FIELDS
Quote	
Applied Discount
Applied Discount Amount
Discount

Quote Line Group	
Discount
Discount Amount
Margin
Margin Amount
Unit Price Uplift

Quote Line Item	
Discount (Amount)
Discount (Percentage)
List Price
Margin Amount
Net Unit Price
Partner Discount Percent
Partner Unit Price
Unit Cost
Sales Price
Unit Price Uplift

Order	
Applied Discount
Applied Discount Amount
Discount Percent

Order Item Group	
Discount
Discount Amount
Margin
Margin Amount
Unit Price Uplift

Order Item	
Discount (Amount)
Discount (Percentage)
List Price
Margin
Margin Amount
Gross Unit Price
Net Unit Price
Pro Forma Billing Period Amount
Partner Unit Price
Partner Discount Percent
Unit Cost
Reference Price
Unit Price Uplift
