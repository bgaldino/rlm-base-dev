---
article_id: release-notes.rn_advanced_approvals.htm
title: Advanced Approvals
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_advanced_approvals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_revenue.htm
fetched_at: 2026-09-30
---

# Advanced Approvals

Reach every active member of an assigned group or queue in Slack through direct messages or channels. Keep approvals moving during planned absences with Advanced Approval Delegation. Protect sensitive approval work items in multistep approvals with separate sharing settings that limit reviewer visibility.

Extend Slack Approval Notifications to Group and Queue Members
Reach every active member of an assigned group or queue via Slack notifications. Each active member receives a direct message regarding the approval request. Approval designers can also configure their approval workflows to post request notifications to a Slack channel. If you turn on Dynamic Approval Notifications, the direct message includes an AI-generated summary of the approval request. Previously, approval steps assigned to groups or queues didn't generate Slack notifications.
Keep Approval Workflows Moving with Advanced Approval Delegation
Prevent approval delays during planned absences by using Advanced Approval Delegation. Reviewers can assign their responsibilities to a user, group, or queue for a defined period or indefinitely by creating approval delegation records. When you turn on Advanced Approval Delegation, delegations configured on reviewer user records no longer apply. Reviewers must create approval delegation records to set up their delegations.
Limit Approval Work Item Visibility to Keep Review Steps Confidential
Prevent reviewers at one step from viewing the work items assigned to reviewers at other steps. You can now set the sharing model to private to control who can view each work item, independent of approval submissions. By default, access to an approval submission extends to all its associated work items. To grant read access to other users or groups, create criteria-based sharing rules on the approval work item object.
New Objects in Advanced Approvals
Store and access more data with the new Advanced Approval objects.
