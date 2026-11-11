---
article_id: ind.sf_contracts_glossary.htm
title: Salesforce Contracts Glossary
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_glossary.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_salesforce_contracts_overview.htm
fetched_at: 2026-10-13
---

# Salesforce Contracts Glossary

Browse through this collection of terms, key objects, and key concepts. This collection is designed to give Salesforce admins, sales reps, and developers a clear and consistent understanding of salesforce contract concepts and helps them navigate the Salesforce Contract landscape.

Auth Providers
Configuration that is used to integrate external authentication services for user login. For example, you can configure a Microsoft Auth Provider to let users to log in to Salesforce apps with their Microsoft Azure ID.
Batch Document Generation
Bundles multiple document generation requests into a batch process for streamlined execution.
Bulk Document Extraction
Automates the extraction of contract data from multiple documents in a single request by processing files stored in external repositories, such as Amazon S3 and Google Cloud Storage, and converting unstructured agreements into structured records.
Bypass Tokens
Preserves specific tokens in a document when no value is available by preventing them from being replaced with empty values during document generation.
Contract Approval
Leverages the Salesforce platform's approval process, allowing contracts to be approved or rejected by other customer stakeholders.
Contract AI Extraction
Extract contract documents (PDFs, images), review them by using the human in the loop method, and persist the contract object with extracted header and clause data.
Contract Authoring Using Microsoft 365
Supports editing of contract documents, including adding clauses, by using the Microsoft 365 add-in (plug-in).
Contract Comparison
Compares the contract's current version with previous versions to highlight differences introduced during redlining.
Contract Clauses
Defines the standard terms and conditions included in the contract document, which are legally binding between the signing parties.
Contract Clause AI Generation
Generate Clauses using Contracts AI in Clause Library and using Microsoft 365 add-in.
Contract Document Generation
Generates contract documents by merging field data with predefined document templates.
Contract Document Risk Analysis
An AI-powered runtime feature that helps contract authors identify potential risks introduced during internal or external review. It analyzes modified clauses against your grounding playbook, scores them by severity, and recommends mitigation content directly in the Microsoft 365 Word add-in.
Contract Document Section Lock
Locks specific sections of a document to make them read-only during the review process.
Contract External Review
The contract author invites external reviewers to collaborate through redlining and commenting. This review typically occurs during the negotiation stage.
Contract Extraction Template
Defines fields and prompts for extracting specific data from contracts.
Contract E-Signature
Provides electronic signing of contracts using built-in DocuSign API integration.
Contract Internal Review
The contract author invites internal reviewers (parties within the organization) to collaborate through redlining and commenting. After all reviews are completed, the document version can be checked in (saved).
Contract Object State Action
For each contract state, the Contract State Action Definition contains details of an action, including whether the action is of type Apex or Omniscript, and determines which action triggers a state transition.
Contract Object State Model
Defines the different contract states and state transitions for each contract type.
Contract Redlining
The process of marking changes in a document in a different color from the original text. It can also refer to the process of editing a contract during negotiations to create a single document that satisfies all parties.
Contract Search

Using AI and vector search capabilities, users could search different contract data and clause information by Q&A type of query

Contract State Transitions
Determines the valid transition between two states. For example, the Contract object can transition from Negotiating to Awaiting Signature.
Contract Type
Type of contract defined at the contract level and at the contract setup level.
Contract Type Config
Defines document-specific settings and esignature configurations for each contract type.
Clause Category
When creating a clause set, select a category for the clause set to categorize your clauses. Selecting a category is important if you need to define sharing rules for showing clauses at runtime.
Clause Library
A repository of preapproved clauses, typically managed by legal teams, for use in templates and contracts.
Clause Marking
Mark specific text in the contract document to identify it as a document clause by using Microsoft 365 add-in.
Clause Promotion
Move a document clause to the clause library via clause-level approvals.
Clause Template Version Identifier
The system-generated token identifier used in a document template to insert a specific clause version during document generation. This identifier always inserts the same clause version, even if a newer active version is published later. The value is auto-populated when the clause is saved and is read-only.
Clause Token
A token placed in a document template that references Clause Library content. At document-generation time, it resolves to either a specific clause version or the latest active version and inserts that clause's content. Clause tokens use the CL_ identifier format.
Client-Side Processing
Only managed packages support this mode. In DocGen 1.0, documents are generated using web browser resources. In DocGen 2.0, documents are generated using web browser and server-side resources.
Custom Fonts
Customer-proprietary fonts uploaded to Salesforce for rendering PDF documents. Salesforce doesn't ship custom fonts.
Data True Up
Data True-Up keeps contract documents and Salesforce records aligned. Using Microsoft 365 add-in, you can compare token values from both sources, identify differences, and update either the document or the record without losing redlines. This bi-directional sync maintains accuracy and compliance throughout the contract lifecycle.
Data True-Up Token
Tokens in the contract document template prefixed with "*DT_"* to compare and sync values between the document and the Contract record.
Document Generation Process (DGP)
The entity behind all server-side document generation activity. Customers and applications use DGP as the request entry point to initiate server-side document generation processing.
Document Template (DT)
Defines the structure, content, and format of generated documents. Using document templates, customers can generate Word documents, PDF files based on the use cases and needs.
Document Template Designer
Helps users create a document template with extraction and transformation configurations, document titles, and document generation formats.
Document Template Type
The supported types of document templates are Microsoft Word, Microsoft PowerPoint, and Microsoft 365. With the Microsoft 365 template type, the designer can edit the template by using the Microsoft 365 add-in (plug-in). For DocGen-only customers, only these document template types are supported: Word and PowerPoint. For Salesforce Contracts customers, all the template types are supported.
Document Template Usage Type
A classification or category field. It isn't user-defined. Salesforce ships a few default document templates and assigns a Usage Type value to them, such as the Tearsheets document template and the Invoice document template.
DocGen on Core
The DocGen capability (designer and runtime) is fully supported on the core, removing the need for any managed packages.
DocGen on Packages
The DocGen capability (designer, runtime, and license) is supported across the Omnistudio, Industries Communications, Media, Energy & Utilities (CME), Insurance (INS), and Vlocity Government (PS) packages.
Document Generation 2.0
Starting with Spring `25, customers can switch to Document Generation 2.0 (DocGen), which includes updates to client-side generation, the previewer, and custom font configuration. To use Document Generation 2.0, customers on Industries Communications, Media, Energy & Utilities (CME), Insurance (INS), Vlocity Government (PS), and Omnistudio packages must provide in-app consent to use it.
Document Playbook
A curated document of your organization's approved contract clauses and fallback language, uploaded as a DOCX, PDF, or XLSX file. The system indexes it into Data 360 using section-aware chunks with hybrid search, so features like Contract Document Risk Analysis can compare a contract's modified clauses against approved standards and flag deviations. Playbooks are private by default and need sharing rules configured to be visible to other users.
Edit Value
Allows you to manually change the document token value.
Extraction Model Fallback
Defines a behavior where the system automatically switches between extraction methods, such as Document AI, Multimodal, and Industries Einstein, based on availability, limits, or processing conditions.
External Document Storage Configuration
The Microsoft OneDrive location for storing document templates and contract files.
Fetch Failed
The system couldn’t retrieve the DT token’s field value from Salesforce. This may occur due to missing permissions, deleted fields, or temporary API failures.
Fetch Values
Retrieves values from Salesforce into the document tokens.
Generate Document LWC
A Lightning Web Component that generates and attaches documents to Salesforce records without requiring OmniStudio.
In Sync
The token value in the document matches the corresponding record field value in Salesforce.
Latest Clause Template Identifier
The system-generated token identifier used in a document template to insert the latest active version of a clause during document generation. This identifier automatically reflects newer active versions, so generated documents use updated clause content without changing the document template. The value is auto-populated when the clause is saved and is read-only.
Localization Enabled
A setting on the Document Generation Process that generates documents using the current user's locale, including translated text and locale-specific currency, date, and time formats.
Merge Token
A token that automatically resolves to Salesforce record data during document generation. Its value comes from configured mappings through Omnistudio Data Mappers or Context Service.
Microsoft 365 Add-In
The Salesforce Contracts Connector for Word Add-In is a supplemental program that adds custom commands and features to the document editing experience provided by Microsoft. Use the add-in to merge Salesforce data into the document and perform certain actions critical for document editing.
Named Credentials
A secure and declarative way to store and manage the credentials required for HTTP callouts in Salesforce, enabling integration with external systems via SOAP and REST APIs.
Obligation Management
The process of tracking, managing, and ensuring compliance with the commitments, responsibilities, and deliverables outlined in a contract.
Out of Sync
The token value in the document differs from the corresponding record field value in Salesforce.
Placeholder Token
A token that either uses a preset default value or enables a user to explicitly provide one at runtime. It supports String, Date, Currency, and Percentage values. In Quote Special Terms, users supply the value when adding or editing a clause.
Purpose
Supports push and pull of field values between documents and Salesforce records through the Microsoft 365 Word add-in.
Quote Special Terms (QST)
Clauses associated with a quote and selected from the Clause Library through the Quote Special Terms component. QST copies the clause content from the source Document Clause, so subsequent quote-level changes remain independent of the source clause. Quote Special Terms support placeholder tokens only during clause selection.
Redlining in Private Mode
Conduct the review process in private mode without exposing comments, redlines, or usernames to either party.
Refetch Value
Retrieves the latest value for a specific DT token from Salesforce.
Salesforce Contracts Org Preference
Allows admins to enable the Salesforce Contracts app in a Salesforce org.
Server-Side Processing
Document generation processing runs on near-core (Hyperforce) and syncs the generated files to the entities.
Single Document Extraction
Extracts contract fields and clauses from a single document by using AI-based extraction methods, such as Document AI, Multimodal, or Industries Einstein.
Single Point Request (SPR)
A single document generation request placed for server-side processing.
Supported Objects
Supports standard and custom objects. Syncing is limited to parent-level fields only.
Supported Template Types
Supports only Microsoft 365 Word (.docx) templates.
Token Format
Requires DT_ prefix. For example, {{DT_FieldName}}.
Update Record
A single document generation request placed for server-side processing.
