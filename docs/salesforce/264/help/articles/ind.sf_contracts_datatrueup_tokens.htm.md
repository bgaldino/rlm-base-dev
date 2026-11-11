---
article_id: ind.sf_contracts_datatrueup_tokens.htm
title: Data True-Up Tokens in Document Templates
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_tokens.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# Data True-Up Tokens in Document Templates

Use Data True-Up tokens in DOCX templates to enable two-way syncing between document content and Salesforce record field values.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
Data True-Up Token Overview
DATA TRUE-UP TOKEN	DESCRIPTION
Definition	A special merge token used to compare and sync field values between a document and its Salesforce record.
Token Format	

The DT_ prefix is required to enable Data True-Up functionality. For example: {{DT_FieldName}}.

Only the DT_ prefix is required. The token mapping from a Data Mapper or Context Service must follow this structure:


         {
         "DT_<tokenkey>": {
         "objectId": "<ID of the object for which the field value is computed>",
         "objectName": "<Name of the reference object>",
         "fieldName": "<Name of the field from which the value is retrieved>",
         "fieldValue": "<Actual value of ObjectName.FieldName>"
         }
         }
        

For example:


         {
         "DT_start": {
         "objectId":"800X4000001ohuvIAA",
         "objectName": "Contract",
         "fieldName": "StartDate",
         "fieldValue": "2022-08-20"
         }
         }
        

Purpose	Enables push and pull of field values through the Microsoft 365 Word add-in during document editing.
Supported Template Types	Microsoft 365 Word
Supported Objects	Standard and custom objects. Only parent-level fields are supported for syncing.
Not Supported	Child object fields, PPTX templates, PDF files
Tool Required	Microsoft 365 Word add-in
Hover Label in Word	When you click tokens with DT_ prefix, they appear with a content boundary labeled Data True-up field. This helps you distinguish them from other token types, such as variable tokens.
Additional Notes	If you delete an entire line that contains a DT token value in a downloaded document, the associated content boundary can also be removed.
