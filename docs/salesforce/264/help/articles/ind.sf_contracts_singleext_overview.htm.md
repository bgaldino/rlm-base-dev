---
article_id: ind.sf_contracts_singleext_overview.htm
title: Single Document Extraction with Contracts AI
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_singleext_overview.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_set_up_contracts_ai.htm
fetched_at: 2026-10-13
---

# Single Document Extraction with Contracts AI

Identify and extract contract fields and clauses from documents by using context definitions, prompts, and system-applied extraction methods. Use prompts and prompt templates to define the extraction logic.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
What You Can Do
Extract contract fields and clauses from documents.
Define extraction logic by using prompts.
Review extraction results before running extraction.
Customize extraction by using extraction templates and Prompt Builder.
How Contract Extraction Works

Contracts AI processes documents by using context definitions, prompts, and AI-driven extraction methods to extract structured contract data. The main components include:

Context definitions define the structure of data to extract and determine what data to extract, not how to perform extraction. They specify:
Attributes (fields) to extract
Relationships between attributes
Data structure for output
Context mapping defines where to map the extracted data.
Maps extracted values to Salesforce fields.
Mapping doesn’t influence how extraction works.
Use AI models to process document content based on the extraction method. You don’t select extraction methods manually.
Prompts are instructions that guide how to identify and extract values from the document. Prompts are the primary way to control extraction behavior.
Summary
Prompts define extraction logic.
Context defines the extraction structure.
Mapping defines the output destination.
Admin configures the extraction methods.
Extraction behavior is validated by using preview.
Extraction Methods in Contracts AI

Contracts AI uses multiple extraction methods to process documents and extract contract data. These methods run in a predefined order based on the configurations.

Document AI
Industries Einstein
Multimodal Extraction
Context Definitions and Prompts for Document Contract Extraction
A context definition specifies which contract data to extract and how it is structured, and you map attributes to object fields so Salesforce stores the results correctly. A prompt identifies which data to extract from a document, and prompt templates let you reuse prompts and standardize that behavior.
Single Document Extraction Methods and Licensing Requirements for Contracts AI
Contracts AI offers three extraction methods, each with different performance characteristics, file requirements, and licensing needs. Compare the methods to determine which ones to configure for your org.
Single Document Extraction Methods Fallback Behavior
Contracts AI provides different extraction methods to identify and pull data from uploaded documents. Each method has specific performance characteristics, and fallback behaviors.
Turn On Document AI for Single Document Contract Extraction
Enable Document AI as the preferred extraction method for contract documents. When enabled, Document AI runs automatically and falls back to other configured methods when limits or conditions aren’t met.
Turn On Multimodal Single Document Contract Extraction
Use multimodal extraction to extract contract details and draft clauses.
Turn On Industries Einstein AI Single Document Extraction
You must define the settings and enable standard action flows to enable users to draft clauses and extract contract details using Industries AI extraction method.
Customize Multimodal Document Extraction with Prompt Builder
Refine extraction for complex clauses and contract fields by modifying prompts and using a different model. Use Prompt Builder to create a new version of the standard template. This step is optional and not required for standard extraction.
Configure Fields for Extraction With Contracts AI
Context Service uses extraction templates to identify and extract required field values from documents. Customizing field prompt descriptions guides generative AI to improve the accuracy of field value extraction based on predefined field mappings. These configurations apply across the Document AI, Multimodal, and Industries Einstein extraction methods.
SEE ALSO
Contract and Clause Extraction with Contracts AI
Compare Bulk and Single Document Extraction
