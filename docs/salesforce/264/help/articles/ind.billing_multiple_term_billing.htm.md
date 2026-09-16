---
article_id: ind.billing_multiple_term_billing.htm
title: Bill for Multiple Terms in a Billing Period
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_multiple_term_billing.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedules_and_schedule_groups.htm
fetched_at: 2026-09-04
---

# Bill for Multiple Terms in a Billing Period

Your sales reps can now set up flexible terms for billing subscriptions whether it’s every three weeks, every five months, or every two years. For example, to bill a subscription every three months, your sales reps can set the billing frequency to monthly and billing term to 3 on the order product. Billing automatically calculates the correct amount for the combined period and sets the next billing date accordingly.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
NOTE For orgs created in or upgraded to Winter ’27, perform a one-time task of adding the Billing Term Unit field on the Asset Action Source, Order Product, and Quote Line Item page layouts.

Sometimes a customer prefers to be billed for several periods at once, or you want to reduce the number of invoices that you generate. You can set how many billing term units to combine into a single billing period. When you combine multiple terms, Billing generates one billing period item for the combined period and adds one invoice line to the invoice, instead of a separate billing period item and invoice line for each period.

For example, for a monthly billing term unit and a billing term of 3, Billing combines 3 months into one billing period, generates one billing period item that covers all 3 months, and adds a single line to the invoice for that period. The billing period amount equals the unit price multiplied by the quantity and by the number of combined periods.

You can set the billing term on the order product or quote line item. Its default value is 1, which bills each period separately. However, to bill for multiple terms, you can enter a higher value up to 1,200, to combine that number of billing term units into one billing period. For both termed and evergreen products, you can combine multiple terms with weekly, monthly, quarterly, semiannual, and annual billing frequencies. For products that use the one-time selling model, leave the billing term blank or set it to 1.
