---
article_id: ind.approvals_slack_channel_notifications.htm
title: Post Approval Notifications to a Slack Channel
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_slack_channel_notifications.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_slack.htm
fetched_at: 2026-09-07
---

# Post Approval Notifications to a Slack Channel

Configure an approval step to post its notification to a specific Slack channel instead of sending it to the assigned group or queue.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
USER PERMISSIONS NEEDED
To configure an approval step's properties:	Manage Flow
Find and copy your Slack channel ID.
From your Slack workspace, open a channel.
To open the channel details, click the channel name at the top.
In the About tab, copy the channel ID.
NOTE If your Slack channel is private, add the Salesforce app to the channel. Private channels don't have access to Salesforce by default. See Guide to apps in Slack.
Configure your approval workflow to send notifications to a Slack channel.
From Setup, find and select Flows.
Open the flow that contains your approval step.
Click the step to open its properties.
Set the Approver Type to Group or Queue.
Specify a group or queue.
Select Send Approval Notification to Slack Channel.
In the Slack Channel ID field, enter your Slack channel's ID. For example, C01234ABC.
Save and activate the flow.
