---
article_id: ind.dro_fulfillment_user.htm
title: Fulfillment User
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_fulfillment_user.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Fulfillment User

A fulfillment user is the user whose permissions are used throughout the fulfillment process, unless you specify a different user at a more granular level. If you don't specifically configure a step to be run by a different user in the Run As User field, then Dynamic Revenue Orchestrator (DRO) uses the fulfillment user's permissions.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

Dynamic Revenue Orchestrator uses permissions and permission sets to determine whether a user can do certain things. When you set the fulfillment user, it's like telling DRO: from now on, pretend that this is the user that submits every order.

Make sure that the fulfillment user has at least the permissions granted by DRO Admin User or Submit Transaction User, and that it has the Assetize Order permission from the Revenue Lifecycle Management permission sets.

When you design a fulfillment step, you can enter a different user in the Run As User field. For example, design a callout that runs as a user who has permissions on the external system that you call out to. If you don't specify a user on a fulfillment step, then the step runs as the fulfillment user.

SEE ALSO
Permission Sets in Dynamic Revenue Orchestrator
