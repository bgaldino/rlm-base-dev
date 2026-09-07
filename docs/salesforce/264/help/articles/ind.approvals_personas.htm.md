---
article_id: ind.approvals_personas.htm
title: Advanced Approvals Personas and Permissions
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_personas.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_manage_advanced_approvals.htm
fetched_at: 2026-09-07
---

# Advanced Approvals Personas and Permissions

Explore the different types of users who work with Advanced Approvals and the permissions they need.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled

To begin, create users for Advanced Approvals. Each user must be assigned a profile, which defines their default settings. Grant specific access by assigning the appropriate permissions. A user can have many permissions.

APPROVALS PERSONA	WHAT PERSONAS CAN DO	PERMISSION NAME
Approval Designer	Design and activate approval workflows.	
Manage Flow
Approval Designer
Read on Approval Submission

Approval Submitter	Initiate submissions and submit or recall them for approval.	
Run Flows
Read on Approval Submission

Approval Reviewer	Receive notifications and review approval work items. A reviewer can be a user, group, or queue.	
Run Flows
Read on Approval Submission

Approval Delegate	Review and act on approval work items on behalf of the original reviewer during an active delegation period. Delegates receive email notifications for assigned work items.	
Run Flows
Read on Approval Submission

Approval Administrator	Manage organization-wide settings and modify, recall, or cancel submissions and review or override any work item. An approval admin also has access to work item conditions and criteria.	
Run Flows
Approval Admin
Read on Approval Submission
