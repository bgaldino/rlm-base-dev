---
article_id: ind.dro_fallout_design_and_management.htm
title: Fallout Design and Management
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_fallout_design_and_management.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_dynamic_revenue_orchestrator_concepts_and_references.htm
fetched_at: 2026-09-05
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
Create Salesforce queues to contain fatally failed steps: For example, you can create a queue for each group in your organization that handles fallout. These queues must include Fulfillment Step as a supported object. See Create Queues. To add fatally failed steps to an existing queue, you must either be a member of the queue or have the System Administrator permission set. Assigning a fulfillment step to a fallout queue does not trigger email notifications or create Salesforce tasks.
Configure fallout rules: These rules tell DRO how many times a step retries, and when. They also tell DRO which queue to send fatally failed steps. See Configure Fallout Rules

After you create or update a Fulfillment Fallout Rule, refresh the Fulfillment Fallout Rules decision table.

NOTE Until you refresh the decision table, DRO reevaluates the previous rule configuration. If no rule matches the step and error code, DRO sets the step status to FATALLY_FAILED without retrying it.

DRO retries errors that a flow returns through an Auto Task Fault Path. It doesn't retry raw or unhandled Apex exceptions. To make an Apex failure eligible for retry, handle the failure through the flow's Fault Path and return the required Auto Task output variables. See Auto Task Fulfillment Step.

Run Time

During fulfillment, manage fallout:

Monitor fallout in queues To view fatally failed steps in a specific queue, navigate to the Fulfillment Steps tab and select the Fatally Failed Fulfillment Steps list view. Filter by the Queue column to see your assigned records. See Monitor Decomposition During Fulfillment.
To see steps that have failed, check the fulfillment plan, fallout queues, or the Fatally Failed Fulfillment Steps list view. See Monitor Decomposition During Fulfillment.
Retry callouts and auto task steps, or mark them complete. You can do so one at a time, or in bulk. See Retry or Complete Multiple Failed Fulfillment Steps.
SEE ALSO
Monitor Decomposition During Fulfillment
