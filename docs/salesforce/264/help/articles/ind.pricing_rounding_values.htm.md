---
article_id: ind.pricing_rounding_values.htm
title: Apply Price Rounding Values
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_rounding_values.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_pricing_element.htm
fetched_at: 2026-09-07
---

# Apply Price Rounding Values

Precisely calculate the price of your product using Rounding Values in your pricing procedure to ensure accurate pricing amounts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license or the Revenue Cloud Advanced license.

Rounding ensures that financial calculations use the correct number of decimal places for the currency, rounding results up or down based on the applied rounding rule. The rounding rules applied are:

Round Up: This rule rounds the currency value of an item to the nearest higher value. For example, if a pen costs US$1.60, applying this rule adjusts the price to $2.
Round Down: This rule rounds the currency value of an item to the nearest lower value. For example, if a pen costs $1.60, applying this rule adjusts the price to $1.
Half Up: This rule rounds the currency value of an item to the nearest number based on its decimal value. For example, if a pen costs $1.45 and you select the Half Up rule, the price adjusts to $1.50. However, if the pen costs $1.20, the price adjusts to $1.00.

For single-currency orgs, the Rounding Values element sets the rounding precision by using the precision input parameter. If no precision value is passed, the element returns the input value unchanged, without rounding. If multicurrency is enabled, the Rounding Values element ignores the precision input parameter and automatically applies the decimal places defined in your Manage Currencies settings. The element uses the decimal places defined for the currency passed through CurrencyIsoCode context. If CurrencyIsoCode isn't passed, the element automatically applies the decimal places defined for each currency in your Manage Currencies settings. See Manage Multiple Currencies.

In addition to setting overall precision, the Rounding Values element also plays a crucial role in determining the final currency outputs from preceding pricing elements, such as Manual Discount and Volume Discount.

Use the Rounding Values Element
Use the Rounding Values element to ensure that the output of any pricing element in a pricing procedure is rounded to the specified decimal place.
