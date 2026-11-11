---
article_id: ind.sf_contracts_contract_and_clause_extraction_with_contracts_ai.htm
title: Contract and Clause Extraction with Contracts AI
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_and_clause_extraction_with_contracts_ai.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contracts_ai_overview.htm
fetched_at: 2026-10-13
---

# Contract and Clause Extraction with Contracts AI

Use generative AI to automate the extraction of contract fields and clauses from PDF documents. Reduce manual data entry errors, track extractions from a unified interface, and improve clause-extraction precision with thumbs-up or thumbs-down feedback.

The contract author can map contract reference details, such as account name and contract owner, to Salesforce by accepting the extracted details or modifying the mapping. Additionally, they can specify or modify the contract term, start, and end dates and verify the extracted clauses, making necessary modifications to the clause content. After the contract author is satisfied with the extracted contract details and has made necessary modifications, they can create a Salesforce contract record from the PDF document. Authors with Clause Designer user permissions can add extracted clauses to the clause library. First, the clause is added in the draft state and follows the clause life cycle to be included in the clause library.

IMPORTANT Generative AI supports PDF files only for extraction.
Contract Extraction Results
The status of the contract extraction is restricted to five statutes.
Extract Contract Details and Clauses with Contracts AI
Use Contracts AI to identify and extract contract details and clauses from a PDF. You can initiate multiple extractions simultaneously. The in-app notification shows the success or failure of the contract extraction and when an extracted clause is added to the clause library.
Review Extracted Clause
Clause designers can directly review the extracted clause content and mark it as reviewed without any modifications. You can edit or delete the extracted clause using the action dropdown next to the clause.
Redraft Extracted Clause
Clause designers can redraft the extracted clause content with generative AI, and then add the updated clause directly to the clause library.
Create Contract Record
After you review the extracted contract details and clauses, create a Salesforce contract record with the extracted contract details. Contract creation deletes the extraction record from the Contract Extraction Results, and the contract data is mapped to the contract fields in Salesforce.
Limitations of Field Values Extraction Using Contracts AI
This topic outlines the limitations of the Contracts Extraction feature, detailing various field types and their specific challenges. Each limitation requires specific manual adjustments after extraction to ensure data accuracy and integrity.
