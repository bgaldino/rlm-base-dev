---
article_id: ind.billing_forecast_schedule.htm
title: Schedule Billing Forecast Runs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_forecast_schedule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_forecast.htm
fetched_at: 2026-09-04
---

# Schedule Billing Forecast Runs

Create a billing forecast scheduler to run forecasts once or on a recurring schedule, then filter the billing schedules to include, similar to the invoice scheduler.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To create and manage forecast schedules:	

Billing Operations User permission set

OR

Billing Admin permission set

Before you start, turn on Billing Forecast. Billing schedules and billing schedule groups must exist for the charges you want to forecast. Add Billing Forecast to Data 360 to view the Billing Forecast Console. See Turn On Billing Forecast and Add the Billing Forecast to Data 360.

From the App Launcher, find and select Billing Batch Schedulers.
Click New Billing Forecast Scheduler.
Enter a scheduler name.
To start a one-time forecast run immediately, select Start run now. Otherwise, configure the start date, start time, time zone, and frequency.
To activate the scheduler, select Active.
Configure the target date, and any other schedule parameters that apply to your run.
For Billing Forecast, you can set a target date up to 5 years. Target date is required for every forecast schedule. Invoice date and date offsets aren’t used for Billing Forecast. These options otherwise work similarly to invoice schedulers. See Understand Invoice Date, Target Date, and Billing Period Count.
Optionally, select Recalculate All Forecast Lines.
This option that’s supported for Once frequency includes filtered billing schedules regardless of forecast status, and recalculates and overwrites existing forecast data. Use it when you need a complete refresh of forecasted data. This option isn’t selected by default, allowing for a faster incremental calculation for billing schedules where Forecast Status is Pending Forecast.
Click Next.
Filter billing schedules by criteria such as billing batch, charge type, legal entity, billing profile, or currency.
NOTE Billing Forecast doesn’t apply to milestone charges or usage charges. Those schedules are excluded even when Recalculate All Forecast Lines is selected.
Click Schedule.

When the forecast run completes, Billing Forecast records are available to review. From the App Launcher, find and select Billing Forecasts, and open a record. Open the related run from the scheduler in Billing Batch Schedulers. Billing Forecast runs also appear in Invoice Batch Runs with Job Type as Forecast. You can also review results in the Billing Forecast Console.

Forecasts cover projected charges for supported one-time and subscription billing schedules. Forecast amounts are calculated before tax and before credit memos or debit memos.

IMPORTANT Don’t run an invoice batch run, a forecast run, or a catch-up bill run while another of these runs is in progress. Overlapping runs can produce inaccurate forecast data. You can still generate invoices while a forecast run is in progress.
NOTE

To check the progress of a forecast run, open the Forecast Batch Run, then click a job ID in the Batch Management Job field. To view all Batch Management jobs, from Setup, find and select Monitor Workflow Services.
