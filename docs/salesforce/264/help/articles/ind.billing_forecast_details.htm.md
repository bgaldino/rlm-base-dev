---
article_id: ind.billing_forecast_details.htm
title: Generated Forecast Details
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_forecast_details.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_forecast.htm
fetched_at: 2026-09-04
---

# Generated Forecast Details

Each Billing Forecast record shows a projected charge from a forecast run, including the related Forecast Batch Run and Forecast Status.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.

From the App Launcher, find and select Billing Forecast. You can also review related Billing Forecast records from the Billing Schedule, Billing Schedule Group, Invoice Batch Run, Order, Quote, and Account record pages.

Each Billing Forecast record is associated with a Forecast Batch Run, the run that created the record. Open that run from the Billing Forecast record, from the scheduler in Billing Batch Schedulers, or from Invoice Batch Runs.

Forecast Status on the billing schedule shows where the schedule is in the forecast process.

Pending Forecast: The schedule is queued for a forecast run.
Processing: A forecast run is in progress for the schedule.
Forecasted: The schedule reflects current forecast data.
Error: The forecast run failed for the schedule.

Use last forecast run target date on the billing schedule to see the target date from the most recent forecast run that processed the schedule. The next forecast run also includes billing schedules in error, and schedules whose last forecast run target date is earlier than this run’s target date.

If Forecast Status remains Processing after a run fails, see Recover Billing Schedules.

NOTE The Legal Entity Accounting Period field on Billing Forecast isn’t populated automatically. Set the value on the Billing Forecast record, or use your own automation to populate it.

When a forecast run processes a billing schedule, it replaces that schedule’s Billing Forecast records starting with the earliest billing period the run generates. Forecast lines for earlier billed periods stay. Billing schedules that aren’t included in the run, or that have Forecast Status set to Error, keep their existing Billing Forecast records. Running the same forecast twice doesn’t create duplicate records.

If you generate a draft invoice for a charge that’s already in Billing Forecast, Forecast Status doesn’t change, and the existing forecast line stays. That line remains until you post the invoice and a later forecast run processes the billing schedule.

When you post an invoice or change the billing schedule, billing schedule group, billing arrangement, billing profile, or account, the system sets Forecast Status to Pending Forecast. Posted invoices show amounts already billed, and Billing Forecast shows projected amounts. After you post an invoice, the related forecast line can still appear until the next forecast run processes that billing schedule.
