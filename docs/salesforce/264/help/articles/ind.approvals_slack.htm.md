---
article_id: ind.approvals_slack.htm
title: Approvals in Slack
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_slack.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_advanced_approvals.htm
fetched_at: 2026-09-07
---

# Approvals in Slack

With Approvals in Slack, approvers can approve or reject requests and add comments without leaving Slack, while submitters receive real-time updates on their requests. Your Slack actions are saved to Salesforce, so approval data stays consistent across channels.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals or Flow Approval Processes is enabled

In Slack, reviewers can view approval-related details, such as the work item name, the related record, the submitter, and the condition that triggered the request. The approval and related records are visible in the Slack unfurl and flexpane components. To manage the fields in these components, see Slack Record Layout.

When reviewers approve or reject requests in Slack, Salesforce automatically updates the corresponding approval records. For example, approving or rejecting a request updates the approval work item's Status and Comments fields, along with the Action Channel Name field on the related approval submission detail.

Notifications
In the Salesforce Slack app, notifications are sent as direct messages to individual reviewers.
When an approval step is assigned to a public group or queue, each active member receives a direct message.
To notify group and queue members of approval requests in a shared channel, the approval designer can specify a Slack channel in the approval step.
If Dynamic Approval Notifications is enabled, direct message notifications also include an AI-generated summary of the approval request.
Turn On Slack Notifications for Approvals
Connect Salesforce to your Slack workspace so that users can receive and act on approval requests in Slack.
Post Approval Notifications to a Slack Channel
Configure an approval step to post its notification to a specific Slack channel instead of sending it to the assigned group or queue.
