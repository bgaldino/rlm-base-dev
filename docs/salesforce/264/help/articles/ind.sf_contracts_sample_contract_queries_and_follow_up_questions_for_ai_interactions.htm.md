---
article_id: ind.sf_contracts_sample_contract_queries_and_follow_up_questions_for_ai_interactions.htm
title: Sample Contract Queries and Follow-Up Questions for AI Interactions
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_sample_contract_queries_and_follow_up_questions_for_ai_interactions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_search_summarize_and_interact_with_contracts_using_ai.htm
fetched_at: 2026-10-13
---

# Sample Contract Queries and Follow-Up Questions for AI Interactions

Use the following examples to help you write effective natural-language prompts when using Contract Search with AI. These samples include queries that retrieve relevant contracts and follow-up questions you can ask to explore contract details. The AI maintains context across interactions, so you can continue asking questions without repeating information.

PROBLEM STATEMENT	SEARCH QUERY	WHAT IT RETURNS	FOLLOW-UP QUESTIONS
I want to find contracts with Cloud Kicks that have short payment terms and delivery failure protection.	Show me all contracts with Cloud Kicks where the payment term is less than 30 days and there is protection against failure of delivery.	Contracts with short payment terms and delivery protection clauses.	
What is the exact payment term?
What qualifies as delivery failure?
What happens if delivery fails?

I’m looking for contracts that include protection for unforeseen circumstances and fast delivery schedules.	Pull up all agreements where the delivery schedule is under 7 days and there are terms that protect against unforeseen circumstances.	Contracts with expedited delivery and force majeure language.	
Are natural disasters included?
Is advance notice required?
Who pays in case of delay?

I need to identify contracts where damages can be waived off.	Provide me the list of agreements where there are no additional damages to be paid in lieu of any untoward incident.	Contracts that limit liability or waive damages.	
What incidents are covered?
Is this waiver mutual?
Are any damages explicitly excluded?

I want a scenario-specific result for a particular region and event.	Show me all contracts with Cloud Kicks where the payment term is less than 30 days and there is protection against failure of delivery due to an upcoming storm in the state of California.	Contracts that combine delivery clauses with location- and scenario-specific language.	
Is the storm clause explicit?
What is the response timeline?
Who bears the risk?

I want to review the terms related to deliverables and obligations in an agreement.	Find the agreement with Cloud Kicks that outlines delivery of software updates.	Relevant section(s) of the contract discussing delivery terms and obligations.	
Summarize the obligations.
What’s the delivery timeline?
Are there penalties for delays?

I’m looking for financial terms in the agreement with Ursa Major Solar.	Get the contract with Ursa Major Solar for cloud service billing.	Contract(s) that contain financial terms like fees, billing schedules, or penalties.	
Summarize the financial terms.
Is there an advance payment?
Are refunds or interest clauses included?
