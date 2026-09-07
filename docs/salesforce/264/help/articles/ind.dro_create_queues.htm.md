---
article_id: ind.dro_create_queues.htm
title: Create Queues for Dynamic Revenue Orchestrator
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_create_queues.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_advanced_setup.htm
fetched_at: 2026-09-05
---

# Create Queues for Dynamic Revenue Orchestrator

Create Salesforce queues to contain fatally failed steps: For example, you can create a queue for each group in your organization that handles fallout. These queues must include Fulfillment Step as a supported object.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management
From Setup, enter Queues in the Quick Find box, then select Queues.
Select New Queue.
Select Fulfillment Step as the supported object.
Assign users to the queue. These users must have Fulfillment Manager/Operator permission set assigned or have the Fulfillment User profile.
