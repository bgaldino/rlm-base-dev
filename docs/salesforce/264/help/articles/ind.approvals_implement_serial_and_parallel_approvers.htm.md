---
article_id: ind.approvals_implement_serial_and_parallel_approvers.htm
title: Implement Serial and Parallel Approvers
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_implement_serial_and_parallel_approvers.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_types_of_approvals.htm
fetched_at: 2026-09-07
---

# Implement Serial and Parallel Approvers

To implement serial and parallel approvers, you’ll need to set up an approval chain.

USER PERMISSIONS NEEDED
To implement serial and approval approvals:	Approval Designer

The steps below assume you are already familiar with how to create a flow.

Open Flow Builder and create a new flow (either an Autolaunched Flow Approval Process or a Record-Triggered Flow Approval Process).
Add a Stage element to the flow and include approval steps for the approvers.
For each approval step, fill out the required fields, including the Approval Chain Name.
The Approval Chain Name should reflect the list of approvers for that step or stage in the process.
