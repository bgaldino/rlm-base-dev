---
article_id: ind.dro_create_a_fulfillment_task_assignment_rule.htm
title: Create a Fulfillment Task Assignment Rule
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_create_a_fulfillment_task_assignment_rule.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_design_time_orchestration.htm
fetched_at: 2026-11-23
---

# Create a Fulfillment Task Assignment Rule

Create reusable rules to automatically assign manual tasks to users based on the criteria and conditions defined in the rule.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To create a fulfillment task assignment rule:	

Fulfillment Designer

OR

DRO Admin User

Dynamic Revenue Orchestrator applies the rule and assigns the task to a person based on the matching source in the step definition, step assignment method, results of the applied conditions, and priority of the rule.

From the App Launcher, find and select Fulfillment Task Assignment Rules.
Click New.
Enter a unique name for the assignment rule.
Select a source for the task assignment.
Select User or Queue as the destination, and then search for and select the user or queue that you want to assign the task to.
Enter a priority value for the rule to run. Rules execute in order from lowest to highest priority. For example, a rule with priority 1 runs before a rule with priority 2.
Select the step assignment method to be used when you assign the task to a user.
Save your work.
To save the rule and see the details pane for the rule, click Save.
To save the rule and then define when the rule runs during fulfillment, click Save & Add Condition.
Define the Conditions for a Fulfillment Task Assignment Rule
Optionally, set up the conditions that must be met for the assignment rule to run.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_create_a_fulfillment_task_assignment_rule.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
