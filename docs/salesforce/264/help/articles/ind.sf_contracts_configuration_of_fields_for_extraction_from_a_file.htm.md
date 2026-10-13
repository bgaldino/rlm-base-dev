---
article_id: ind.sf_contracts_configuration_of_fields_for_extraction_from_a_file.htm
title: Configuration of Fields for Extraction From a File
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_configuration_of_fields_for_extraction_from_a_file.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_fields_for_extraction_with_contracts_ai.htm
fetched_at: 2026-10-13
---

# Configuration of Fields for Extraction From a File

Custom contract extraction lets you extract specific values from a file for both predefined and user-defined fields. For example, extract a payment method from a document and map it to a custom contract field. Use adaptable extraction templates with tailored prompt instructions for different use cases.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions

As a contract admin, you have two options to create context definitions for extraction.

Option 1: Create a contract extraction template. The default ContractsExtractionContext context definition is cloned when you click Create Attribute Definition, and you can further customize your persistence mapping. See Create a Contract Extraction Template for Extraction.

Option 2: Clone the default ContractsExtractionContext context definition. Modify the persistence mapping accordingly, and then select the newly created context mapping while creating your contract extraction template. See Clone the ContractsExtractionContext Context Definition for Extraction.

Create a Contract Extraction Template for Extraction
Create an extraction template to define the attribute mapping, context mapping, and prompt instructions that generative AI uses to extract contract details from a file. Each template must have a unique name and combination of contract object and record type.
Clone the ContractsExtractionContext Context Definition for Extraction
Create a custom context definition by choosing nodes, defining their relationship, and adding attributes. These custom definitions are available under the Custom Definitions tab. You can create custom definitions by using new, extend, and clone actions. For extraction, Salesforce recommends using the clone feature to clone the default ContractsExtractionContext context definition.
Add Description for User-Defined Fields
Add descriptions for user-defined extraction fields. Each description acts as a prompt for generative AI, so precise and clear descriptions improve extraction accuracy.
Manage and Test Contract Extraction Instructions
Set up and refine extraction instructions for standard and custom fields. Upload PDF files to test extraction results in the Preview tab, adjust field-level instructions to improve LLM accuracy, and save the validated instructions to extraction templates for runtime use.
