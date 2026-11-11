---
article_id: ind.sf_contracts_document_clause_library.htm
title: Document Clause Library
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_document_clause_library.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Document Clause Library

The Document Clause Library is a central repository of preapproved and prebuilt standardized template clauses that you can use to build contracts and other legal documents. Having all legal language in a single repository expedites document creation and enables the sales team to send out contracts without contacting the legal team for every deal.

You can create variations of clauses, categorize them by business unit or product, and manage draft, in approval, active, and archived versions. In document templates, you can reference a clause token which includes both merge and placeholder tokens that get resolved during document generation, either the latest active version or a specific version.

Document Clauses
A document clause defines the terms of the agreement between the parties, such as the goods or services to be delivered, payment terms, ownership rights, or applicable law. You can use a clause in a variety of documents, such as contracts, document templates, and disclosure responses. To facilitate creating clauses, the Clause Library provides predefined, reusable clauses.
Document Clause Sets
A document clause set groups and organizes related clauses based on their variations and versions. It enables the use of standardized language in documents, ensuring consistency and accuracy.
Configure Clause Category
When creating a clause set, to categorize your clauses, select the category for the clause set. In Setup, the system admin defines the clause categories for clauses.
Clause Approval Workflow
Set up a clause approval workflow to send your draft clause for approval to your internal stakeholders, such as managers, and the legal team. The Submit for Approval action triggers the approval workflow. Salesforce verifies the list of approvers and automatically initiates the approval request notification via email, based on configuration.
Create a Custom Report Type and Clause History Report
Create a custom report type with the Document Authored Content object to run reports on clause metadata. Add fields from contracts, clauses, and clause sets to customize the report layout, then build a report for detailed clause analysis.
