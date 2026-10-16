---
article_id: release-notes.rn_contracts_new_connect_rest_apis.htm
title: New Connect REST APIs in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_contracts_new_connect_rest_apis.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_salesforce_contracts.htm
fetched_at: 2026-09-30
---

# New Connect REST APIs in Salesforce Contracts

Bring AI-assisted risk review and playbook standards into your contract workflows. Start an asynchronous risk analysis for a contract document version and a poll for its findings. Also, create a playbook version from a content document, and retrieve the playbook content chunks that best match a passage of contract text.

New Connect REST API Resources
Start a risk analysis for a contract document version
Make a POST request to the new /connect/contracts-ai/contract-document-version/contractDocumentVersionId/risk-analysis resource.
New request body: Contract Risk Analysis Input
New response body: Contract Risk Analysis Run
Get the status and findings of a risk analysis run for a contract document version
Make a GET request to the new /connect/contracts-ai/contract-document-version/contractDocumentVersionId/risk-analysis resource.
New response body: Contract Risk Analysis Run
Get the playbook content chunks that match a query string
Make a GET request to the new /connect/playbook/playbook-contents resource.
New response body: Playbook Content
Create a playbook version from a content document
Make a POST request to the new /connect/playbook/playbook-version resource.
New request body: Playbook Version Input
New response body: Playbook Version Details
SEE ALSO
Salesforce Contracts: Salesforce Contracts Resources
