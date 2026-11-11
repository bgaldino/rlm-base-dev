---
article_id: ind.sf_contracts_auto_generate_document_on_contract_update.htm
title: Auto Generate Document On Contract Update
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_auto_generate_document_on_contract_update.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_type_config_settings.htm
fetched_at: 2026-10-13
---

# Auto Generate Document On Contract Update

To automatically generate a new contract document version and add it to the object when using the Contract Update action button, you must configure the contract type config settings. You need to set up a few contract type configurations for updating contracts to be successful. The configurations include the default template name, document file name format, and auto-generate doc file type.

Go to Setup.
In the Quick Find box, search for Contract Type Config.
Click Contract Type Config.
Make these changes to your specific Contract Type:
Set Yes in the Auto Generate Document On Contract Update setting.
Set the file type in the Auto Generate Doc File Type setting.
Set the file format in the Document File Name Format setting.
Enter the template that you want to use for document generation in the Default Template Name setting.
The template must be available in the org and active. For more information, see Contract Type Config Settings .
