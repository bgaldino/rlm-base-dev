---
article_id: ind.approvals_delegation_considerations.htm
title: Considerations for Advanced Approval Delegations
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_delegation_considerations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals_considerations.htm
fetched_at: 2026-09-07
---

# Considerations for Advanced Approval Delegations

Keep these considerations in mind when working with approval delegation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
A delegate user must be active. Inactive users can't be set as delegate users.
When delegating to a queue or group, the queue or group must have at least 1 member.
A reviewer can't delegate to themselves.
Delegates receive email notifications when approval work items are assigned or reassigned. Slack notifications aren't sent to delegates.
Approval Delegation records can't be deleted. To end a delegation early, update the end date.
Delegations for the same approver can't overlap in date ranges.
