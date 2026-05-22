---
article_id: ind.dro_fallout_design_and_management.htm
title: Fallout Design and Management
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_fallout_design_and_management.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Fallout Design and Management

Fallout refers to fulfillment steps that have failed. Dynamic Revenue Orchestrator (DRO) can retry failed callouts or auto tasks, send them to a queue, or simply mark them as failed. During fulfillment, operators can mark steps as complete, or retry them.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions

When designing fulfillment, create rules that determine what DRO does when a step fails. For example, set the number of times the step retries before being assigned to a queue for resolution.

During the fulfillment process, retry failed steps, or mark them as complete, either one by one or in bulk.

EXAMPLE The fulfillment designer creates a rule so that if a Credit Check callout step receives an error from the credit department, the step retries 3 times. If the step still fails, then it goes to the Credit Team Fallout queue.

During fulfillment, the credit department's credit check system is down for a few minutes. After the credit check system is back online, the credit team checks the fallout queue, selects all the failed callouts in the queue, and clicks Retry.

All the steps retry, and since the system is back online, they're all successful and fulfillment continues.

Design Time

Before fulfillment, designers configure fallout in DRO:

Turn on Fallout settings. See Turn On Features to Manage Fallout and Service Level Agreements
Create Salesforce queues to contain fatally failed steps: For example, you can create a queue for each group in your organization that handles fallout. These queues must include Fulfillment Step as a supported object. See Create Queues. To add fatally failed steps to an existing queue, you must either be a member of the queue or have the System Administrator permission set.
Configure fallout rules: These rules tell DRO how many times a step retries, and when. They also tell DRO which queue to send fatally failed steps. See Configure Fallout Rules
View failed records in the queue: To view the fatally failed steps in the queue, navigate to Fulfillment Steps, select the Fatally Failed Fulfillment Steps list view, and filter the results to show the specific queue containing the fatally failed steps. You can also create a custom list view to view the records in the queue. See Create or Clone a List View in Lightning Experience.
Run Time

During fulfillment, manage fallout:

To see steps that have failed, check the fulfillment plan, fallout queues, or the Fatally Failed Fulfillment Steps list view. See Monitor Decomposition During Fulfillment.
Retry callouts and auto task steps, or mark them complete. You can do so one at a time, or in bulk. See Retry or Complete Multiple Failed Fulfillment Steps.
SEE ALSO
Design-Time Administration for Order Fulfillment
Monitor Decomposition During Fulfillment
