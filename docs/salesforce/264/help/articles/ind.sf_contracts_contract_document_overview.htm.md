---
article_id: ind.sf_contracts_contract_document_overview.htm
title: Agentforce for Contract Search
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_document_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contract_search_for_contract_ai.htm
fetched_at: 2026-10-13
---

# Agentforce for Contract Search

Use Agentforce to power AI-driven contract search. The Contract Document Overview topic lets contract managers and legal analysts summarize documents or ask questions about specific clauses. Customize the topic and prompt templates to match your business needs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, and Unlimited Editions with the Agentforce for Sales, Agentforce for Platform, or Agentforce for Service add-on, Revenue Cloud Advanced, or Agentforce for Industries (X).
Contract Document Overview Topic Details
API Name	ContractDocumentOverview
Included Agent Actions	

Query Contract Document

Summarize Contract Document

*This action executes one or more prompt templates.

Examples of Utterances Classified to This Topic
INSTRUCTIONS	EXAMPLE UTTERANCE	AGENT RESPONSE	ACTION ENGAGED
Retrieve a specific clause or data point.	“What are the payment milestones and due dates?”	“Milestone 1: Initial payment of $50,000 due within 10 business days of the Effective Date. Milestone 2: $50,000 due upon delivery of beta deliverables. Milestone 3: $50,000 due upon final acceptance of deliverables.”	QueryContractDocument
Generate a concise summary of the entire contract.	“Summarize this contract agreement.”	“This Consulting Services Agreement between Cloud Kicks and Zenith LLC establishes a 30-day notice period for termination, outlines a $150,000 annual retainer plus expense reimbursement, includes confidentiality and IP assignment clauses, and is governed by California law.”	SummarizeContractDocument
Summarize in defined chunks for lengthy contracts.	“Summarize this contract and keep chunk limit as 25.”	“Chunk 1 (lines 1–25): Parties, recitals, definitions… Chunk 2 (lines 26–50): Scope of services, deliverables… [and so on].”	SummarizeContractDocument
Guidelines and Considerations

Before using this topic, make sure you’ve completed the Contract Search setup and understand any constraints. See Configure Contract Search and Contract Search Limitations.

Set Up a Contract Agent
Create and configure a contract by using Agentforce Employee agent template to help your users efficiently find and manage contract-related information. After creating the agent, add essential contract search topics, and assign permissions to ensure the right users have access to relevant contract insights and functionalities.
Customize the Contract Document Overview Topic for Contract Search
Edit the Contract Document Overview topic to reflect your contract search use case and ensure the content aligns with your organization's compliance, legal, and business standards. Customizing this topic helps surface the most relevant context when users interact with contract search results or ask follow-up questions in Agentforce
Customize Prompt Templates for Contract Search
Tailor prompt templates to improve the accuracy and relevance of contract search results for your business needs. Using Prompt Builder, select standard templates such as Contract Q&A or Summarize Contract, save them as new versions, and then customize as needed.
Use Case: Customize the Contract Agent Experience
In this use case, a Salesforce Admin customizes the Contract Agent to help legal and sales teams find and summarize key clauses, then send insights via email. Learn how to tailor prompt templates and agent actions to reflect your internal standards.
