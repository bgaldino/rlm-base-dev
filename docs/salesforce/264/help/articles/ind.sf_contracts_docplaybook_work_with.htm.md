---
article_id: ind.sf_contracts_docplaybook_work_with.htm
title: How Document Playbook Works
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_docplaybook_work_with.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_documnet_actions_overview.htm
fetched_at: 2026-10-13
---

# How Document Playbook Works

A document playbook captures the guidelines, acceptable clause language, and fallback positions that legal and contract teams follow during contract negotiations. When a contract author runs a risk analysis on a contract in the Microsoft 365 Word add-in, Salesforce compares the contract against the active playbook and highlights deviations, escalation paths, and nonstandard language. Use document playbooks to manage versioned negotiation guidelines that Contract Risk Analysis uses to evaluate contract changes against your organization's standards.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance editions.

Document Playbook separates playbook management from playbook use. Document Playbook Designers create, version, activate, and assign playbooks. Document Playbook Users have read-only access to relevant guidance during Contract Risk Analysis.

Document Playbook Records

Document Playbook uses these record types to organize data.

RECORD TYPE	PURPOSE
Document Playbook	The top-level record that groups related versions and assignments. A playbook moves through Draft, Active, and Archived statuses. The parent playbook's status is derived from its versions. Activating any version moves the parent playbook to Active.
Document Playbook Version	The actual playbook content. Each version stores an uploaded file (PDF, DOCX, or XLSX) and moves through Draft, Active, and Archived statuses. A playbook can have many versions, but only one Active version and one Draft version at a time. Activating a new version automatically archives the previously active one.
Document Playbook Assignment	Links a playbook to a target object and record type so that risk analysis can retrieve the appropriate playbook when the author runs the analysis. The target object is a contract. An assignment belongs to the parent playbook, not to an individual version. You can create an assignment only when the parent playbook is Active, and you can assign a target object and record type combination to only one playbook at a time.
Data 360 Search

When a designer activates a version, the Document Playbook Data Kit's data streams ingest the version's file into Data 360 (Data Cloud), chunk it into semantically meaningful segments, and store those segments in a hybrid search index. The Document Playbook index supports both keyword and vector search so risk analysis can find the segments most relevant to each section of an incoming contract.

During Contract Risk Analysis, Salesforce uses playbook guidance in this order.

Identify the Contract record type of the contract being analyzed.
Find the Document Playbook Assignment that matches that record type.
Find the active Document Playbook Version linked to the assigned playbook.
Run a hybrid search on the version's indexed content in Data 360 to retrieve the segments most relevant to each contract section.
Supply those segments to the risk analysis flow so the reviewer sees deviations, escalation paths, and nonstandard language.

The search query filters to the active version of the assigned playbook, so retired and draft content is never surfaced during risk analysis.

Document Playbook Access, Files, and Limits

Document playbook records are private by default. Only the record owner can see a playbook until a sharing rule grants access to other users. Create sharing rules on the Document Playbook object and, if child records must be shared beyond the owner, on Document Playbook Version and Document Playbook Assignment. See Create a Document Playbook Sharing Rule.

LIMIT	VALUE
Upload formats	PDF, DOCX, and XLSX
Maximum file size	100 MB
Data-kit chunking formats	PDF, DOCX, and XLSX
Language support	English only
Playbook and Version Statuses and Actions

Each record type has a lifecycle. Playbook and version statuses determine which actions are available and when content can be used during risk analysis. To update playbook content, create a new version. You can't modify the description of an Active version, and you can't modify an Archived version.

RECORD	STATUS	MEANING	AVAILABLE ACTIONS	HOW THE ACTIONS WORK
Document Playbook	Draft	Newly created playbook. No version has been activated yet. Not available for risk analysis.	View, Edit, New Version, Delete	Add and edit versions. Deleting removes the playbook and its versions. The playbook moves to Active automatically when any version is activated.
Document Playbook	Active	At least one version is active. Guidance is available for risk analysis.	View, Edit, New Version, Assignment, Archive	Add new draft versions or replace the active version. Create or update the assignment for a target object and record type. Archive to retire the playbook.
Document Playbook	Archived	Retired playbook. Kept for reference. Not returned during risk analysis.	Delete	Archiving a playbook archives all of its Active and Archived versions along with it. The Draft version remains in Draft. Deleting an archived playbook removes it and all its versions, along with their indexed chunks from Data 360, so risk analysis no longer returns content from the deleted playbook.
Document Playbook Version	Draft	Newly created or edited version. Not yet available for risk analysis.	Edit, Replace Document, Activate, Delete	Edit metadata or replace the attached document. Activate to move this version and the parent playbook to Active. Activating this version archives the previously active version of the same playbook.
Document Playbook Version	Active	Currently in force. Available for risk analysis. Only one version per playbook can be Active at a time.	Archive	Archive to retire this version. To replace it, activate a new draft Salesforce archives the current active version automatically.
Document Playbook Version	Archived	Retired version. Kept for reference and audit. Not returned during risk analysis.	Delete	Deleting a version removes its chunks from Data 360, so risk analysis no longer shows content from the deleted version.
Create a Document Playbook and Activate a Version
To iterate on a playbook document before making it live, create the playbook shell first, then add and activate a version, and assign the playbook to a Contract record type. Each action is a separate step, so you can pause between them to review or update the document.
Create a Document Playbook by Uploading a File
Create a playbook, activate its first version, and assign the playbook to a Contract record type in a single action. Use this task when your playbook document is final and you don't need to iterate on drafts before making the playbook active.
