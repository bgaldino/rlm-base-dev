---
article_id: ind.dro_configure_procedure_plan_definition_for_business_process_orchestration.htm
title: Configure Procedure Plan Definition for Business Process Orchestration
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_configure_procedure_plan_definition_for_business_process_orchestration.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.dro_orchestrate_sales_transaction_business_processes.htm
fetched_at: 2026-11-23
---

# Configure Procedure Plan Definition for Business Process Orchestration

Use the procedure plan definition to determine the correct context definition and mapping, and orchestrate the business process to create a sales transaction fulfillment request.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud
USER PERMISSIONS NEEDED
To create, update, and activate procedure plan definitions:	

Procedure Plan Access

AND

DRO Design Time User

Before you begin, extend the Sales Transaction context definition, map your entity to the new context definition, and activate the context definition. See Create Custom Context Definition and Map Business Objects.

TIP To orchestrate custom business objects, first create custom primary objects to define the process rules for each business process entity that you want to orchestrate. See Create a Custom Object.
Create a custom procedure plan definition.
From Setup, in the Quick Find box, enter Procedure Plan Definitions, and then select it.
Create a procedure plan definition by entering a title and a developer name.
Select DRO as the process type.
Select the object that you want to submit for orchestration as the primary object.
For example, Service Request or Case.
Select the custom context definition that you created from the Sales Transaction context definition.
Save your work.
Update and activate the procedure plan definition.
Open the procedure plan definition.
Select a value for the read context mapping.
Select the same value for the save context mapping.
NOTE The procedure plan definition doesn’t write any information to your object.
Save the plan definition.
Activate the procedure plan definition.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.dro_configure_procedure_plan_definition_for_business_process_orchestration.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
