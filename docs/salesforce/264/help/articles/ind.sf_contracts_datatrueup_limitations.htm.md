---
article_id: ind.sf_contracts_datatrueup_limitations.htm
title: Limitations for Data True-Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_limitations.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# Limitations for Data True-Up

Review the limitations for Data True-Up token naming, template formats, supported features, and editing capabilities before configuring your templates. These restrictions affect token behavior, record updates, and template compatibility.

General DT Token Rules and Limitations
Data True-Up doesn’t support:
Special characters in DT token names.
Data transformations for DT tokens.
RTB, HYP, and IMG DT tokens.
DT tokens within clauses, including the Marked clause. You can create DT tokens inside sections.
DT tokens placed inside headers or footers.
DT tokens placed inside section or clause headings and titles.
Data True-Up supports:
Repeating line item tokens when the section and its field tokens use the DT_ prefix.
Nested DT tokens for related object fields up to one level deep when you use the DT_ prefix.
A maximum of 1,000 DT tokens, and 2,000 DT line-item tokens within in a document.
DT Token Behavior and Document Impact:
Requires you to define DT tokens at the top-level in the tokenMap.
Recognizes only DT tokens that include the DT_ prefix.
Deleting a line containing a DT token value in a downloaded document may remove the associated content boundary.
Use unique token names for variable DT tokens and line item DT tokens. This makes sure that Data True-Up can correctly distinguish and reconcile each token type.
The Data True-Up panel is disabled after you check in the document from the Microsoft 365 add-in.
Line Item Token Requirements
Use the DT_ prefix on both the main node and field token names in line-item sections for Data True-Up to process line items.
Don’t place line items inside sections; use dedicated repeating line-item areas in the template.
Maintain consistent DT_ prefixed token naming for line items that are mapped to multiple tables in the document.
Calculates sync status for line items collectively across all related line items.
Nested and Related Object Tokens
DT nested tokens support only one level of a related object. Deeper nested references aren’t supported.
Data True-Up reconciles nested object fields only for one-to-one mappings; for one-to-many relationships use line items.
Template Compatibility
Document template work only with document generation 2.0 and requires the Advanced Doc Generation API version type.
Merging Data True-Up token data during document generation works only with Salesforce Contracts.
Supports only DOCX templates. PPTX and PDF files aren’t compatible.
Doesn’t support DT tokens in a document template’s table of contents.
Avoid importing documents that contain DT fields from another org or a different contract object. DT tokens reference the contract object that they were generated from or the object specified in the ObjectId field of the Omnistudio Data Mapper or Context Service.
Data Source Compatibility
Custom date formats aren’t supported when the data is sourced through Data Mappers and transformed with formats. Only the default date format is supported.
Data True-Up uses database values for fetching values without intermediate formatting. Document formatting doesn’t affect reconciliation values.
For numeric fields, such as number, percentage, and currency, values with more decimal places than defined for the field show a validation warning but can be saved in the document without rounding off.
Editing and Formatting
DT token values in the generated document are locked and can be edited only through the Edit Value option in the Microsoft 365 Word add-in.
Date-type DT tokens support display format changes (for example, YYYY/MM/DD or MM/DD/YYYY). The default format is YYYY-MM-DD.
Reviewers must accept or reject existing document changes before updating DT token values through the Edit Value option.
Access Requirements
The Update Records feature isn’t supported for auto number fields.
Field-level security read and edit access is required for any field referenced by DT token for reconciliation and record update.
Partner Community users can open documents in Microsoft 365 add-in only in Firefox and Safari when the browser privacy setting ‘Browser Privacy’ is custom configured under ‘Privacy and Security’. Without this configuration, add-in access isn’t supported. Users must also have field-level security (FLS) access to use Data True-Up from Microsoft 365. Without the required access, check-in and update actions aren’t supported.
Guidelines (Not Limitations)
You can't edit locked fields from the Edit Value window. Use the copy option in the window to sync the record value into the document value.
Perform Fetch Values before initiating Update Fields to make sure that all token statuses reflect the latest Salesforce data.
If a DT token references a field that is not editable, perform a refetch value for that field before you initiate an update record.
You can delete individual DT tokens from the Data True-Up panel before reconciliation.
When Fetch Values or Update Fields encounters a validation error on a field for a record ID, Data True-Up doesn’t update any fields for that record ID.
DT token formatting is preserved in generated documents when these conditions are met:
Formatting must be applied to the entire token, from {{ to }}.
Formatting must be uniform across the entire token. You can't format part of the token one way and another part differently, for example, half bold and half italic.
Only the following formatting options are supported: Bold, Italics, Underline, Font (typeface), and Font Size. Additional formatting options can be added on demand.
You can edit DT token values through the Edit Value option in the Microsoft 365 Word add-in, even when tokens have formatting applied.
