---
article_id: ind.rev_agent_topic_summarize_multiple_approval_work_items.htm
title: "Subagent: Summarize Multiple Approval Work Items"
source_url: https://help.salesforce.com/s/articleView?id=ind.rev_agent_topic_summarize_multiple_approval_work_items.htm&type=5&release=264
release: 264
release_name: Winter '27
area: agents
parent_article: ind.rev_agent_approval_agent.htm
fetched_at: 2026-09-07
---

# Subagent: Summarize Multiple Approval Work Items

Filter approval work item records and summarize them in aggregate, providing per-record details so reviewers can quickly understand the context of each approval.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
Subagent Details
API Name	SummarizeMultipleApprovalWorkItems
Included actions	

Query Records

Get Record Details

Examples of Utterances Classified to This Topic
USER SAMPLE INPUT	ACTION ENGAGED	AGENT RESPONSE
"Summarize my most recent Approval Work Item and tell me what I need to look at."	Query Records	The agent searches for the latest approval work item assigned to the user, fetches its record details, and generates a summary highlighting key fields and items requiring attention.
"Summarize the 10 most recent approval work items of the contracts."	Query Records	The agent searches for the 10 most recent approval work items linked to the records and provides a summarized breakdown of their statuses and key details.
"Summarize the most recent 10 approval work items on this record."	Get Record Details	The agent searches for approval work items associated with the record, retrieves the 10 latest entries, and presents a summarized list of their current progress.
"Summarize the 10 most recent approval work items assigned to me."	Get Record Details	The agent queries approval work items filtered by the current user's ID as the assignee, orders them by date, and generates a summary of the 10 most recent items.
