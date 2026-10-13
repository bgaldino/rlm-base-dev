---
article_id: ind.sf_contracts_billing_considerations_for_contract_agent.htm
title: Billing Considerations for Contract Search
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_billing_considerations_for_contract_agent.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contract_search_for_contract_ai.htm
fetched_at: 2026-10-13
---

# Billing Considerations for Contract Search

Use of the Summarize Contract Document and Query Contract Document actions impacts credit consumption. These actions rely on Data Cloud for document indexing and querying, and invoke generative AI through Agentforce to deliver summaries and answers.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, and Unlimited Editions with the Revenue Cloud Advanced, Agentforce for Sales, Agentforce for Platform, Agentforce for Service, or an Agentforce for Industry add-on license..
TIP

This feature has access to Digital Wallet, a free account management tool that offers near real-time consumption data for enabled products across your active contracts. Access Digital Wallet and start tracking your org's usage. To learn more, see About Digital Wallet.

DIGITAL WALLET CARD	USAGE TYPE	DESCRIPTION	NOTES
Data Services	Data Queries	

Usage is calculated based on the number of records processed.

The count of records processed depends on the structure of a query as well as other related factors such as the total number of records in the objects being queried.

	See Data Cloud Billable Usage Types.
Data Services	Data Spaces	Usage is calculated based on the number of data spaces beyond the default data space.	See Data Cloud Billable Usage Types.
Einstein Requests	

Standard Prompts

Basic Prompts

Advanced Prompts

	

Usage is calculated based on two factors: the number of direct requests to the LLM via the LLM gateway, and whether the gateway uses a Salesforce managed large language model. The specific category depends on the model that is used. See Large Language Model Support to find out which usage types apply.

All Standard, Basic, and Advanced prompts process up to 2,000 tokens per prompt. Token usage is rounded up in 2,000-token increments. All Standard, Basic, and Advanced prompts that exceed this limit will be metered as multiple prompts, with each additional 2,000-token chunk counting as a new prompt. For example, a prompt with a total of 6,500 input and output tokens will be metered as 4 prompts.

Tokens are units of data processed by the AI models.

NOTE Advanced Prompts were launched with a designated multiplier listed in the Agentforce Flex Credits Rate Card. Salesforce will start metering the use of Advanced Prompts on July 21, 2026.
	This usage type isn’t billed when it's associated with a generative AI action that qualifies as unmetered human context usage. For more information, see Metering for Agentforce and Generative AI Usage.
Flex Credits	Standard Action	

Usage is determined by the number of standard actions called by the agent in a text conversation. Currently, every standard action called by the agent is metered as one standard action, irrespective of the number of tokens processed.

Standard agent actions are actions that are available out-of-the-box. To check the list of Standard actions, see Standard Action Reference.

NOTE Use of some standard agent actions require that a subscription has been purchased for each user that accesses these actions, such as a subscription to Agentforce for Sales Add-on or Agentforce for Service Add-on. To determine which subscription is required for such standard actions, see Standard Action Reference at Standard Action Reference. While this requirement is not technically enforced yet, users who don’t have the required add-on license will lose access to such actions for which they don’t have a license when the requirement is enforced.
	This usage type applies only when Agentforce is configured. This usage type isn’t billed when it's associated with a generative AI action that qualifies as unmetered human context usage. For more information, see Metering for Agentforce and Generative AI Usage.

For more information on how usage is billed, refer to your contract or contact your account executive.

When you use the contract search, credits can be consumed in usage types on other consumption cards by related features such as or Audit and Feedback.
