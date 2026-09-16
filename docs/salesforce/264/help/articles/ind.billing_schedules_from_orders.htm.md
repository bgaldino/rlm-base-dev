---
article_id: ind.billing_schedules_from_orders.htm
title: Generate Billing Schedules from Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedules_from_orders.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedules_and_schedule_groups.htm
fetched_at: 2026-09-04
---

# Generate Billing Schedules from Orders

Generate billing schedules from orders by using a flow or an API.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management
The Order To Billing Schedule flow template and Create Billing Schedules for Orders API are available with the Revenue Management Advanced license or the Revenue Management Billing license.
USER PERMISSIONS
NEEDED
To use Create Billing Schedules for Orders API:	

Create Billing Schedules From Billing Transactions API permission

AND

Context Service Runtime permission set


To use Order To Billing Schedule flow template:	

Billing Admin permission set

AND

Billing Operations User permission set


To generate billing schedules for usage-based charge types:	

Product Catalog Management Viewer permission set

OR

Usage Management Runtime permission set

To automatically trigger the generation of billing schedules when the order is activated, use the Order to Billing Schedule flow. To generate billing schedules for orders by using API, use Create Billing Schedules for Orders API or Create Standalone Billing Schedules API.

IMPORTANT

Use the Order to Billing Schedules API and Order to Billing Schedules flow for any new sale, amendments, renewals, or cancellations that originate from Revenue Management orders and assets.

Use Order to Billing Schedule Flow
Use the Order to Billing Schedule flow to automatically generate billing schedules and billing schedule groups from order items as soon as orders are activated.
Use Create Billing Schedules for Orders API
Use Create Billing Schedules for Orders API to generate billing schedules from orders.
Use Create Standalone Billing Schedules API
For one-time, termed, and evergreen products, use Create Standalone Billing Schedules API to generate billing schedules from orders and order items.
