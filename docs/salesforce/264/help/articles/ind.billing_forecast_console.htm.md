---
article_id: ind.billing_forecast_console.htm
title: Use the Billing Forecast Console
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_forecast_console.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_forecast.htm
fetched_at: 2026-09-04
---

# Use the Billing Forecast Console

Review projected charges across accounts, charge types, and billing periods, and see how cancellations change upcoming amounts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

To view the Billing Forecast Console, you need the Tableau Next Consumer license. Users who create or edit dashboards and semantic models need the Tableau Next Creator license. See Tableau Next Permission Sets and Licenses.

Turn on Billing Forecast and run the forecast scheduler at least once so that forecast data is available. Your org must have Data 360 enabled and connected. See Build your Data Cloud Connection.

After you enable Billing Forecast, deploy the Billing Forecast Console. See Add the Billing Forecast to Data 360.

The console gets Billing Forecast data from Data 360. After a forecast run writes records in your Salesforce org, there can be a delay before those records appear in the dashboard.

From the App Launcher or the Billing app navigation bar, find and select Billing Forecast Console.

Amounts in the dashboard are shown in the Salesforce org default currency. To create a scheduler from the console, click New Billing Forecast Scheduler.

Filters

Use the filters at the top of the dashboard to focus on a specific data.

Date Range: Limit the dashboard to a selected period of projected billing. The default is Next 90 Days.
Legal Entity: Show forecast data for one or more legal entities.
Account: Show forecast data for one or more accounts.
Charge Type: Show forecast data for one or more charge types, such as Recurring or One-Time.
Billing Frequency: Show forecast data for one or more billing frequencies, such as monthly or yearly.
Category: Show forecast data for one or more line categories, such as Original, Amendment, Renewal, or Cancellation.
Summary Cards

The console shows three summary cards.

Total Forecasted Billings: The net projected amount and the number of forecast lines.
Recurring Billing Contribution: The projected amount from termed and evergreen subscriptions, and how many of the total lines are recurring.
Cancellation Impact: The reduction in projected billings from cancellations, and the number of cancelled lines.

The chart shows projected amounts by billing period. Group the amounts by Charge Type, Legal Entity, Currency, or Category. Charge Type is selected by default.

Billing Forecast Details

The details table lists the projected charge lines that make up the dashboard totals for the filters you applied. The heading shows that line count. For each line, you can review billing period, charge type, billing frequency, account, legal entity, quantity, unit price, charge amount, currency, and category.
