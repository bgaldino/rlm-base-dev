---
article_id: ind.sf_contracts_singleext_concept_one.htm
title: Context Definitions and Prompts for Document Contract Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_singleext_concept_one.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_singleext_overview.htm
fetched_at: 2026-10-13
---

# Context Definitions and Prompts for Document Contract Extraction

A context definition specifies which contract data to extract and how it is structured, and you map attributes to object fields so Salesforce stores the results correctly. A prompt identifies which data to extract from a document, and prompt templates let you reuse prompts and standardize that behavior.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions

Context definitions and prompts work together to control how contract data is extracted and stored. Context definitions model what you extract, they describe the structure of that data, including fields, relationships, and how values are organized.

Prompts supply the field-level instructions that guide how each value is identified and interpreted from documents during extraction. Prompt templates let you reuse those instructions so behavior stays consistent where you need the same logic in more than one place. Context mapping connects attributes in the context definition to Salesforce object fields so extracted values are stored on the right records and fields.

For example, a context definition can include a field for contract start date, and the prompt for that field describes how the system should find and extract that date from the document; mapping determines which Salesforce field receives the result.
