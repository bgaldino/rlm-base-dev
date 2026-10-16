---
article_id: ind.approvals_approval_process_execution.htm
title: Approval Process Execution
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_approval_process_execution.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals_considerations.htm
fetched_at: 2026-09-07
---

# Approval Process Execution

This section covers errors and expected behaviors that occur after a flow is activated and in use.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
Execution Errors

When a flow execution results in an errored state, this is often due to multiple steps trying to lock the same record simultaneously or because of issues rendering the Work Item screen guide. Administrators should be directed to review the flow in Paused and Failed Interviews within Setup or check the error email sent to the admin user for specific troubleshooting details.

Multiple Reviewers Conflict

A user may receive an error stating a work item is already completed if they attempt to review it at the same time as another member of their group or queue. The system correctly processes the first user's completion request and rejects the second user's request. No action is required as this is normal system operation.
