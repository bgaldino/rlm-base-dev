---
article_id: ind.dro_define_conditions_for_a_fulfillment_step_to_run.htm
title: Define Conditions for a Fulfillment Step to Run
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_define_conditions_for_a_fulfillment_step_to_run.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_design_time_orchestration.htm
fetched_at: 2026-11-23
---

# Define Conditions for a Fulfillment Step to Run

You can prevent a fulfillment step from running until certain conditions are met.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To set conditions for a fulfillment step to run:	

Fulfillment Designer

OR

DRO Admin User

From the App Launcher, find and select Fulfillment Workspaces.
Locate a step you wish to add execution conditions to. Click  and select Configure Execution Rules.
Click Create Rule.
Choose whether the rule is based on a Sales transaction item or a fulfillment line item.
NOTE For fulfillment steps, you can evaluate conditions against Fulfillment Line Items. As the fulfillment system has already generated the necessary fulfillment records by this stage, the data is available for the rule to check.
Set the conditions.
Define the logic, if you choose Custom Condition Logic Is Met.
Select the resources to evaluate.
The resources are either sales transaction or fulfillment line item context tags as defined in the DRO context definition.
Save your work.
To skip the entire branch of remaining steps rather than just one step, turn on Skip Branch.
When the step's conditions aren't met, DRO skips the step and the branch that depends solely on it. For more information, see How Skipping a Fulfillment Branch Works.
How Skipping a Fulfillment Branch Works
A fulfillment branch contains an initial step and a series of dependent steps that follow it. When you turn on Skip Branch for a step and that step is skipped, the branch that depends on the step is also skipped because the remaining steps no longer apply. For example, if the Get Shipping Address step is skipped, the subsequent steps related to shipping are also skipped.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_define_conditions_for_a_fulfillment_step_to_run.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
