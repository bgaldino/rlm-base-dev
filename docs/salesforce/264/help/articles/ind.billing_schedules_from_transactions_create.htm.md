---
article_id: ind.billing_schedules_from_transactions_create.htm
title: Use Create Billing Schedules for Orders API
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_schedules_from_transactions_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_schedules_from_orders.htm
fetched_at: 2026-09-04
---

# Use Create Billing Schedules for Orders API

Use Create Billing Schedules for Orders API to generate billing schedules from orders.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with Revenue Management
The Order To Billing Schedule flow template and Create Billing Schedules for Orders API are available with the Revenue Management Advanced license or the Agentforce Revenue Management Billing license.

Before using Create Billing Schedules for Orders API, select the context definition and the context mapping from the Billing settings page or create a custom procedure plan definition.

Create a custom procedure plan definition with these values.
Select Billing as the process type.
Select the object that you want to generate billing schedules for as the primary object.
Select the context definition extended from BillingContext as the context definition.
Update and activate the procedure plan definition.
Open the procedure plan definition and select a read context mapping for the primary object.
Activate the procedure plan definition.
To create billing schedules from orders, use Create Billing Schedules for Orders API.

To automate this process for external transactions or Salesforce objects, design a custom flow and add the Create Billing Schedules From Billing Transaction action.

Generate invoices from these billing schedules by scheduling invoice runs, from the Order record pages, or by using an API.
