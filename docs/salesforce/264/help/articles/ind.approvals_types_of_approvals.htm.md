---
article_id: ind.approvals_types_of_approvals.htm
title: Approval Workflow Types
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_types_of_approvals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_building_blocks_of_advanced_approvals.htm
fetched_at: 2026-09-07
---

# Approval Workflow Types

You can implement approvals in your workflow using two primary methods: serial or parallel. These are managed by setting up an approval chain, which is a label that identifies the specific group and sequence of approvers for a given process.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
Serial Approvals

Serial approvals create a sequential chain where approvers must complete their tasks one after another. Each approver waits for the previous approver to complete their task before receiving the task assigned to them. This method is particularly useful in complex workflows with multiple stages of approvals, as it ensures a specific order of review is followed.

To implement serial approvals, set the first approval step’s condition to When the stage starts, the step starts. The second approval step's condition must be set to When another step is marked Completed, the step starts, and it should watch for the approved or rejected status of the first step.

EXAMPLE Set up a serial chain named Finance Approvals. The process could involve an accountant, a finance manager, and a VP of Finance, each approving in sequence. The request will not go to the manager until the accountant has approved it.
Parallel Approvals

Parallel approvals, in contrast, send the task to multiple approvers at the same time. This approach is used when you need a group of people to review an item, but the order in which they do so does not matter.

The workflow can be configured in two common ways:

First Response: The task is completed (either approved or rejected) as soon as the first person in the parallel chain responds.
All Must Approve: The task is only considered approved after every individual in the parallel chain has given their approval.

Using parallel approvals, you can trigger multiple steps simultaneously as long as their conditions are satisfied at the same time. For instance, setting the condition for several different approval steps to When the stage starts, the step starts will cause them all to begin together. You can structure this by placing all parallel chains within a single Stage element, which allows each chain's steps to execute independently of the others.

Alternatively, you can group all steps of the same level into one Stage element to ensure all steps at that level are executed together before the flow moves on to the next. However, within any single parallel chain, you can still define serial sequencing (like Step B waiting for Step A) by using the same output-based conditions mentioned for serial approvals.

EXAMPLE A marketing campaign might be sent to the Head of Legal, the Head of PR, and the Head of Brand simultaneously. If configured for All Must Approve, the campaign can’t launch until all three have signed off.
Implement Serial and Parallel Approvers
To implement serial and parallel approvers, you’ll need to set up an approval chain.
