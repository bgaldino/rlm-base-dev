---
article_id: ind.dro_add_a_fulfillment_user.htm
title: Create Fulfillment Users for Order Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_add_a_fulfillment_user.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Create Fulfillment Users for Order Orchestration

During fulfillment, Dynamic Revenue Orchestrator (DRO) uses the permissions associated with the fulfillment user rather than those of the user who submits an order. You can specify a different user for certain orchestration tasks, but generally, the permissions default to the fulfillment user. Select the fulfillment user from the Dynamic Revenue Orchestrator Settings pane.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To add a fulfillment user:	DRO Admin
From Setup, in the Quick Find box, enter Dynamic Revenue Orchestrator Settings and select it.
Choose one of these options:
User who submitted the order: The permissions and name of the user who submitted the order are used for fulfillment processes.
Other User: Search for and select a user whose permissions and name are used for fulfillment processes.
IMPORTANT The fulfillment user must have the Assetize Order permission from the Revenue Lifecycle Management permission sets and either Submit Transaction User or DRO Admin User permissions.

The fulfillment user is set. You don't need to save your work.

SEE ALSO
Fulfillment User
Permission Sets in Dynamic Revenue Orchestrator
