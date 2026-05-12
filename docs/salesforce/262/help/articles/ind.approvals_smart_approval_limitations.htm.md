---
article_id: ind.approvals_smart_approval_limitations.htm
title: Smart Approval Limitations
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_smart_approval_limitations.htm&type=5&release=262
release: 262
release_name: Summer '26
area: approvals
fetched_at: 2026-05-12
---

# Smart Approval Limitations

This section covers eligibility rules and known constraints for the Smart Approvals feature.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions where Advanced Approvals is enabled
Smart Approval Eligibility - Evaluation Flows

Using an evaluation flow as an entry or exit condition in any approval step marks the entire flow as ineligible, violating a key constraint for Smart Approvals. To resolve this issue, update the workflow to incorporate those conditions directly.

Smart Approval Eligibility - Decision Nodes

A flow is considered ineligible if you add a decision node before a stage when you add the condition When the stage starts, the step starts in an approval step. To resolve this issue, update the approval step's entry conditions to directly include the criteria from the preceding decision node.

Unsupported Data Types for Smart Approval

Approval conditions must use a supported Number or Text data type to be eligible for auto-review in Smart Approvals.

Smart Approval Trigger Requirement

A record's preceding submission status must be Rejected or Recalled for the resubmission to be eligible for Smart Approval evaluation.

Smart Approval Version Dependency

Smart Approvals are dependent on a consistent flow definition version. If the active flow definition version changes between the original submission and a resubmission, Smart Approvals won’t be considered. To ensure correct function,a resubmission must use the same flow definition version as the original submission to be eligible for Smart Approval evaluation.

Smart Approval Logic Constraint

Using the NOT operator in custom entry logic marks the approval step as ineligible for Smart Approvals. To resolve this issue, you must rebuild the logic using only positive conditions to achieve the same outcome.

Smart Approval Limitation Post-Reassignment

Reassigning a work item during the original submission's execution marks the resubmission as ineligible for Smart Approvals. This scenario will require a manual review of the work item.
