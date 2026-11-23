---
article_id: ind.approvals_approval_delegation.htm
title: Advanced Approval Delegation
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_approval_delegation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals.htm
fetched_at: 2026-11-23
---

# Advanced Approval Delegation

When a reviewer is unavailable, approval work items can stall a workflow. With Advanced Approval Delegation, reviewers redirect their approval responsibilities to another user, group, or queue for a set period or indefinitely. During an active delegation, delegates receive email notifications and review and act on approval work items on behalf of the original reviewer.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled

With Advanced Approval Delegation, reviewers can hand off their approval responsibilities to another user, group, or queue for a set period or indefinitely.

During a delegation, ownership of approval work items stays with the original reviewer, even though the delegate can review items submitted before the delegation began. These examples show how delegation affects approval work item visibility and assignment.

Example: Review Approvals Submitted Before a Delegation Starts

When you submit a quote for approval on January 1 and the delegation period starts on January 2, the delegate can review the previously submitted quote starting January 2. Delegation applies to existing approval work items, not just ones created after the delegation begins.

Example: Approval Work Item Assignment During an Active Delegation

Approval work items created during an active delegation period remain assigned to the original reviewer. Delegates can view and review these items during the delegation period, but ownership doesn't change.

Find and Manage Delegation Records

To find and manage delegation records, use these list views on the Approval Delegation object.

Approval Delegations from Me: Shows delegations that you set up.
Approval Delegations for Me: Shows delegations where you're the designated delegate.
All Approval Delegations: Shows all delegation records in the org.

To view approval work items assigned to you as a delegate, use the Delegated Approval Work Items list view on the Approval Work Item object.

Turn On Advanced Approval Delegation
Give reviewers the ability to delegate their approval responsibilities to another user, group, or queue for a set period or indefinitely.
Create Approval Delegation Records
Set up approval coverage by specifying who handles your approval responsibilities and for how long.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.approvals_approval_delegation.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
