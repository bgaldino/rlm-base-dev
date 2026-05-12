---
article_id: ind.qocal_saving_usage_rates_for_quotes_and_orders.htm
title: Saving Usage Rates for Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_saving_usage_rates_for_quotes_and_orders.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Saving Usage Rates for Quotes and Orders

Automatically save current usage rates by generating rate card entries when you save a quote or order. This process helps maintain rate consistency for the duration of the sale, even if the product catalog is updated later.

REQUIRED EDITIONS
NOTE To enable this feature, admins must configure the Revenue Management transaction processing type with RatingPreference set to Fetch. Automatic rate capture does not trigger if you use a different transaction processing type.
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
How Rate Capture Works

To support rate stability, Revenue Management saves usage rates at the beginning of the sales process. This prevents future catalog changes from affecting quotes in progress and helps maintain rate consistency from the quote to the order.

Revenue Management automatically captures catalog rates during the quoting process:

When you save a quote, Revenue Management captures the current catalog rates and generates a Quote Line Rate Card Entry record, which prevents subsequent catalog updates from impacting the quote.
When you successfully order the quote, Salesforce transforms those records into Order Item Rate Card Entry records to maintain the exact rates for the order.
NOTE When you add quote line items from a related list, Revenue Management doesn't create the quote line rate card entries immediately. The entries are created the next time the pricing service is invoked, such as when you edit a quote line item, save the quote, or assetize the quote.
