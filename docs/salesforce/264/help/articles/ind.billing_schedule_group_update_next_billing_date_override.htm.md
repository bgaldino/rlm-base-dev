---
article_id: ind.billing_schedule_group_update_next_billing_date_override.htm
title: Next Billing Date Override
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedule_group_update_next_billing_date_override.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedule_group_update.htm
fetched_at: 2026-09-04
---

# Next Billing Date Override

The next billing date override overrides the next billing dates of all the billing schedules.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
Eligibility Conditions for Updating Next Billing Date Override

The next billing date override can be updated only if these conditions are met:

The billing term unit of the billing schedule can't be Milestone Plan.
The status of the related billing schedules must be Ready for Invoicing.
The status of all the billing schedules related to the billing schedule group can't be Completely Billed.
The next billing date override must be greater than the current date, and between the effective next billing date and end date of the billing schedule group.
Updating Next Billing Date Override

When the next billing date override is updated, it results in these changes:

To generate invoices for the related billing schedules, billing schedule groups that have the next billing date override before the target date are considered.
Invoices are generated on the next billing date override instead of the next billing date of the related billing schedules. The invoice is generated for the charge period between the original next charge date and the next billing date override.
The next billing date override is used only once for generating invoices. It’s removed after the invoices are generated.

For example, the current month is April and a billing schedule group has these values:

Billing Type: Advance
Bill Day of Month: 15
Next Billing Date Override: 04/20/2025

The related billing schedules have these values:

Next Billing Date: 04/15/2025
Next Charge Date: 04/15/2025

When a target date that's on or after 04/20/2025 is specified for generating invoices, invoices are generated for these billing schedules. After the invoices are generated, the Next Billing Date Override value is removed.
