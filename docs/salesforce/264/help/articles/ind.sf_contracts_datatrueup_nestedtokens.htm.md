---
article_id: ind.sf_contracts_datatrueup_nestedtokens.htm
title: Nested and Related Record Tokens in Data True-Up
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_datatrueup_nestedtokens.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_datatrueup_overview.htm
fetched_at: 2026-10-13
---

# Nested and Related Record Tokens in Data True-Up

If you have nested object references and lookup fields, you can pull data from the contract record and related objects, such as accounts, opportunities, quotes, and custom lookup records. Context Service document templates support Data True-Up nested tokens.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions

Data True-Up supports token processing for fields on related objects up to one level deep. To include related record fields in a document template, reference the objects by using nested token syntax and include the DT_ prefix. Before you use a related object token, confirm that Data True-Up supports the referenced field types and validate the lookup or master-detail relationship.

Format for Nested and Related Object Tokens

When a contract record is linked to related objects, you can reference the relationship in a template token. Here are some sample token expressions that illustrate typical usage.

{{DT_AccountName}} fetches the Account name associated with the contract.
{{DT_OpportunityAmount}} fetches the Opportunity amount from the opportunity linked via the SourceOpportunity lookup field.
{{DT_QuoteExpiryDate}} fetches the expiry date from a Quote record linked via a SourceQuote lookup field.
{{DT_CustomObjName}} fetches the name of the custom object linked to Contract via the CustomObj__c lookup field.

When you use a related object token, use only single-level nested references. After generating a document or when related record data changes, run Data True-Up to fetch and synchronize related object values.

Considerations for Related Object Tokens
A token can reference a field on a record that’s directly related to the contract. It can’t reference a field on a record that’s related to that related record, such as Contract.Account.Owner.Email, even though it can reference Contract.Account.Name.
Use related record fields that have data types supported by Data True-Up. See Supported Data Type Fields for Data True-Up.
Make sure that the lookup or master-detail relationship exists and is set up correctly in Salesforce.
Run Data True-Up after document generation or related record updates to fetch and sync related record values into the document.
