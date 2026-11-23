---
article_id: ind.approvals_lightning_components.htm
title: Configure Lightning Components for Approvals
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_lightning_components.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_design_advanced_approvals.htm
fetched_at: 2026-11-23
---

# Configure Lightning Components for Approvals

Add Lightning components to pages to enable users to track progress, preview an approval chain, and review outstanding approvals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions where Advanced Approvals is enabled
USER PERMISSIONS NEEDED
To customize approval pages in Lightning App Builder:	Customize Application
LIGHTNING COMPONENT	DESCRIPTION	SUPPORTED PAGES
Approval Trace	Shows the approval work items associated with a record.	Any record page associated with an approval workflow.
Orchestration Work Guide	Shows pending approval work items to assigned users.	Any record page associated with an approval workflow.
Approval Workflow	Provides a preview of the approval process, including conditions, chain names, and assignees triggered when a record is submitted. This component is available only with Advanced Approvals.	Any record page associated with an approval workflow.
Chatter	Shows the activity feed for a record.	All approval and related record pages.
From Setup, in the Quick Find box, find and select Lightning App Builder.
On the record page that you want to add the component, click Edit.
Drag the component to the canvas.
To edit the component properties, click it.
For components such as Approval Workflow, enter the API name of the autolaunched flow that triggers your approval process.
Save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.approvals_lightning_components.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
