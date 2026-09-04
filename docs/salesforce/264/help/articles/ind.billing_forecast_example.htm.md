---
article_id: ind.billing_forecast_example.htm
title: "Example: Preview Projected Billing Charges"
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_forecast_example.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_forecast.htm
fetched_at: 2026-09-04
---

# Example: Preview Projected Billing Charges

Explore an example that shows how a billing team reviews subscription charges after an amendment and a cancellation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

Acme Software Innovations provides these products to Growth Digital Marketing Pro.

Analytics Platform, annual subscription, billed yearly at $12,000
User Licenses, monthly subscription, billed monthly at $200
Support Package, monthly subscription, billed monthly at $50

On April 1, 2026, Growth Digital Marketing Pro amends the order to add licenses, which increases the monthly user licenses charge from $200 to $300. On May 1, 2026, they cancel the support package.

The Acme billing team wants to review projected charges through September 1, 2026, and share the upcoming amounts with the account team before invoices are created. They create a billing forecast scheduler, set the target date to September 1, 2026, and run the forecast.

After the Forecast Batch Run completes, they open the Billing Forecast Console.

Total forecasted billings shows the net projected amount for supported one-time and subscription charges through the target date.
Recurring billing contribution shows the subscription amounts from Analytics Platform and User Licenses.
Cancellation impact shows the reduction from the canceled Support Package.

The billing team uses the Billing Forecast Details section to review the forecasted invoice lines by billing period, charge type, and category. Amendment lines show the April license increase, and cancellation lines show the canceled Support Package. They share the projected charges with the account team so the customer knows what to expect.
