---
article_id: ind.sf_contracts_clone_the_contractsextractioncontext_context_definition.htm
title: Clone the ContractsExtractionContext Context Definition for Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_clone_the_contractsextractioncontext_context_definition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configuration_of_fields_for_extraction_from_a_file.htm
fetched_at: 2026-10-13
---

# Clone the ContractsExtractionContext Context Definition for Extraction

Create a custom context definition by choosing nodes, defining their relationship, and adding attributes. These custom definitions are available under the Custom Definitions tab. You can create custom definitions by using new, extend, and clone actions. For extraction, Salesforce recommends using the clone feature to clone the default ContractsExtractionContext context definition.

If you’ve user-defined fields in the custom context definition, ensure the contract record has corresponding fields for mapping. If you get an error, see this knowledge article.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To clone a default context definition:	Context Service Admin
From Setup, in the Quick Find box, enter Context Service, and then select Context Definitions.
Click the down arrow next to the ContractsExtractionContext context definition, and then select Clone.
Enter a name for your custom definition, and then save your changes.
The seven predefined fields under attributes fields get cloned.
To edit the custom context definition you created:
Go to the Custom Definitions tab.
Click Edit next to the cloned context definition mapping.
Modify the context definition details, if required, and then click Next.
Click Next.
To add contract details that you want to extract from the document.
Click Add Attributes.
Specify the attribute details such as Attribute Name, Type, and Data Type.
Click Next.
Save your changes.
To map the newly added user-defined fields to the contract fields for data extraction.
This mapping is essential for persisting data by transferring extracted data from the cache to contract fields, enabling the creation of Contract records.
Click the custom context definition.
Click Map Data.
Select Edit next to the persistence mapping.
Click Map.
You’re directed to Context Mapping’s builder page to begin mapping your nodes and attributes. You can map the contract fields to the document’s predefined and user-defined fields.
Map the fields on the contract object with the ContractCache fields. See Add Context Mapping.
Save your changes.
To activate your context definition, click the down arrow and select Activate.
To create an extraction template.
From Setup, in the Quick Find box, enter Contract Lifecycle Management, and then select Contracts AI.
Click Create Extraction Template.
Complete these fields: Template Name, Target Object: Contract, and Record Type.
Click Next.
In the Attribute Definition field, select the custom context definition that you created.
In the Context Mapping field, select the corresponding custom persistence mapping that you created for the context definition in the previous step.
To add prompt descriptions for the newly added user-defined fields, click the Additional Field Mapping tab. See Add Description for User-Defined Fields.
To modify the persistence mapping, click Edit Context Mapping. Then use the dropdown edit action to modify the persistence mappings.
Save your changes.

See Also

Extract Contract Details and Clauses with Contracts AI
