---
article_id: ind.sf_contracts_singleext_promptbuilder_extraction.htm
title: Customize Multimodal Document Extraction with Prompt Builder
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_singleext_promptbuilder_extraction.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_singleext_overview.htm
fetched_at: 2026-10-13
---

# Customize Multimodal Document Extraction with Prompt Builder

Refine extraction for complex clauses and contract fields by modifying prompts and using a different model. Use Prompt Builder to create a new version of the standard template. This step is optional and not required for standard extraction.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To modify the standard prompt template:	

CLM Admin User

AND

Prompt Template Manager

Make sure that the Prompt Builder and Einstein licenses are enabled in your org.

From Setup, in the Quick Find box, enter Prompt Builder, and then select Prompt Builder.
Open the prompt template used for contract and clause extraction.
	
Entity Extraction	For standard contract data retrieval.
Document Clause Extraction	For retrieving clause data.
Modify the prompt.
When results are inaccurate, first try switching the model before modifying the prompt instructions. Changing the model often resolves accuracy issues without requiring complex prompt engineering.
Save a new version of the template.
In Prompt Builder, use the model selector to change the model.
If needed, add instructions to improve accuracy by including contextual guidance, such as document sections or formatting, and refine how clauses or values are identified.
Modify the base prompt descriptions only if model switching doesn’t resolve the issue. To prevent hallucinations, avoid changing the default fields.
Save the template and activate it.
Preview the extraction results.
Go to the extraction template’s Preview tab.
Upload a document, and click Show Response.
Review the extracted results.
If needed, change the LLM model and refine the prompt further.
The extraction behavior updates based on the modified prompt and selected model.
