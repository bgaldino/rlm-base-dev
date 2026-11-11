---
article_id: ind.sf_contracts_invocable_actions_for_salesforce_contracts.htm
title: Invocable Actions for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_invocable_actions_for_salesforce_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_na_1.htm
fetched_at: 2026-10-13
---

# Invocable Actions for Salesforce Contracts

With invocable actions, create your own Salesforce Flows, triggering various functions within Salesforce Contracts. You can create document versions, create and update contracts, perform various contract actions, and send contracts for e-signature.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
INVOCABLE ACTION	DESCRIPTION	INPUT	OUTPUT
Create Contract Document Version	Creates a contract document version based on specified information.	

Required fields

Contract ID: The ID of the contract that you want to create a document version for.

Optional fields

PDF Document ID: The ContentDocumentId of the contract document to be imported in the PDF format.

Template ID: The ID of the document template that you want to use to create the version of the contract document.

Word Document ID: The ContentDocumentId of the contract document to be imported in the DOCX format.

	

For the provided Contract ID, a contract document version is created.

Use the Template ID as the optional value generates a contract document from the specified document template.

The Import Contract method includes the use of the PDF Document ID or Word Document ID. In this scenario, the file to be imported must be available in the DocGenDocumentTemplateLibrary, and the user must have access to the files in the library.


Check Out Contract Document Version	Creates a version of a contract document.	

Required fields

Contract Document Version ID: The ID of the latest contract document version that you want to use to create the contract document version.

Optional fields

External Review: A Boolean value that indicates whether the contract document version checkout is for an external review.

External Review Type: The type of external review. Possible values are OnlineMicrosoft365 and OfflineMicrosoftWord. This parameter is required if External Review is set to true.

PDF Document ID: The ContentDocumentId of the contract document to be imported in the PDF format.

Template ID: The ID of the document template that you want to use to create the version of the contract document.

Word document ID: The ContentDocumentId of the contract document to be imported in the DOCX format.

	

A content document version is created in the inactive state. You can generate contract documents by using an active document template or the import method.

Note: On Check out, the existing contract document version is still active. Only on Check In, does the new version become active and the previous version become inactive.


Unlock Contract Document Version	The unlock action deletes the latest contract document version that isn’t checked in.	

Required fields

Contract Document Version ID: The ID of the latest contract document version that you want to unlock.

Optional fields: N/A

	The latest contract document version gets deleted.
Create or Update CLM Contracts	Updates contracts associated with the specified sObject record and creates a contract document version (if the latest version is active) and the contract documents.	

Required fields

Create Contract Document: A Boolean value that indicates whether to create a contract document in addition to updating the contract.

Source Record ID: The sObject ID that the contract is created from is used to update the fields on the contract.

Optional fields

Document Template Name: The name of the active document template to be used when you create the contract.

	The output is a collection of all the contract IDs, which were updated for the SourceObject ID.
Get Content Doc Details for Contract Doc Version	Retrieves content document details such as the contentDocumentLinkId, createdDate, and lastModifiedDate that are associated with a contract document version.	

Required fields

Contract Document Version ID: The ID of the contract document version record used to retrieve the content document details.

Optional fields: N/A

	Gets the generated content document details such as contentDocumentId, contractDocumentVersionId, fileExtension, isSharedExternally, and contentDocumentLinkId.
Get Contract Document Versions	Retrieves the contract document versions for a specified contract by using the contract ID or an associated contract document version ID.	

Required fields

Contract Id: The ID of the contract that you want to get the contract document versions for.

Optional fields

Contract Document Version Id: The ID of the contract document version associated with the contract that you want to get the contract document versions for.

	

Gets the contract document version details associated with a contract.

When only the contract ID is passed, the action retrieves all the contract document version details.

When the contract ID along with a contract document version ID is passed, it retrieves the specified contract document version details.


Send Contract for E-Signature	Sends a contract to specified recipients for e-signature.	

Required fields

Contract ID: The ID of the contract to be sent to the recipients for e-signature.

E-Signature Vendor Name: The name of the provider of the e-signature service.

Email Template Name: The developer name of the email template that you want to send to the recipients. For more information, see View and Edit Email Templates in Salesforce Classic.

Get Documents Apex Class Name: Specifies the Apex class that retrieves the document IDs to send for e-signature. See E-Signature APis.
Get Recipients Apex Class Name: Specifies the Apex class that retrieves the list of recipients for the e-signature request. See E-Signature APis.
	The ID of the contract that was sent to the recipients.
Create CLM Contract	Creates a contract for a specified record.	

Required fields

Source Record ID: The sObject ID of the record that you want to use to populate the fields on the contract.

Optional fields

Create Contract Document: A Boolean value that indicates whether to create a contract document in addition to the contract.

Contract Record Type: The API name of the contract record type.

Document Template Name: The name of the active document template that you want to use when you create the contract.

	The ID of the contract that was created.
Perform Contract Action	Performs actions on a contract based on its status.	

Required fields

Action Name: The API name of the action that you want to perform on the contract.

Contract ID: The ID of the contract that you want to perform the action on.

Optional fields

Action Data: A JSON expression that contains the additional data necessary to perform the action on the contract.

	The ID of the contract that the action was performed on.
Check-In Contract Document Version	Checks in a contract document version.	

Required fields

Contract Document Version Id: The ID of the contract document version that you want to check in.

Optional fields

Save When Action Completes: A Boolean value that indicates whether to save the changes when the action is completed instead of when the flow ends.

	The ID of the contract document version that was checked in.
Perform Contract Action	Revokes the contract’s e-signature request.	

Required fields

Action Name: The name of the contract action to perform. Use revokeESign to revoke the contract’s e-signature request.
Contract ID: The ID of the contract whose e-signature request you want to revoke.
Action Data: The JSON payload that contains additional data required to revoke the e-signature request. Pass the following JSON structure:
{ "requestBody": "{\"voidedReason\":\"Voided for amended document.\",\"senderEmail\":\"xyz@gmail.com\"}" }
	 
Run Salesforce Contracts Invocable Actions
Leverage invocable actions to enhance the functionality of your applications. These actions can trigger various functions within Salesforce Contracts to manage the contract lifecycle efficiently.
