---
article_id: ind.sf_contracts_contract_search_limitations.htm
title: Contract Search Limitations
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_search_limitations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contract_search_for_contract_ai.htm
fetched_at: 2026-10-13
---

# Contract Search Limitations

Review the functional and configuration limitations that impact how contract search indexes, retrieves, and processes contract data.

LIMITATION	IMPACT
Encrypted Files	Files encrypted using Shield Platform Encryption or the "Encrypt Files and Attachments" setting are not ingested or searchable by contract search. See Shield documentation.
Day-0 Indexing	Only contracts created after contract search setup are indexed. Existing contracts present before setup are excluded from search results.
Contract Version	Search results include only the active version of a contract. Drafts, archived, or previous versions are not included.
Language	Contract search supports natural language queries in English only. Queries in other languages are not supported.
File Type	DOCX files are not supported in contract search.
Query Length	The query field on the contract search page accepts a maximum of 4,000 characters. Inputs exceeding this limit will be truncated or rejected.
Attachments	Attachments within contract document versions are not supported.
Companion org support	Contract Search doesn’t support querying from companion orgs that use custom dataspace configurations.
