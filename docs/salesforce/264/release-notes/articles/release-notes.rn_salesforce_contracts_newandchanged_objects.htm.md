---
article_id: release-notes.rn_salesforce_contracts_newandchanged_objects.htm
title: New and Changed Objects in Document Generation and Contracts
source_url: https://help.salesforce.com/s/articleView?id=release-notes.rn_salesforce_contracts_newandchanged_objects.htm&type=5&release=264
release: 264
release_name: Winter '27
area: revenue
parent_article: release-notes.rn_salesforce_contracts.htm
fetched_at: 2026-09-30
---

# New and Changed Objects in Document Generation and Contracts

Do more with these new and changed Document Generation and Contracts objects.

New Objects
Represent the AI-generated risk finding for a contract document risk element
Use the new CntrDocRiskElmntFinding object.
Represent the input for one AI-driven review of a contract document risk element
Use the new CntrDocRiskElmntRvwInpt object.
Represent a bounded text block from a contract document for risk analysis
Use the new CntrDocRiskElement object.
Represent one execution of contract risk analysis for a contract document version
Use the new CntrDocRiskRun object.
Represent the processing record for one contract document risk element in a document risk run
Use the new CntrDocRiskRunItm object.
Represent a set of guidelines used to standardize how a contract is authored, reviewed, and negotiated
Use the new DocumentPlaybook object.
Represent the assignment of a document playbook to a specific object and record type
Use the new DocumentPlaybookAssignment object.
Represent a read-only version of a document playbook
Use the new DocumentPlaybookVersion object.
Represent a token used in document clause content
Use the new DocumentClauseContentToken object.
Represent a clause associated with a quote
Use the new QuoteClause object.
Changed Objects
Insert a specific clause version during document generation
Use the new ClauseTmplVersionIdentifier field on the DocumentClause object. This identifier always inserts the same clause version, even if a newer active version is published later. The value is auto-populated when the clause is saved and is read-only.
Indicate whether the clause can be added to the relevant Salesforce object
Use the new IsEligibleForTerms field on the DocumentClause object.
Use the system-generated token identifier to insert the latest active version of the clause during document generation
Use the new LatestClauseTmplIdentifier field on the DocumentClause object. The value is auto-populated when the clause is saved and is read-only.
Indicate whether the document template contains tokens in the clause
Use the new HasClauseToken field on the DocumentTemplate object. The default value is false.
