---
article_id: ind.sf_contracts_limitations_for_microsoft_365.htm
title: Limitations with Microsoft 365 Editor
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_limitations_for_microsoft_365.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_authoring.htm
fetched_at: 2026-10-13
---

# Limitations with Microsoft 365 Editor

Before you use Microsoft 365 editor, make sure you review the limitations

The character limit for the Content field in the Document Authored Content object is 320,000. This field contains text marked as a clause. Exceeding this limit fails the Check In and Save functionalities for Microsoft 365 documents.
The maximum payload size supported for a Microsoft 365 document is 4,194,304 characters for the Check In and Save functionalities. It includes marked clauses content, content control identifies for sections, standalone, and marked clauses. Exceeding this limit fails the Check In and Save functionalities for Microsoft 365 documents. To incorporate additional content into the document template, manually include the content instead of marking any text as a clause.
The cumulative record limit for marked clauses and sections within the Document Authored Content object is 200.
The Microsoft 365 add-in may fail to create a contract document if the account name contains special characters. See OneDrive reserved characters.
Salesforce Sans font isn’t supported in Microsoft 365. When you insert a clause into the document, the font is automatically converted to Calibri.
The Microsoft 365 Add-in may fail to check in a contract document if the associated account name is too long. To resolve this, you can either:
Shorten the Account Name
In Contract Type Config, change the Check In Document File Type from Word, PDF to Word.
In Document File Name Format, remove Contract.Account.Name. This prevents the account name length from affecting check-in and allows PDF generation to continue working.
