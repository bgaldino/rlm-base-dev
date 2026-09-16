---
article_id: ind.approvals_add_partners_to_approval_steps.htm
title: Advanced Approval Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_add_partners_to_approval_steps.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_manage_advanced_approvals.htm
fetched_at: 2026-09-07
---

# Advanced Approval Objects

Learn about the objects and list views available in Advanced Approvals.

OBJECT	FUNCTIONALITY
Approval Submission	Represents the master record of an approval request, tracking its overall progress and storing the requests assigned to various reviewers.
Approval Work Item	Represents an approval step assigned to a specific user, group, or queue. It tracks the step's status and stores the reviewer's final decision, such as Approved or Rejected.
Approval Submission Detail	Stores a detailed audit trail for the entire approval process, logging every change on the main request or any of its individual tasks.
Approval Work Item Criteria	Represents the approval logic for the workflow. It contains the logical conditions used to evaluate the entry and exit criteria for each approval step.
Approval Work Item Condition	Stores the outcome of the approval logic, including the entry and exit conditions evaluated for every approval step.
Record Sharing

By default, any user with access to an approval submission has access to all its associated approval work items. To limit visibility, in Sharing Settings, set the sharing default of the Approval Work Item object to Private. This setting prevents reviewers at one step from seeing the work items assigned to reviewers at other steps. Reviewers also see only the work items that they're directly assigned or delegated to.

The owner and submitter of the approval submission can view the associated work items but can't review or reassign them.

To extend access to other users of the approval work item, create criteria-based sharing rules. See Create Criteria-Based Sharing Rules.

Default List Views

Based on record access, the following lists are available to users. Customize these lists by updating filter criteria or displayed columns. You can also create a new list view or clone an existing one to suit your needs.

All Approval Submissions: All submission records that you have access to, irrespective of the record's status.
My Approval Submissions: All submission records that are assigned to you.
Pending Approval Submissions: All submission records awaiting review that you have access to.
All Approval Work Items: All work item records that you have access to, irrespective of the record's status.
Assigned Approval Work Items: All work item records awaiting your review, including those assigned through groups, queues, or delegations.
All Approval Submission Details: All submission detail records that you have access to.
SEE ALSO
Data Model Gallery: Revenue Management Advanced Approvals Data Model
Considerations for Approval Objects
Considerations for Approval List Views
