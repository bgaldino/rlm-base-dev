---
article_id: ind.sf_contracts_contract_creation.htm
title: Create and Manage Contracts in Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_contract_creation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_documnet_actions_overview.htm
fetched_at: 2026-10-13
---

# Create and Manage Contracts in Salesforce Contracts

Create contracts from opportunities, orders, quotes, or any standard or custom object that has field mappings configured.

Two contract actions are available on source objects:

Create Contract
Creates a contract record from the source object. You can define a contract start date and contract term, which determine the contract end date.
Update Contracts
Updates an existing contract's line items or creates a new contract document version from the source object. Each document version indicates whether it was created from an opportunity, order, or quote.
Contract Field Mapping

Salesforce Contracts uses Context Service to map data between a source object and the contract object. When you create a contract, the application automatically populates contract fields based on these mappings.

For opportunities, orders, and quotes, predefined Context Service mappings are available. For other standard objects and custom objects, your admin must create a custom source field and configure the mappings manually. For more information, see Configure Context Service to Create and Update Contracts.

Manage Contract Versions

After you generate a contract document, you can manage document versions with the Check In and Check Out actions.

Check Out
Locks the active document version for editing. While checked out, only the current user can modify the document. You can generate a new version from another template, import a new document, or modify attachments.
Check In
Saves your changes as a new contract document version and releases the lock so other users can access the document.

To create or update a contract, follow these instructions:

Create a Contract from an Opportunity, Order, or Quote
Using the Create Contract action button, you can create a contract directly from any object. The data from the object is copied to the contract object based on the defined field mappings. The field mappings can include both parent-to-parent mappings and child-to-child mappings.
Update Contracts from Opportunity, Order, or Quote
Sync field changes from an opportunity, order, or quote to associated contracts by using the Update Contracts action. Only contracts in Draft status that were created with the Create Contract action are eligible for updates.
Generate Contract Document Versions
When you create a new contract or modify an existing contract, you can create a new document by selecting a document template or by importing a pre existing document or by creating a document in Microsoft 365.
Create New Contract Document Versions
When a contract document has already been generated, you can generate a new contract document, using the same template or a different template.
Check In a Contract Document
If you checked out a contract document, you can check it in.
View Contract Documents
You can preview the contract document for any version of the document.
Lock and Unlock a Contract Document Version
To lock and unlock a contract document version, it must be active.
Attachments in Salesforce Contracts
The Contract Attachments allow you to upload, delete, search, and download the files from the list of attachments.
Retry Contract Document Generation
Salesforce Contracts allows you to retry or cancel the contract document generation if the generation is incomplete due to any failure or time-out issues in generating the document.
