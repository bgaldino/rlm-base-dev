---
article_id: ind.sf_contracts_set_up_agentforce_employee_agent_aea_for_contract.htm
title: Set Up a Contract Agent
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_agentforce_employee_agent_aea_for_contract.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_document_overview.htm
fetched_at: 2026-10-13
---

# Set Up a Contract Agent

Create and configure a contract by using Agentforce Employee agent template to help your users efficiently find and manage contract-related information. After creating the agent, add essential contract search topics, and assign permissions to ensure the right users have access to relevant contract insights and functionalities.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.
USER PERMISSIONS NEEDED
To set up a contract agent:	

Data Cloud Architect [Home Org]

OR

Data Cloud One [Companion Org]

AND

CLM Admin User

AND

Contracts AI User

Create a Contract Agent. and update these fields:
FIELD	VALUE
Name	Contract Agent
API Name	Contract_Agent
Description	Use a contract agent to ask questions or generate summaries from contract documents using natural language.
Add Subagents to the Created Contract Agent.
In the Explorer panel, click the plus icon next to the Experience Management subagent and select Add from Asset Library.
Find and select Contract Document Overview.
(Optional) To create a task or set reminders, select Manage Deals. To draft and send emails, select General CRM.
Click Add to Agent.
In the Subagents section, remove General FAQ.
Grant Users Access to the Contract Agent.
In Setup, find and select Permission Sets.
Click New.
Enter the Label as AccessContractAgent.
Save your changes.
In the Apps section, click Agent Access.
Click Edit and move Contract Agent from Available Agents to Enabled Agents.
Save your changes.
Assign the created permission set to admin and business users.
SEE ALSO
Create an Agent from an Agentforce Employee Agent Template
Agent Topic: Manage Deals
Agent Topic: General CRM
Agentforce Glossary of Terms
