---
article_id: ind.um_billing_schedules_for_usage_products.htm
title: Billing Schedules and Invoices for Usage-Based Products
source_url: https://help.salesforce.com/s/articleView?id=ind.um_billing_schedules_for_usage_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Billing Schedules and Invoices for Usage-Based Products

For usage-based products, Billing considers late usage and extra orders.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license

When you activate an order, Billing creates a billing schedule and a billing schedule group for each binding instance and usage resource pair. The status of the billing schedule for usage resources is always Ready for Invoicing.

When another order creates a billing schedule for the same binding instance and usage resource, the dates of the existing billing schedule and billing schedule group are updated.

Unlike other charge types, usage charges don’t transition to a completely billed status. Usage billing schedules remain open beyond their end date to accommodate late usage and new orders tied to the same binding instance.

Usage-based products are invoiced under these conditions.

When you generate invoices by using the Invoice Scheduler, you select All or Usage filter.
Billing picks usage billing schedules for invoicing when the account is in a billing batch schedule and the schedules are ready for invoicing.
The liable summary status is marked as Ready for Invoicing.
The liable summary, usage entitlement bucket, and usage entitlement account share the grant binding target.
The usage billing schedule and the usage entitlement bucket correspond to the same usage resource, which is referenced from the billing period item.
When the usage entitlement bucket’s usage resource is populated, the same resource is autopopulated on the billing period item record.
NOTE For usage billing schedules and billing schedule groups, Billing doesn’t calculate invoice periods. Instead, it uses the liable summary start date and end date, stamping them on the billing period item and invoice line.

For example, if a company starts billing on January 20, 2025, and the billing cadence is monthly, the first billing period ends on February 19, 2025. Usage records are aggregated for invoicing if their event date falls within this window. The start date on the order product and the frequency define the billing period. During the invoice posting process, the liable summary status changes to Invoiced.

NOTE Draft invoices don’t affect the liable summary status. If a user voids a posted invoice, the liable summary status automatically reverts to Ready for Invoicing status and for rebilling.
Business Use Case

TelcoOne offers a data connect plan, a subscription that includes a monthly data allowance and charges for extra usage. The plan’s anchor product is the subscription itself, while mobile data consumption is modeled as a usage resource billed according to actual usage.

When a user activates an order, Billing creates billing schedules and billing schedule groups for both the subscription and its usage resources. Assets are created only for the anchor subscription product. Billing doesn’t create assets for usage resources.

The data allowance is provisioned as a grant. If the grant is exceeded, overage is chargeable. Actual data usage is recorded against the billing period, and Billing gets the usage data from the liable summaries record to generate invoice lines.

SAMPLE INVOICE LINES
PRODUCT	USAGE TYPE	QUANTITY	UNIT PRICE	TOTAL	ASSET ID
Data Connect Plan	Base Subscription	1	$30	$30	Asset-201
Data Connect Plan	Data Overage GB	2	$10	$20	Asset-201

This model provides a clear visibility into included allowances versus overage charges. It’s ideal for Telecom providers that need transparent and flexible invoicing for subscription and consumption-based services.
