---
article_id: ind.sf_contracts_workflow_to_setup_esignature_for_contract_object.htm
title: Workflow to Setup E-Signature for Contract Object
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_to_setup_esignature_for_contract_object.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_e-signature.htm
fetched_at: 2026-10-13
---

# Workflow to Setup E-Signature for Contract Object

Integrate DocuSign with Salesforce Contracts for users to be able to email a copy of the document to sign at the recipient’s convenience. DocuSign integration requires an active DocuSign account.

NOTE To send documents generated from standard and custom objects other than a contract, you use a different process. For details, see Workflow to Setup E-Signature for Standard and Custom Objects.
NOTE To customize envelope settings such as reminders, expiration, and recipient options, you can optionally configure an Electronic Signature Envelope Config after completing the required setup.

To use DocuSign for e-signature, complete the following setup steps in order. DocuSign integration requires an active DocuSign account.

Permission Sets For DocuSign
The system admin must assign either the Contract Management (Salesforce Contracts) or DocGen permission set licenses to your user to send documents for e-signature. Non-Salesforce Contracts users must be assigned a DocGen license.
Create an Auth Provider for DocuSign
Add an Auth Provider credential for DocuSign in Salesforce to create a secure connection. Omnistudio uses these credentials to fetch document templates from DocuSign.
Create a Named Credential for DocuSign
Add a Named Credential using auth provider information to create a secure connection. Omniscripts and Integration Procedures use these credentials to connect with DocuSign.
Electronic Signature Configuration for Salesforce Contracts
Using the Electronic Signature Configuration setup, the system admin must define the required configurations to support the e-signature APIs and UI.
Default Contract Type Config Settings for E-Signature
Salesforce Contracts application provides a default set of signature settings for the contract such as defining the default reminders and expiry warnings for the envelopes submitted for e-signatures.
Set Up the Remote Site for Salesforce Contracts E-Signature
To configure DocuSign to work with the Salesforce Contracts application, you must connect Salesforce to a DocuSign account. You set up the DocuSign remote site as one of the websites your Salesforce org can invoke.
