---
article_id: ind.sf_contracts_bulk_extra_compare.htm
title: Compare Bulk and Single Document Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_bulk_extra_compare.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contracts_ai.htm
fetched_at: 2026-10-13
---

# Compare Bulk and Single Document Extraction

Single-file extraction works well for new contracts that arrive individually. You upload a file directly to Salesforce and extract data from it immediately. Bulk extraction processes documents from an external repository connected through Data Cloud. The documents stay in the external repository and aren’t uploaded to Salesforce storage. Use bulk extraction to digitize a large volume of contracts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
ASPECT	BULK EXTRACTION	SINGLE DOCUMENT EXTRACTION
Processing	Asynchronous	Synchronous
Volume	Many documents from an external repository	One document at a time
Configuration	Requires a saved bulk extraction configuration	No configuration needed
Source	External repository via a Data Cloud connector	The user uploads the file
File storage before processing	Files remain in the external repository	File is uploaded to Salesforce
Model choice	Limited to Document AI certified multimodal models	Broader model choices are available
When to use	Digitizing large volumes of legacy contracts	Processing individual contracts on demand
Supported File Type	PDF	PDF
Supported Languages	English	English
Fields, clauses, context for extraction	

Same template and Contracts AI setup

Requires a bulk extraction configuration, Data Cloud connector path, and asynchronous processing.

	Same template setup possible; file is uploaded; synchronous flow.
Field extractions limit	Maximum 50 fields per template	Maximum 50 fields per template
SEE ALSO
Bulk Extraction with Contracts AI
Single Document Extraction with Contracts AI
