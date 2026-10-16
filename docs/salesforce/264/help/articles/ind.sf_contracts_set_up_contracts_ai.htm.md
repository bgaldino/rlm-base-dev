---
article_id: ind.sf_contracts_set_up_contracts_ai.htm
title: Set Up Contracts AI
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_set_up_contracts_ai.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contracts_ai_overview.htm
fetched_at: 2026-10-13
---

# Set Up Contracts AI

Enable generative AI settings and set up use case configurations to activate the standard action flows that extract and generate clauses from your contract.

Prerequisites

Assign the appropriate Contracts, Microsoft 365 Word, and Clause permission sets and the appropriate Contracts AI, and Einstein licenses.

For more information, see:

Permission Set Licenses for Contracts AI
Personas and Permission Set Licenses for Salesforce Contracts
Next Steps

After you assign permission sets and licenses, follow these instructions to complete the Contracts AI setup.

Compare Bulk and Single Document Extraction
Single-file extraction works well for new contracts that arrive individually. You upload a file directly to Salesforce and extract data from it immediately. Bulk extraction processes documents from an external repository connected through Data Cloud. The documents stay in the external repository and aren’t uploaded to Salesforce storage. Use bulk extraction to digitize a large volume of contracts.
Single Document Extraction with Contracts AI
Identify and extract contract fields and clauses from documents by using context definitions, prompts, and system-applied extraction methods. Use prompts and prompt templates to define the extraction logic.
Bulk Extraction with Contracts AI
Process documents directly from external repositories without uploading each file individually. Use Data Cloud and Document AI to extract large volumes of contract data and convert unstructured data into structured records. Create templates to define which contract fields and clauses to extract.
Turn On Clause Generation in Contracts AI
Generate clause content by using Contracts AI. The standard prompt template runs automatically during clause generation and defines how content is generated.
