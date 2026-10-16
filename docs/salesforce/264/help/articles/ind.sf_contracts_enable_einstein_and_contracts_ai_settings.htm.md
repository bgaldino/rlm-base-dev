---
article_id: ind.sf_contracts_enable_einstein_and_contracts_ai_settings.htm
title: Turn On Industries Einstein AI Single Document Extraction
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_enable_einstein_and_contracts_ai_settings.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_singleext_overview.htm
fetched_at: 2026-10-13
---

# Turn On Industries Einstein AI Single Document Extraction

You must define the settings and enable standard action flows to enable users to draft clauses and extract contract details using Industries AI extraction method.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To enable Einstein and Contracts AI settings	

CLM Admin User

AND

Contracts AI User

AND

Prompt Template Manager

AND

NLP Service

AND

Scoring Framework Admin

Before you begin: Confirm AWS Textract policies are attached to the AWS identity you use with that named credential.

Enable Einstein Generative AI.
From Setup, in the Quick Find box, enter Einstein Setup, and then select Einstein Setup.
IMPORTANT If you can’t find Einstein Setup, ensure that your org meets the prerequisites for any generative AI features you plan to use. For more support, contact your Salesforce Account Executive (AE).
Turn on Einstein.
Enable Industries Cloud Einstein.
From Setup, in the Quick Find box, enter Industries Cloud Einstein, and then select Industries AI Setup.
IMPORTANT If you can’t find Industries AI Setup, ensure that your org meets the prerequisites for any generative AI features you plan to use. For help, contact your Salesforce account executive (AE).
Turn on the Industries AI setup setting.
Enable Document Extraction in Contracts AI.
From Setup, in the Quick Find box, enter Contracts AI, and then select Contract Extraction.
Turn on Contract Document Extraction.
Update general settings for Salesforce files.
From Setup, in the Quick Find box, enter Salesforce Files, and then select General Settings.
Click Edit, and then select Display alternative file previews.
Save your changes.
To enable users to process contract extraction, update the profile settings.
From Setup, in the Quick Find box, enter Profiles, and then select Profiles.
Click Edit next to the profile responsible for initiating contract extraction.
In the General User Permissions section, select Run Flows.
In the Standard Object Permissions section, define full access for Ocr Document Scan Results , and User External Credentials.
In the Tab Settings section, select Default On for Ocr Document Scan Results, Contract Extraction Results, AI Natural Language Process Results, and AI Natural Language Process Chunk Results.
Save your changes.
Define Share Settings for all your internal users to view the contract extraction results.
From Setup, in the Quick Find box, enter sharing, and click Sharing Settings.
In the Contract Extraction Result Sharing Rules section, click New.
Define your sharing rules.
For example, Shared With: All Internal Users, and Access Level: Read/Write.
Save your changes.
Assign the required permission sets to your users.
To design clauses and extract contract and clause details from the PDF, assign these permission sets: Contracts AI Clause Designer, Contracts AI User, Prompt Template User, NLP Service, and Scoring Framework Admin.
To extract contract and clause details from the PDF, assign these permission sets: Contracts AI User, Prompt Template User, NLP Service, and Scoring Framework Admin.
Configure a Named Credential and External Credential for Industries Einstein AI Extraction.
To enable a standard action flow that extracts clauses from your contract, create a Use Case Configuration for Clause Extraction.
From Setup, in the Quick Find box, enter Industries AI Setup, and then select New Use Case Configuration.
Select Document Clause Extraction as the configuration type, depending on the type of extraction that you require.
Enter a unique configuration label.
Enter a description.
Click Save and Continue.
To link your AWS account, click Set Up, and then accept the terms and conditions.
Select the named credential that you created, or click the link to create a named credential.
To activate the use case configuration, click Activate, and then confirm the action on the confirmation window.
Similarly, you can create multiple use case configurations for clause and entity extraction. Ensure that you set up at least one use case configuration each.
To enable a standard action flow that extracts entities from your contract, create a use case configuration for Entity Extraction.
From Setup, in the Quick Find box, enter Industries AI Setup, and then select New Use Case Configuration.
Select Entity Extraction as the configuration type, depending on the type of extraction that you require.
Enter a unique configuration label.
Enter a description.
Click Save and Continue.
To link your AWS account, click Set Up, and then accept the terms and conditions.
Select the named credential that you created, or click the link to create a named credential.
To activate the use case configuration, click Activate, and then confirm the action on the confirmation window.
Similarly, you can create multiple use case configurations for clause and entity extraction. Ensure that you set up at least one use case configuration each.

After enabling Einstein and Contracts AI, configure a named credential.

Configure a Named Credential and External Credential for Industries Einstein AI Extraction
A named credential stores your AWS account information. You can create a named credential in Setup. To extract contract details using Contracts AI, you must first extract values such as access keys, account ID, ARN, and IAM role from your AWS account. Use these AWS values to create an external credential and named credential. Additionally, create and assign a permission set to users.
