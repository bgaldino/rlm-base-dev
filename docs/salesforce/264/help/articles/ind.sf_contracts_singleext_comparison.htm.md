---
article_id: ind.sf_contracts_singleext_comparison.htm
title: Single Document Extraction Methods and Licensing Requirements for Contracts AI
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_singleext_comparison.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_singleext_overview.htm
fetched_at: 2026-10-13
---

# Single Document Extraction Methods and Licensing Requirements for Contracts AI

Contracts AI offers three extraction methods, each with different performance characteristics, file requirements, and licensing needs. Compare the methods to determine which ones to configure for your org.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
Extraction Methods
EXTRACTION METHOD	DOCUMENT AI EXTRACTION	INDUSTRIES EINSTEIN EXTRACTION	MULTIMODAL EXTRACTION
Description	

For small to mid-sized documents. Uses Data Cloud Document AI to process structured contract data.

AWS Extract license isn’t required.

Supports multiple models, such as OpenAI and Gemini.

	

For complex or large documents without Data Cloud license. Uses Industries AI APIs to process documents.

Requires an AWS Textract license.

	

For small to mid-sized documents. Processes documents through a platform gateway call to a large language model.

A Data Cloud or Industries Einstein license isn’t required.

Supports multiple models, such as OpenAI and Gemini.


Availability	Available when Data Cloud is enabled.	Available when Industries Einstein is enabled.	Available without Data Cloud or Industries Einstein.
Processing role	Preferred method	Secondary method	Fallback method
Processing approach	Uses prompt instructions defined for fields and clauses.	Uses Industries AI APIs for extraction.	Uses API-based inputs to Large Language Models (LLMs).
Maximum file size	10 MB	Supports files exceeding 20 MB	As per the supported LLM model
Maximum pages	25	Varies	As per the supported LLM model.
Fallback behavior when one extraction model fails	Falls back to multimodal or Industries Einstein depending on the scenario and document size.	Used when Document AI can’t process the document.	Is the final fallback method when Document AI fails and Industries Einstein is unable to start the extraction.
Licensing Requirements for Contracts AI

Contracts AI features depend on enabled licenses and consumption-based entitlements.

COMPONENT	TYPE	DESCRIPTION
Einstein Foundations	License	Base requirement for AI capabilities in Contracts AI. Enables AI-powered extraction, multimodal processing, model-based extraction, and access to features such as Prompt Builder.
Salesforce Contracts	License	Required to use Salesforce Contracts features.
Contracts AI	License	Required to use all Contracts AI features, including contract extraction, clause generation, and related workflows.
Entitlement Credits (Flex Usage)	Entitlement	Consumption-based model governed by a Flex SKU. Provides credits used for extraction and clause generation. Credits are shared across AI features, such as Agent for Sales and Agent for Service.
Data Cloud	License	Enables Data Cloud capabilities, including Document AI. Required to use Document AI and advanced AI-driven extraction features.
Context Service (RCA License)	License	Defines the data structure (context definitions) used for extraction. Enables schema creation and supports prompt-based extraction at the field level.
AWS Textract	License	Required only for Industries Einstein extraction. Supports large file processing and legacy extraction workflows. Not required for Document AI or multimodal extraction.
Industries Einstein	License (conditional)	Enables extraction for large or complex documents by using industry-specific processing. Requires AWS Textract for execution.
