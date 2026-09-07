---
article_id: ind.rev_agent_topic_approval_management.htm
title: "Subagent: Approval Management"
source_url: https://help.salesforce.com/s/articleView?id=ind.rev_agent_topic_approval_management.htm&type=5&release=264
release: 264
release_name: Winter '27
area: agents
parent_article: ind.rev_agent_approval_agent.htm
fetched_at: 2026-09-07
---

# Subagent: Approval Management

Manage approval work items and submissions by summarizing, approving, rejecting, or recalling requests, with optional comments.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
Subagent Details
API Name	ApprovalManagement
Included actions	

Identify Record by Name

Get Record Details

Review Approval Work Item

Recall Approval Submission

Examples of Utterances Classified to This Topic
USER SAMPLE INPUT	ACTION ENGAGED	AGENT RESPONSE
"Find the approval work item named AWI-000000001."	Identify Record by Name	The agent looks up the approval work item by the provided name and returns the matching record.
"Do we have an approval submission called AS-000000006?"	Identify Record by Name	The agent checks whether an approval submission with that name exists and returns the matching record reference.
"Summarize this approval request."	Get Record Details	The agent resolves the approval work item from the current page context and returns a concise summary of its key fields.
"What's the reviewer and status on AWI-000000008?"	Get Record Details	The agent retrieves the approval work item's details and reports the assigned reviewer and current status.
"Go ahead and approve AWI-000000008."	Review Approval Work Item	The agent confirms the approval decision, asks whether the user wants to add a comment, and submits the approval.
“Reject this work item with the comment 'budget exceeded.'"	Review Approval Work Item	The agent confirms the rejected decision and exact comment text, then submits the rejection.
"I need to withdraw the approval I submitted for this quote."	Recall Approval Submission	The agent finds the approval submission related to the current quote, confirms the recall, asks for an optional comment, and recalls the submission.
"Recall the approval submission for this lead."	Recall Approval Submission	The agent finds the approval submission related to the current lead, confirms the recall, asks for an optional comment, and recalls the submission.
