---
article_id: ind.approvals_building_blocks_of_advanced_approvals.htm
title: Design an Approval Workflow
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_building_blocks_of_advanced_approvals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Design an Approval Workflow

Approval workflows enable businesses to implement complex, multi-step approval rules and efficiently manage transaction compliance.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled

This functionality leverages the Flow Orchestration engine, which manages and coordinates these approval processes, providing a flexible and powerful way to manage both simple and complex approval scenarios of the Flow Approval Process Type.

Approval workflows manage processes using your organization's staffing structure. They link together different Salesforce Flows, assign tasks to various people or queues, and automatically manage the handoffs and sequencing of work. These workflows are made up of sequential or parallel steps, and you can easily configure them to create smart, flexible governance strategies that span multiple teams (like Sales, Finance, and Legal). Furthermore, the process can pause to await user input and provides clear audit tracking, simplifying the understanding and management of complex approvals.

Before you design an approval workflow, we recommend you understand the fundamental details about the Flow Approval Process.

Building Blocks of Flow Approval Processes
Flow Approval Processes Concepts
Build a Flow Approval Process

You can create flow approval processes in Flow Builder, including the autolaunched flow from the Approvals app on your org or the Flow Approval Process from Setup.

Create a Draft Autolaunched Flow Approval Process
Create a Flow Approval Process from Scratch
/apex/HTViewHelpDoc?id=ind.Chunk1519288329.htm#approvals_types_of_approvals

Smart Approvals in Approval Flows
To eliminate approval bottlenecks, Smart Approvals routes requests by auto-approving pre-qualified data changes and not reviewing unchanged data. When a record is resubmitted for approval, Smart Approvals compares the new conditions against the previous submission. If the values remain within the defined range, it skips re-approval.
Example: Configure an Approval Workflow
Let’s build a complete approval workflow to determine the approvals required on a quote’s discounts, implementing both Smart Approvals and Dynamic Approval Notifications.
Define Rules and Conditions for Auto-Approval Resubmissions
Set your own rules and conditions on specific fields for auto-approving resubmissions. Compare the current submission’s record details against the previously submitted record so that only significant changes require manual review.
Use the Stage Exit Condition
Serial and approval workflows can easily get stuck in a “waiting” state if the Stage element's exit condition isn't configured properly. The problem occurs when the stage is set to wait for all steps to finish, as it can't account for conditional steps that were never triggered. This creates a deadlock.
Flow Core Action: Override Approval Work Item
Update the status of an approval work item to reflect the approval admin's decision, allowing admins to override the decision for any assignee.
