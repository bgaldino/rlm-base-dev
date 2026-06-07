---
article_id: ind.billing_automate_invoice_run_schedules.htm
title: Generate Invoices Automatically Based on Billing Schedules
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_automate_invoice_run_schedules.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Generate Invoices Automatically Based on Billing Schedules

Set up invoice schedulers to schedule invoice generation or generate on-demand invoices. Modify the parameters and filter criteria of the invoice scheduler to tailor the invoice run schedules to your needs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Agentforce Revenue Management


This feature is available with the Agentforce Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

The Milestone Billing and Usage-Based Invoicing features are available only with the Agentforce Revenue Management Billing license. Contact your Salesforce account executive for more information.

USER PERMISSIONS
NEEDED
To create invoice schedulers:	

Billing Operations User permission set

Before scheduling invoice runs, make sure that:

At least one user with the System Admin user profile has the Billing Admin permission set and the Data Pipelines Base User permission set. Make sure the required permission sets are assigned directly. The invoice batch run fails when billing permission sets are assigned through a permission set group. See Invoice Batch Run Fails When Billing Permission Sets Are Assigned via Permission Set Group.
Your admin has enabled Data Pipelines.
IMPORTANT

Invoice batch runs can generate a maximum of 2000 invoice lines for an invoice. Since invoice runs use Data Processing Engine, it is crucial to also understand the default limits for Data Processing Engine and Data Pipelines. These underlying limits can impact the overall invoice generation by batch runs.

You can have a maximum of 30 active billing batch schedulers.

From the App Launcher, find and select Billing Batch Schedulers.
Click New Invoice Scheduler.
Enter a scheduler name.
To initiate a one-time invoice run, select Start run now.
All other scheduling options for the invoice run are hidden when you immediately start the invoice run.
To activate the invoice scheduler, select Active.
Invoices are generated only when the scheduler is active. You can also create invoice schedulers in a draft state and activate them when needed.
Select a start date, start time, and the time zone for the scheduler.
To generate invoices in a posted status, select Post invoices.
If you deselect Post invoices, invoices are created in draft status.
Select a frequency.
Depending on the selected frequency, the billing schedules selected for processing and the date stamped on the invoices vary.
Target Date	The billing schedules with the next billing date before this date are picked up for invoicing.
Target Date Offset	The number of days added to or subtracted from the next run date to calculate the target date.
Invoice Date	The date that's stamped on the invoice.
Invoice Date Offset	The number of days added to or subtracted from the target date to generate the invoice date.
Calculate invoice date from run date	Selecting the checkbox calculates the invoice date from the run date by applying the invoice date offset to the run date instead of the target date.
If you select Once as the frequency, specify these values.
Target Date: The billing schedules with the next billing date before the target date are picked up for invoicing.
Invoice Date: The date that's stamped on the invoice.
If you select a Daily, Weekly, or Monthly frequency, specify these values.
Target Date Offset: The number of days added to or subtracted from the next run date to calculate the target date.
Invoice Date Offset: The number of days added to or subtracted from the target date to generate the invoice date.
Exclude holidays and weekends: Selecting the checkbox moves the scheduler's next run date to the following business day if it falls on a company holiday or a weekend.
Calculate invoice date from run date: Selecting the checkbox calculates the invoice date from the run date by applying the invoice date offset to the run date instead of the target date.
If needed, for recurring invoice runs, stop the schedule recurrence after a date by selecting the end date.
Click Next.
Select the billing batch to generate invoices for.
The invoice run selects billing batches from the billing schedules based on the invoice run matching criteria. A billing batch includes several invoices that are processed simultaneously during an invoice run.
Select the billing charge type for the invoice.
You can select one or a combination of the charge types. By default, all charge types are selected.
If needed, you can also filter the invoice based on legal entity and customer account.
Select the currency for the invoices. You can select multiple currencies to manage invoicing across different regions and locations.
The billing schedules are filtered based on the selected currency.
Click Schedule.
You can modify the scheduled invoice runs later, provided that the runs are in a draft or inactive state.

To explore examples to understand how to schedule invoice batch runs based on your requirements, see Examples: Invoice Batch Run Frequencies.

To understand the invoice generation process, see Invoice Batch Run Process.

SEE ALSO
Knowledge Article: Invoice Batch Run Fails When Billing Permission Sets Are Assigned via Permission Set Group
