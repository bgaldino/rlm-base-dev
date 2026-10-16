---
article_id: release-notes.rn_adv_approvals_slack_notifications.htm
title: Extend Slack Approval Notifications to Group and Queue Members
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_adv_approvals_slack_notifications.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_advanced_approvals.htm
fetched_at: 2026-09-30
---

# Extend Slack Approval Notifications to Group and Queue Members

Reach every active member of an assigned group or queue via Slack notifications. Each active member receives a direct message regarding the approval request. Approval designers can also configure their approval workflows to post request notifications to a Slack channel. If you turn on Dynamic Approval Notifications, the direct message includes an AI-generated summary of the approval request. Previously, approval steps assigned to groups or queues didn't generate Slack notifications.

Where: This change applies to Lightning Experience in Enterprise, Unlimited, and Developer editions where Advanced Approvals is enabled.

How: To send group and queue notifications in a Slack channel, open your approval workflow in Flow Builder. Go to the properties panel of an approval step, and select Send approval request to Slack channel. Specify a Slack channel ID.

SEE ALSO
Salesforce Help: Approvals in Slack
