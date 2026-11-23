---
article_id: ind.approvals_turn_on_smart_approvals.htm
title: Turn On Smart Approvals
source_url: https://help.salesforce.com/s/articleView?id=ind.approvals_turn_on_smart_approvals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: approvals
parent_article: ind.approvals_smart_approvals.htm
fetched_at: 2026-11-23
---

# Turn On Smart Approvals

To skip reviewing previously approved steps in an approval resubmission, turn on Smart Approvals.

From Setup, find and select Flows.
Open the flow that you use for managing approvals.
Select an approval step.
In the step’s properties tab, select Use Smart Approval.
To skip specific start conditions from Smart Approvals evaluation, enter each start condition number separated by a comma in the Smart Approval Skip Conditions field.
Condition numbers match the order of conditions in the Requirements to Start Step list, starting at 1. For example, if a step has four start conditions and you enter 2, 4, Smart Approvals skips the second and fourth conditions.
If you enter an invalid value or provide a resource, Smart Approvals doesn't skip the condition.
Save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.approvals_turn_on_smart_approvals.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
