---
article_id: ind.approvals_core_actions_override_approval_work_item.htm
title: "Flow Core Action: Override Approval Work Item"
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_core_actions_override_approval_work_item.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_building_blocks_of_advanced_approvals.htm
fetched_at: 2026-11-23
---

# Flow Core Action: Override Approval Work Item

Update the status of an approval work item to reflect the approval admin's decision, allowing admins to override the decision for any assignee.

REQUIRED EDITIONS
View supported editions for Flow Approval Processes
Special Access Rules
To use this action, you need the Approval Admin user permission.

To override the approval work item, go to Flow Builder, add an Action element to your flow. In the New Action field, enter Override and select Override Approval Work Item.

Set Input Values
FIELD	DESCRIPTION
Approval Decision	

This is a required field. Action that the approval admin took for the unreviewed approval work item. Valid values are:

Approve
Reject

Approval Work Item ID	This is a required field. ID of the unreviewed approval work item to be reviewed by the approval admin.
Channel Type	

This is an optional field. Type of channel where the request to review the approval work item originated. Valid values are:

InvocableAction
Slack
ApprovalRecord

The default value is InvocableAction.


Comments	This is an optional field. Comments that the approval admin enters about their decision to approve or reject an unreviewed approval work item.
Usage
This action requires API version 62.0 or a later version in the flow.
You can only override an approval submission if it's status is Assigned.
SEE ALSO
Provided Flow Core Actions
Flow Approval Processes Flow Core Actions

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.approvals_core_actions_override_approval_work_item.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
