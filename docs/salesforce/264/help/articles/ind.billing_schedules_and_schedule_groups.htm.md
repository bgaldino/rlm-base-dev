---
article_id: ind.billing_schedules_and_schedule_groups.htm
title: Manage Billing Schedules and Billing Schedule Groups
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedules_and_schedule_groups.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing.htm
fetched_at: 2026-09-04
---

# Manage Billing Schedules and Billing Schedule Groups

Billing schedules define when and how an order product is invoiced. Billing schedule groups contain one or more billing schedules. Both of these are created and updated as a result of creating, amending, and canceling orders. You can generate billing schedules directly from transactions in external systems, or from any Salesforce object by using Create Standalone Billing Schedules API. To generate billing schedules from orders, use the Order to Billing Schedule flow, Create Billing Schedules for Orders API, or Create Standalone Billing Schedules API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
NOTE For details about how billing schedules are triggered and how invoices are grouped, see Understanding Billing Schedule Creation and Invoice Generation.
Generate Billing Schedules from External Transactions or Salesforce Objects
Use the Create Standalone Billing Schedules API to generate billing schedules directly from transactions in external systems, or from any Salesforce object.
Generate Billing Schedules from Orders
Generate billing schedules from orders by using a flow or an API.
Generated Billing Schedule Details
View all the key billing schedule and invoice details in the Billing Schedule Group records.
Add the Billing Schedule Details Component to a Group Page
Give billing operations and sales teams a timeline and summary metrics on the Billing Schedule Group page. In Lightning App Builder, drag Billing Schedule Details onto the page, then save and activate the page.
Manage Billing Frequencies
You can set a product’s billing frequency to be different from its pricing frequency. For example, you can bill a customer on an annual basis even if the order or subscription is priced monthly.
Bill for Multiple Terms in a Billing Period
Your sales reps can now set up flexible terms for billing subscriptions whether it’s every three weeks, every five months, or every two years. For example, to bill a subscription every three months, your sales reps can set the billing frequency to monthly and billing term to 3 on the order product. Billing automatically calculates the correct amount for the combined period and sets the next billing date accordingly.
Update Billing Schedule Groups
Update billing schedule group fields at any time. You can update the billing day of month, next billing date override, billing and shipping addresses, tax treatment, and the payment term of a billing schedule group.
Define Invoice Grouping on a Billing Schedule
Generate grouped or split invoices by configuring default, custom, or billing schedule group types on billing schedules.
