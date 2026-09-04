---
article_id: ind.billing_invoice_batch_run.htm
title: Invoice Batch Run Process
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_batch_run.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_automate_invoice_generation.htm
fetched_at: 2026-09-04
---

# Invoice Batch Run Process

Invoice batch runs stream invoices by processing billing schedules in parallel. Track each stage of the invoice batch run to monitor progress and status.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Job Types

Billing Batch Schedulers support Invoice, Catch-Up Bill Run, and Forecast job types. The job type determines whether the run generates invoices, advances billing schedules without invoicing, or creates forecast data.

Invoice—Generates invoices for selected billing schedules. The run is an invoice batch run. See Generate Invoices Automatically Based on Billing Schedules.
Catch-Up Bill Run—Advances billing schedules without generating invoices. See Catch-Up Bill Runs.
Forecast—Creates projected billing forecast data. The run is labeled Forecast Batch Run. See Billing Forecast.

For target date, billing period count, and day-of-month options used when selecting schedules, see Understand Invoice Date, Target Date, and Billing Period Count.

How Invoice Batch Runs Generate Invoices

Invoice batch runs use the Batch Management Service to process billing schedules and generate invoices in parallel. You can start reviewing, sending, and collecting payments on invoices as they’re generated, without waiting for the entire batch to complete.

From the App Launcher, find and select Invoice Batch Runs, and then open the relevant record. To view the related Invoice Batch Draft to Posted Run or Invoice Batch Run Recovery records, go to the Related tab.

To check the overall status and stage of an invoice batch run, check the status subtype on the Invoice Batch Run record. See Status Subtype of Invoice Batch Runs.

To monitor granular progress, select the job ID in the Batch Management Job field to open the corresponding Batch Management Job record. You can view real-time progress, processing status, and any errors. To view the status of all Batch Management jobs, from Setup, find and select Monitor Workflow Services.

The batch management service processes invoice batch runs in these stages.

Identifies billing schedules that meet the criteria defined in the invoice batch run scheduler, such as the next billing date and billing frequency. Each eligible billing schedule is assigned a grouping key
Processes billing schedules simultaneously across multiple threads. Each grouping key is processed independently, so completed invoices are available for review as soon as they're generated
Calculates estimated taxes for draft invoices and actual taxes for posted invoices using the configured tax engine
Updates the amounts and billing dates on associated billing schedules and billing schedule groups in alignment with the generated invoices, to prepare the data for the next billing cycle
Updates the invoice batch run record with a summary of the completed run, including the total number of invoices generated, any failures, and the overall status
Status of Invoice Batch Runs

If an invoice batch run completes successfully, its status changes to Completed. If any errors occur during processing, its status changes to Failed.

Status Subtype of Invoice Batch Runs

To monitor and troubleshoot an invoice batch run, the Billing Operations user can check its status subtype. The status subtype provides visibility into each stage of the invoice batch run. This field isn’t available by default and can be added from the Invoice Batch run object’s page layout settings.

Billing Schedules Filtering Started—The invoice run is preparing to identify the billing schedules to include for invoice generation.
Billing Schedules Filtering In Progress—The invoice run is identifying the billing schedules to include for invoice generation.
Billing Schedules Filtering Completed—The invoice run has identified the billing schedules to include for invoice generation.
Invoice Generation Started—The process of generating invoices has started.
Invoice Generation In Progress—The invoice run is generating invoices for the identified billing schedules.
Invoice Generation Completed—The invoice run has finished generating invoices for the identified billing schedules.
Invoice Generation Summarization In Progress—The summarization of the generated invoices is in progress.
Completed—The invoice batch run has completed successfully. This corresponds to the Completed status of the invoice batch run.
Failed—The invoice batch run has failed.
NOTE Canceling in-flight batch management jobs isn't supported and results in inaccurate data summarization on the Invoice Batch Run record.

In the Invoice Batch Run records, the billing schedule summary is available on the Details tab. If the invoice batch run processes multiple currencies or a currency different from your Salesforce org’s default currency, the total invoiced amount and total draft invoice amount can’t be summarized.

Target Date Offset Limit

By default, the maximum target date for an invoice batch run is 12 months from the current date. If you schedule a batch run with a target date offset greater than 12 months, you receive an error. This limit is an org-level configuration.

Failed Invoice Batch Runs

Review the generated invoices in the Invoices related list. If the invoice generation fails, check the Revenue Transaction Error Logs related list on the Invoice Batch Run records. The log’s Error Message field shows the reason for the failure.

SEE ALSO
Data Processing Engine
Revenue Cloud Developer Guide: InvoiceBatchRun
Monitor Your Batch Jobs
