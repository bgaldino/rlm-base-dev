---
article_id: ind.billing_automate_invoice_generation.htm
title: Automated Invoice Generation with Invoice Batch Runs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_automate_invoice_generation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_invoice_generation.htm
fetched_at: 2026-09-04
---

# Automated Invoice Generation with Invoice Batch Runs

Schedule invoice batch runs to automate invoice generation. These runs use Data Processing Engine to generate invoices.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Understand Invoice Date, Target Date, and Billing Period Count
Before you schedule invoice batch runs, learn how invoice dates are determined, how billing schedules are selected, and how many billing periods are processed for each schedule. You can also process a specific number of billing periods without relying on a target date.
Catch-Up Bill Runs
Use a catch-up bill run to advance the next billing date, billed amount, and pending amount on billing schedules for transactions that a legacy system fully or partially billed. Catch-up doesn’t create invoices for those periods.
Generate Invoices Automatically Based on Billing Schedules
Set up invoice schedulers to generate invoices on a schedule or on demand. Select billing schedules by target date, billing period count, or both. Generate invoice documents during the run, or use a catch-up bill run to advance migrated schedules without creating invoices.
Convert Automations to Asynchronous for Invoice Batch Runs
Identify active flows and Apex triggers on Billing objects and convert them to asynchronous processes before you schedule an invoice batch run. Synchronous automations can stop a run or leave invoices in Draft In Progress, Posting In Progress, or Error.
Examples: Invoice Batch Run Frequencies
Explore examples to understand how to schedule invoice batch runs based on your requirements.
Invoice Batch Run Process
Invoice batch runs stream invoices by processing billing schedules in parallel. Track each stage of the invoice batch run to monitor progress and status.
