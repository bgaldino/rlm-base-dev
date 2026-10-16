---
article_id: ind.billing_understand_target_date_and_billing_period_count.htm
title: Understand Invoice Date, Target Date, and Billing Period Count
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_understand_target_date_and_billing_period_count.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_automate_invoice_generation.htm
fetched_at: 2026-09-04
---

# Understand Invoice Date, Target Date, and Billing Period Count

Before you schedule invoice batch runs, learn how invoice dates are determined, how billing schedules are selected, and how many billing periods are processed for each schedule. You can also process a specific number of billing periods without relying on a target date.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

During an invoice batch run, Billing selects billing schedules, generates invoices from those schedules, and applies tax. Billing also selects schedules using the filter criteria on the invoice scheduler and a target date, billing period count, or both. It then creates invoices for those schedules. The invoice date is stamped on each invoice and is the date used to calculate tax. Estimated tax is calculated for draft invoices. Actual tax is calculated for posted invoices. See Invoice Batch Run Process and Tax Calculation Process.

Use this table to compare invoice date, target date, and billing period count. You can set a target date, a billing period count, or both.

OPTION	WHAT IT DOES	WHEN TO USE
Invoice Date	Date stamped on the invoice and used for tax calculation.	Always set
Target Date	Selects which billing schedules to invoice.	When you want to invoice schedules through a specific date.
Billing Period Count	Caps how many periods are invoiced per schedule.	When you want to limit the number of periods invoiced per schedule.

You can select billing schedules using a target date, billing period count, or both, regardless of the invoice batch run frequency. The run frequency only affects how you specify or calculate the target date and invoice date.

Invoice Date

The invoice date is the date stamped on an invoice and used for tax calculation. For a one-time invoice batch run, you specify the invoice date directly. For recurring runs, Billing determines the invoice date by adding an invoice date offset to either the target date or the run date.

The invoice date offset is the number of days Billing adds to or subtracts from the selected date. A positive offset produces a date after the selected date, a negative offset produces a date before the selected date, and an offset of 0 uses the selected date as the invoice date. Base invoice date on determines whether Billing applies the offset to the target date or the run date.

When you base the invoice date on the target date, Billing adds the invoice date offset to the target date. For example, if the target date is August 23, an offset of 0 makes the invoice date August 23, an offset of 3 makes the invoice date August 26, and an offset of –3 makes the invoice date August 20.

When you base the invoice date on the run date, Billing adds the invoice date offset to the date the invoice batch run runs. For example, if the invoice batch run runs on July 23, an offset of 0 makes the invoice date July 23, an offset of 3 makes the invoice date July 26, and an offset of –3 makes the invoice date July 20.

Target Date

The target date tells Billing which billing schedules to invoice. Billing invoices a schedule when its next billing date is on or before the target date and the schedule matches the filter criteria on the invoice scheduler. When no target date is set, Billing invoices every schedule that matches those filters.

Use a target date when you want to invoice selected billing schedules through a specific date. For example, if the selected schedules are billed monthly, a target date of June 1 invoices those schedules with a next billing date on or before June 1.

For a one-time run, you specify the target date directly. For recurring invoice batch runs, Billing determines the target date from either the run date or a calendar day of the month. Base target date on chooses which of these dates to use.

When you base the target date on the run date, a positive offset produces a target date after the run date, a negative offset produces a target date before the run date, and an offset of 0 uses the run date as the target date. For example, if the invoice batch run executes on July 23, an offset of 0 makes the target date July 23, an offset of 3 makes the target date July 26, and an offset of –7 makes the target date July 16.

In some complex billing scenarios, businesses don’t have a fixed day offset. Instead they work with a flexible date like the Nth day of the coming month. When you base the target date on a calendar day of the month, Billing determines the target date from the target day of month and target month offset. The target day of month can be 1 through 28, or the last, second-to-last, or third-to-last day of the month. The target month offset is the number of months added to or subtracted from the month of the invoice batch run. For example, a monthly invoice batch run on July 23 with a target day of month of 23 and a target month offset of 1 has a target date of August 23.

NOTE For milestone billing, the target date determines which accomplished milestones are invoiced. When no target date is set, Billing uses the run date of the invoice batch run so that future milestones aren’t invoiced. Usage billing schedules with liable summaries in Ready for Invoicing status are always invoiced, regardless of the target date. The Milestone Billing and Usage-Based Invoicing features are available only with the Revenue Management Billing license.
Billing Period Count

When schedules have different next billing dates, using a fixed target date to select all of them can cause some schedules to be invoiced for extra billing periods. This can result in over-billing.

Billing period count specifies how many billing periods to process for each selected schedule, from 1 through 12. Each schedule is invoiced for the specified number of periods, even when schedules have different next billing dates or billing period lengths.

Use billing period count with a target date when you want to limit which schedules are invoiced and specify how many billing periods to invoice for each schedule. Each selected schedule is invoiced for the specified number of periods or through its end date, whichever comes first.

You can also use billing period count without a target date when you want to invoice every schedule that matches the invoice scheduler's filter criteria for a specific number of periods. For example, to invoice every matching schedule for the next two billing periods, set billing period count to 2.

NOTE Billing period count doesn’t apply to milestone or usage billing schedules. For milestone billing, the target date determines which milestones are invoiced. Usage billing invoices all Ready for Invoicing usage records. The Milestone Billing and Usage-Based Invoicing features are available only with the Revenue Management Billing license.

To create an invoice scheduler after you choose these options, see Generate Invoices Automatically Based on Billing Schedules.

EXAMPLE

You have a monthly schedule with a next billing date of April 1 and a quarterly schedule with a next billing date of June 1. A target date of June 1 without a billing period count invoices the monthly schedule for three monthly periods instead of one.

With billing period count set to 1, each schedule is invoiced for one period: April 1 to May 1 for the monthly schedule and June 1 to September 1 for the quarterly schedule.
