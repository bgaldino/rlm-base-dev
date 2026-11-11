---
article_id: ind.sf_contracts_create_a_contract_extraction_template_for_extraction.htm
title: Create a Contract Extraction Template for Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_a_contract_extraction_template_for_extraction.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configuration_of_fields_for_extraction_from_a_file.htm
fetched_at: 2026-10-13
---

# Create a Contract Extraction Template for Extraction

Create an extraction template to define the attribute mapping, context mapping, and prompt instructions that generative AI uses to extract contract details from a file. Each template must have a unique name and combination of contract object and record type.

If you have user-defined fields in the custom context definition, ensure the contract record has corresponding fields for mapping.

You can use the cloned ContractsExtractionContext context definition as is or customize the cloned context definition to fit your needs. For this illustration, the assumption is that no active context definitions are available. If you get an error, see this knowledge article.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To create an extraction template:	Context Service Admin
To create an extraction template, from Setup, in the Quick Find box, enter Contract Lifecycle Management, and then select Contracts AI.
Click Create Extraction Template.
Complete these fields.
Template Name: A name for the extraction template.
Target Object: Select Contract.
Record Type: The record type associated with the Contract object. For example, Contract Lifecycle Management.
Click Next.
To define the user-defined fields that you want to extract from the file and map those fields to the contract fields, create an attribute definition.
Click Create Attribute Definition.
The standard custom definition ContractsExtractionContext is cloned.
Click OK on the message.
The cloned context definition opens. The Attribute Definition and Context Mapping are populated with the cloned definition and mapping. In the Extraction Template Details window, the Document (Attribute) Fields tab lists the seven predefined context definition mapping field details, while the Additional Field Mapping tab is empty.
To view the seven predefined fields for extraction, click the down arrow next to the DocExtrctPersistenceMapping and select Input Mapping.
Click Cancel to close the window.
To add user-defined fields to the persistence mapping.
Click Edit.
Click Next twice.
Click Add Attributes.
Specify the attribute details such as Attribute Name, Type, and Data Type.
Click Next.
Save your changes.
To map the newly added user-defined fields to the contract fields for data extraction, complete these actions.
Click Map Data.
Select Edit next to the persistence mapping.
Click Map.
You’re directed to Context Mapping’s builder page to begin mapping your nodes and attributes. You can map the contract fields to the document’s predefined and user-defined fields.
Map the fields on the Contract object with the ContractCache fields. See Add Context Mapping.
Save your changes.
After you define your context definition, its structure, and its mapping, activate your context definition.
To add prompt descriptions for the newly added fields, go back to the extraction template details page. See .
In the context mapping section, select the persistence mapping that you want to use.
To modify the persistence mapping.
Click Edit Context Mapping.
Use the dropdown edit action to modify the persistence mappings.
Save your changes on the extract template details page.

See Also

Add Description for User-Defined Fields

Extract Contract Details and Clauses with Contracts AI
