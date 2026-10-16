---
article_id: ind.sf_contracts_new_and_changed_connectapis_spring24.htm
title: New and Changed Salesforce Contracts Connect APIs
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_new_and_changed_connectapis_spring24.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_spring_24_release_notes.htm
fetched_at: 2026-10-13
---

# New and Changed Salesforce Contracts Connect APIs

Integrate intranet sites, and third-party web applications with Salesforce using Salesforce Contracts Connect REST API. These resources are new or have changes.

Document Template (GET, PATCH, POST)

Retrieve a list of document templates in the document generation
Make a GET request to the new /connect/docgen/document-templates?offset=${offset}&limit=${limit}&searchString=&{searchString} resource.

New response body: Document Template List

Update document template in the document generation
Make a PATCH request to the new /connect/docgen/document-templates?documentTemplateId=${documentTemplateId}

New request body: Document Template Update Input

New response body: Document Template

Create or update document templates in the document generation
Make a POST request to the new /connect/docgen/document-templates?documentTemplateId=${documentTemplateId}&action=${action}

New request body: Document Template Request

New response body: Document Template

Content Document Details (PATCH)

Update the content document details associated with a contract document version
Make a PATCH request to the new /connect/clm/contract-document-version/${contractDocumentVersionId}/content-document?contentDocumentId= {contenDocumentId}&share=true/false

New response body: Generic Output

Contract Document Version for Customer Community User (GET)

Get the latest details of a contract document version based on a contract ID
Make a GET request to the new /connect/clm/cc/contract/${contractId}/contract-document-version

New response body: Contract Document Version CC Response

Checkout

Template Input
This request body has these new properties.

external​Review​Type

isExternal​Review​Import

See Also

Salesforce Contracts Developer Documentation
