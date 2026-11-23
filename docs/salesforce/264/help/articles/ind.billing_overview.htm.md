---
article_id: ind.billing_overview.htm
title: Billing in Revenue Cloud
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_get_started.htm
fetched_at: 2026-11-23
---

# Billing in Revenue Cloud

Billing takes billing schedules through invoicing, payment, and accounting. Billing creates those schedules when you activate an order in Revenue Cloud, or when you use the Create Standalone Billing Schedules API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
NOTE Availability of Billing features depends on your Revenue Cloud license. See Billing Feature Availability.
Quotes and Orders

Quotes and orders are the source records for Billing. Billing uses the products, quantities, terms, and priced amounts in these records to create invoices. Changes to order details, such as quantity or term updates, are reflected in downstream billing records.

See Create a Quote, Create an Order from a Quote, and Create an Order.

Pricing

Pricing defines list prices and price adjustments for products on quotes and orders. Billing doesn't recalculate prices. It uses the order’s pricing to calculate the invoice amount.

Pricing determines the amounts. Billing determines when and how those amounts are invoiced.

See Design Your Pricing Model.

Billing Treatments, Proration Policies, and Arrangements

Billing policies, treatments, and profiles determine whether a charge is billable and when, how, and to whom it is billed.

When a subscription starts, ends, or changes during a billing period, Billing prorates the charge to match the portion of the period that applies. Period boundaries and billing frequency determine when each period starts and ends.

Billing arrangements define which account receives the invoice and how the billable amount is allocated when one account owns the service and another is billed or when costs are split across multiple billing accounts.

See Define Billing Policies and Billability Rules, Period Boundaries and Billing Day of Month, Manage Billing Arrangements, and Create Billing Profiles.

Billing Schedules

Billing schedule groups and billing schedules represent how charges are organized over time for invoicing, including billing dates, frequencies, and billing status.

As orders change through amendments, renewals, and cancellations, the related billing schedules stay aligned to the order changes. See Manage Billing Schedules and Billing Schedule Groups.

For usage-based products, Billing invoices the amount based on actual product usage, not a fixed order quantity. Usage Management tracks consumption against grants and entitlements, applies rates to that usage, and produces invoice-ready summaries.

When an order is activated, Billing creates a billing schedule for each usage resource. A schedule remains open beyond its end date so that Billing can invoice late usage and overage.

See Manage and Track Usage-Based Products, Manage Consumption for Usage-Based Products, and Billing Schedules and Invoices for Usage-Based Products.

Taxes

Tax configuration defines how tax is calculated during invoicing. Tax is represented on invoice lines and contributes to final invoice amounts.

See Define Tax Calculation for Invoices.

Invoices

Invoices represent billable charges for an account or order. They bring together billing dates, grouping rules, priced or consumption-based amounts, and tax results into customer-facing billing documents.

See Generate Invoices.

Credits and Debits

Credits and debits represent how invoice balances are adjusted. Credit memos and debit memos record balance adjustments associated with invoice changes.

See Manage Credit Memos and Manage Debit Memos.

Payments and Collections

Payments and refunds represent cash movement that settles invoice balances.

See Process Payments and Issue Refunds.

Collections and dispute management extend this post-invoice lifecycle by supporting follow-up actions on overdue balances and contested charges.

See Collections and Manage Disputes.

Accounting

Billing captures the full financial lifecycle, including invoice and payment activity, credit and demo memos, refunds, and realized and unrealized foreign exchange gains and losses. It prepares this data for general ledger integration as journal entries, general ledger account summaries, and foreign exchange gain and loss summaries. See Manage Financial Accounting.

Billing supports milestone billing, usage-based billing, sequential invoice numbering, suspending and resuming billing, collections, invoice write-offs, dispute management, account statements, and operational views such as Billing Settlements Central and the Billing Operations Console.

Billing supports agentic and self-service experiences that help customers review invoices, pay balances, raise service requests, and get conversational explanations of charges. Together, these capabilities support the complete quote-to-cash flow.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_overview.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
