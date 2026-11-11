---
article_id: ind.sf_contracts_manage_and_test_contract_extraction_instructions.htm
title: Manage and Test Contract Extraction Instructions
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_manage_and_test_contract_extraction_instructions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configuration_of_fields_for_extraction_from_a_file.htm
fetched_at: 2026-10-13
---

# Manage and Test Contract Extraction Instructions

Set up and refine extraction instructions for standard and custom fields. Upload PDF files to test extraction results in the Preview tab, adjust field-level instructions to improve LLM accuracy, and save the validated instructions to extraction templates for runtime use.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED	 
To prompt test instructions in Industries Einstein	

CLM Admin User

AND

Contracts AI User

AND

Prompt Template Manager

AND

NLP Service

AND

Scoring Framework Admin


To prompt test instructions in Document AI	

CLM Admin User

AND

Contracts AI User


To prompt test instructions in Multimodal Extraction	

CLM Admin User

AND

Contracts AI User

AND

Prompt Template Manager

From Setup, in the Quick Find box, enter Contracts AI, and then select Contract Extraction.
Open the extraction template that you want to modify.
Click the Preview tab.
If extraction results require refinement, go to the Entity Extraction and Clause Extraction tabs to update descriptions for custom fields and clauses. These descriptions are stored at the context attribute level and remain available even if mappings are reset. Model selection is available only when Document AI is enabled and can be changed from the Extract Document Fields section. For multimodal extraction, change the model using Prompt Builder. Model selection isn’t available for Industries Einstein.
Click Upload Files.
Find and select the file from your computer, and then click Open.
After the files are processed, the Show Response button appears.
Click Show Response.
In the Preview Prompt Response, review the extracted field and clause values based on the tab you’re viewing. To test clause extraction, open the Clause Extraction tab and click Show Response for the same uploaded file. If the results aren’t satisfactory, update the prompt instructions for the relevant entities and generate the response again. You can also change the document extraction model when applicable. Repeat this process until the results meet your requirements.
In the prompt response, you can see each mapped field and its extracted values.
Save your changes.
You can now use the prompt template during runtime to extract entity values.
The prompt instructions are saved to context mapping.
