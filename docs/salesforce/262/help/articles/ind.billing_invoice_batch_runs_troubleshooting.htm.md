---
article_id: ind.billing_invoice_batch_runs_troubleshooting.htm
title: Troubleshoot Invoice Batch Run Errors
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_invoice_batch_runs_troubleshooting.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Troubleshoot Invoice Batch Run Errors

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Troubleshoot Invoice Batch Run Errors

Get tips for resolving Invoice Batch Run errors.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
ERROR	REASON	RESOLUTION
Invoices remain stuck in the Started status.	The batch jobs for the Filter Billing Schedules for Generating Invoices DPE definitions are stuck in the Submitted status.	In Setup, find and select Monitor Workflow Services. Cancel these batch jobs and schedule a new invoice batch run.
Invoice batch runs fail to generate invoices.	The batch jobs for the Filter Billing Schedules for Generating Invoices DPE definitions fail because the Integration User is frozen.	Unfreeze the Analytics Integration User with the Analytics Cloud Integration User profile. See Freeze or Unfreeze Users.
Invoices remain stuck in Draft In Progress, Posting In Progress, or Error status.	The batch jobs for the Generate Invoices for Billing Schedules DPE definitions fail because custom flows or triggers that are running in parallel prevent the progress of the invoice batch run.	

Review and correct any custom flows or triggers that are running in parallel with the invoice batch run. Then, recover billing schedules and generate new invoices by completing these steps.

In the invoice batch run, click Recover to cancel all invoices that are stuck in the Draft In Progress status and recover the associated billing schedules.
As a test, generate a new invoice for a billing schedule by using Invoice Creation API. If the invoice is generated successfully without any errors, run the invoice batch run again to generate new invoices.
Optionally, you can delete the old invoices that were stuck in Draft In Progress or Posting in Progress status as they’re now canceled after recovery.
