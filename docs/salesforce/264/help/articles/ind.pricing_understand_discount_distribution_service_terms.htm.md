---
article_id: ind.pricing_understand_discount_distribution_service_terms.htm
title: Understand Discount Distribution Service Terms
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_understand_discount_distribution_service_terms.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_discount_spread_service.htm
fetched_at: 2026-09-07
---

# Understand Discount Distribution Service Terms

Familiarize yourself with the variables and terminology you'll encounter when you configure a pricing procedure to calculate discounts using the Discount Distribution Service element.

Here are the variables that are specific to and important to know when you use the Discount Distribution Service element in your pricing procedure.

VARIABLE	DESCRIPTION
Header Distribution Type	This variable indicates the discount amount to be removed from the ItemNetTotalPrice or NetUnitPrice variable.
Header Discount Type	

This variable indicates the type of discount that can be applied. There are three possible values: Amount, Percentage, and Override.

If you select the Override option, you'll also need to provide a variable for the Header Subtotal. The Header Subtotal variable contains the subtotal amount from which the target discounts are deducted.


Header Distribution Logic	This variable defines the distribution method for the discount. The values you can apply are Equal or Proportionate.
IMPORTANT Map the Input Unit Price input variable when the Net Unit Price variable is mapped (either in the Pricing Setting element or here). If you don't, the service will return an empty value, and as a result, the Waterfall view will display a null value for the Net Unit Price of the line item.

You can control the distribution logic of the discounts as follows:

LOGIC	DESCRIPTION
Equal	In this distribution logic, the discount is applied equally across all line items.
Proportionate	In this distribution logic, the discount applied at the quote level (header) is allocated to individual line items based on their respective list prices. Basically, items with higher values receive a larger portion of the discount compared to those with lower values. This ensures the discount is distributed proportionally to each line item’s contribution to the total quote value.

When you set floor limits, you’ll need to map these tags in the procedure.

VARIABLE	DESCRIPTION
Minimum Net Unit Price	This variable indicates the minimum net unit price that can be set for a line item. No discount can be applied below this price. This must be of currency type.
Total Remainder Amount	This variable stores the remainder amount after applying all the discounts. This must be of currency type.
