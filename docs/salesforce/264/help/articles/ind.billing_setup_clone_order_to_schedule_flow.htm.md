---
article_id: ind.billing_setup_clone_order_to_schedule_flow.htm
title: Use Order to Billing Schedule Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_clone_order_to_schedule_flow.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedules_from_orders.htm
fetched_at: 2026-09-04
---

# Use Order to Billing Schedule Flow

Use the Order to Billing Schedule flow to automatically generate billing schedules and billing schedule groups from order items as soon as orders are activated.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management
The Order To Billing Schedule flow template and Create Billing Schedules for Orders API are available with the Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

Save a version of the out-of-the-box Order to Billing Schedule flow and activate it. When you clone the flow, we recommend that you include Custom in the name to distinguish it from out-of-the-box flows.

When an order is activated, two flows—Order to Asset and Order to Billing Schedule—are triggered. The Order to Billing Schedule flow then generates a billing schedule group and a billing schedule for the order.

NOTE As a best practice, we recommend that you use only one active flow to generate billing schedules. If there are multiple active flows, duplicate billing schedules get generated for the same order.
