---
article_id: ind.billing_automate_invoice_run_schedules.htm
title: Generate Invoices Automatically Based on Billing Schedules
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_automate_invoice_run_schedules.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_automate_invoice_generation.htm
fetched_at: 2026-09-04
---

# Generate Invoices Automatically Based on Billing Schedules

Set up invoice schedulers to generate invoices on a schedule or on demand. Select billing schedules by target date, billing period count, or both. Generate invoice documents during the run, or use a catch-up bill run to advance migrated schedules without creating invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management


This feature is available with the Revenue Management Advanced license or the Revenue Management Billing license.

The Milestone Billing and Usage-Based Invoicing features are available only with the Revenue Management Billing license. Contact your Salesforce account executive for more information.

USER PERMISSIONS
NEEDED
To create invoice schedulers:	

Billing Admin permission set

OR

Billing Operations User permission set


To generate invoice documents during a batch run:	

Billing Admin permission set OR Billing Operations User permission set

AND

DocGen User permission set

From the App Launcher, find and select Billing Batch Schedulers.
Click New Invoice Scheduler.
Enter a scheduler name.
To advance migrated billing schedules without generating invoices, select Catch-Up Bill Run.
Catch-up bill runs use the Once frequency and require a target date. Because catch-up doesn't generate invoices, the scheduler disables the invoice generation options, such as post invoices, create invoice documents, invoice date, and recurrence. For when to use a catch-up bill run, see Catch-Up Bill Runs.
To initiate a one-time invoice run, select Start run now.
All other scheduling options for the invoice run are hidden when you immediately start the invoice run.
To activate the invoice scheduler, select Active.
Invoices are generated only when the scheduler is active. You can also create invoice schedulers in a draft state and activate them when needed.
Select a start date, start time, and the time zone for the scheduler.
To generate invoices in a posted status, select Post invoices.
If you deselect Post invoices, invoices are created in draft status.
To create invoice PDF documents automatically as invoices are streamed during the batch run, select Generate Invoice Documents.
Select a frequency, then specify the date and period fields that appear.
For when to use each option, see Understand Invoice Date, Target Date, and Billing Period Count.
Once	Enter the target date and invoice date as calendar dates. If Catch-Up Bill Run is selected, frequency is Once and Invoice Date is disabled.
Daily, weekly, or monthly	Billing calculates the target date and invoice date for each invoice batch run. Base Target Date On, Base Invoice Date On, and Invoice Date Offset control those calculated dates. You can also select Exclude holidays and weekends. Holidays are configured in the UTC time zone, and the scheduler must match the time zone. A weekly run also shows the day of the week.
For every frequency, Select billing schedules based on determines whether Billing uses a target date, a billing period count, or a billing period count with an optional target date filter.
Target Date	For a once run, enter Target Date. For a daily, weekly, or monthly run, specify Base Target Date On. Billing selects schedules whose next billing date is on or before the target date.
Billing Period Count	Billing Period Count appears. Each selected schedule is invoiced for that number of periods. Target date fields remain available to filter which schedules are selected for invoicing. For a once run, Target Date is optional. For a daily, weekly, or monthly run, Base Target Date On remains available; those target date fields are optional.
For a daily, weekly, or monthly run, Base Target Date On controls how Billing calculates the target date.
Offset from Run Date	Billing adds Target Date Offset to the date the invoice batch run runs.
Day Of Month	Billing uses Target Day Of Month in the month of the invoice batch run, shifted by Target Month Offset. Target day of month can be 1 through 28, or last, second-to-last, or third-to-last.
For a daily, weekly, or monthly run, Base Invoice Date On controls how Billing calculates the invoice date. Invoice Date Offset appears with either option.
Offset from Target Date	Billing adds Invoice Date Offset to the target date.
Offset from Run Date	Billing adds Invoice Date Offset to the date the invoice batch run runs.
For a monthly run, On controls whether the run uses a weekday cadence or a calendar date.
Every	Cadence (First, Second, Third, Fourth, or Last) and Day (Sunday through Saturday).
Specific Date	Date (1 through 28, or last, second-to-last, or third-to-last).
If needed, for recurring invoice runs, stop the schedule recurrence after a date by selecting the end date.
Click Next.
Select the billing batch to generate invoices for, or filter billing schedules based on your criteria.
The invoice run selects billing batches from the billing schedules based on the invoice run matching criteria. A billing batch includes several invoices that are processed simultaneously during an invoice run.
Select the billing charge type for the invoice.
You can select one or a combination of the charge types. By default, all charge types are selected.
If needed, you can also filter the invoice based on legal entity and customer account.
Select the currency for the invoices. You can select multiple currencies to manage invoicing across different regions and locations.
The billing schedules are filtered based on the selected currency.
Click Schedule.
You can modify the scheduled invoice runs later, provided that the runs are in a draft or inactive state.
IMPORTANT When generating invoices by using the Invoice Creation API or invoice batch runs, implement custom automation on generated invoices as asynchronous processes, such as asynchronous flow paths or asynchronous Apex triggers. Synchronous automation in this context can cause performance issues, timeouts, or failures.

To explore examples to understand how to schedule invoice batch runs based on your requirements, see Examples: Invoice Batch Run Frequencies.

To understand the invoice generation process, see Invoice Batch Run Process.

SEE ALSO
Knowledge Article: Invoice Batch Run Fails When Billing Permission Sets Are Assigned via Permission Set Group
