---
article_id: ind.billing_catch_up_bill_runs.htm
title: Catch-Up Bill Runs
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_catch_up_bill_runs.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_automate_invoice_generation.htm
fetched_at: 2026-09-04
---

# Catch-Up Bill Runs

Use a catch-up bill run to advance the next billing date, billed amount, and pending amount on billing schedules for transactions that a legacy system fully or partially billed. Catch-up doesn’t create invoices for those periods.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management


This feature is available with the Revenue Management Advanced license or the Revenue Management Billing license.

The Milestone Billing feature is available only with the Revenue Management Billing license. Contact your Salesforce account executive for more information.

After you import accounts, orders, billing schedules, billing schedule groups, and billing milestone plans, complete catch-up before generating invoices for those schedules. You can run catch-up more than once for the same schedules until a draft or posted invoice exists. Schedules that already have a draft or posted invoice aren’t included.

Set the target date to the last date billed in the legacy system so the next invoice batch run in Billing starts with the next unbilled period. Catch-up doesn’t create tax, credit or debit memos, payments, or invoice documents for those periods.

NOTE Don’t start an invoice batch run while a catch-up bill run is in progress. Parallel invoicing can leave billing schedules and invoices inconsistent.

For milestone billing, accomplished milestones with an accomplishment date on or before the target date are treated as invoiced. Later milestones remain available for the next invoice run.

To schedule a catch-up bill run, select Catch-Up Bill Run when you create an invoice scheduler. Catch-up bill runs use the Once frequency and require a target date. See Generate Invoices Automatically Based on Billing Schedules.

CATCH-UP AFTER A LEGACY MIGRATION

Infiwave migrates monthly billing schedules from a legacy system that billed those schedules through May 1, 2026. The company wants the first invoice in Billing to cover June 2026. The company configures a catch-up bill run by using these values.

Catch-Up Bill Run: Selected
Frequency: Once
Target Date: May 1, 2026

Catch-up advances the next billing date, billed amount, and pending amount through May 1. It doesn’t create invoices. Billing updates the next billing date to June 1, 2026. The company then configures an invoice batch run by using these values.

Frequency: Once
Select billing schedules based on: Target Date
Target Date: June 1, 2026

Billing generates invoices for the June 2026 billing period. A later target date, such as July 1, 2026, can include more than one billing period. To invoice only the next unbilled period, match the target date to that period or set billing period count.
