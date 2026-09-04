---
article_id: ind.billing_initiate_dunning_orchestration.htm
title: Initiate and Monitor Dunning Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_initiate_dunning_orchestration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_configure_dunning_orchestration.htm
fetched_at: 2026-09-04
---

# Initiate and Monitor Dunning Orchestration

With the dunning orchestration solution set up and enabled on the Billing Settings page, you can initiate automated dunning on your collection plans.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
Create a collection plan and add the required collection plan items.
Make sure that the collection plan has the due date, risk profile, accurate contact information, and includes at least one fulfillment workspace with usage type as Billing.
On the collection plan record, click Initiate Dunning Orchestration.

This action creates an orchestration plan with an In Progress status and triggers an automated task. The customer receives an email notification detailing their upcoming invoices.

When you initiate dunning orchestration, the orchestration plan shows the status of each step based on the collection plan’s milestones. You can check which steps are in waiting status before the due date or when the next milestone is reached. You can also check whether reminder emails have been sent to the customers, and if any manual escalation task has been assigned.

NOTE If the Initiate Dunning Orchestration quick action button isn’t available, add it by editing the Collection Plan object’s page layout.
