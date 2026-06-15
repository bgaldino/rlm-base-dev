---
article_id: ind.rm_rate_card_entries.htm
title: Rate Card Entries
source_url: https://help.salesforce.com/s/articleView?id=ind.rm_rate_card_entries.htm&type=5&release=262
release: 262
release_name: Summer '26
area: rating
fetched_at: 2026-05-11
---

# Rate Card Entries

Use rate card entries to set rates and rate adjustments that are used to calculate and control the final net rate of each usage resource. The setup ensures that your deals are accurately rated. To make sure products are accurately charged during usage selling, define the pricing for your products in both standard currency and tokens.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management Advanced

You can configure Rate Card Entries (RCEs) by using either a currency or tokens. However, the Product Usage Resource (PUR) settings for a sellable product determine which rate (currency or token-based) is used during the Usage Selling process. Make sure your PUR configuration aligns with how you want to price the product for sale.

For tokens, create two Rate Card Entries (RCEs).

To convert usage to tokens, make sure the Rate Unit of Measures is the token unit.
To convert tokens to currency, make sure the Rate UoM is the currency.
Create a Rate Card Entry for Base Rate Cards
Define a per-unit rate applicable to the usage resource. When creating a new rate card entry for Base Rate Cards, you define the per-unit rate that will be applied to the usage resource. This per-unit rate specifies the cost or charge for each unit of the resource consumed.
Create a Rate Card Entry For Tier Rate Cards
Define different tiers of consumption for a usage resource and set a rate for each of these tiers. With tier-based adjusted rates, provide discounts to customers who have varying consumptions.
