---
article_id: ind.sf_contracts_use_case_customize_the_contract_agent_experience.htm
title: "Use Case: Customize the Contract Agent Experience"
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_use_case_customize_the_contract_agent_experience.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_document_overview.htm
fetched_at: 2026-10-13
---

# Use Case: Customize the Contract Agent Experience

In this use case, a Salesforce Admin customizes the Contract Agent to help legal and sales teams find and summarize key clauses, then send insights via email. Learn how to tailor prompt templates and agent actions to reflect your internal standards.

Goals
Create and configure a custom Contract Agent
Customize the Contract Document Overview topic
Tailor the Summarize Contract and Contract Q&A prompt templates
Example

Your legal team wants to prioritize termination and confidentiality clauses in summaries. Meanwhile, sales needs fast access to renewal terms and discounts. Here's how set up and test the experience:

Set Up the Contract Agent

Go to Setup and then select Agentforce Agents and create a Contract Agent.

Remove General FAQ.
Add the Contract Document Overview.
(Optional) Add Manage Deals to create a task or set reminders.
(Optional) Add General CRM to draft and send emails
Activate the agent.
Assign the AccessContractAgent permission set to legal and sales users.
Customize the Agent Topic
Open the Contract Agent in builder and create a new version of Contract Document Overview.
Modify the instructions to reflect Acme’s compliance checklist:
Summarize must include confidentiality clauses, governing law, renewal terms, and early termination penalties. Include financial obligations if present.
Activate the updated version so all users get consistent, compliance-ready summaries.
Update Prompt Templates
In Prompt Builder, open the Summarize Contract prompt template and save it as a new version.
Modify the instruction section to say: Always include the contract’s effective and renewal dates, confidentiality obligations, jurisdiction, and discount conditions. Call out any risks, such as penalties or ambiguous clauses.
Activate the version.
Repeat this for the Contract Q&A prompt template to better guide answers for common legal queries. For example, update the instruction to say: “Always respond with the relevant clause text, followed by a short explanation in plain language. Focus on clauses related to renewal, termination, confidentiality, and discount commitments.”

Your legal and sales teams now get structured summaries, accurate answers, and instant follow-up options—all aligned with Acme's review standards. You’ve turned a generic agent into a smart, guided experience tailored for your users.
