---
article_id: ind.sf_contracts_workflow_to_setup_esignature_for_standard_and_custom_objects.htm
title: Workflow to Setup E-Signature for Standard and Custom Objects
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_to_setup_esignature_for_standard_and_custom_objects.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_configure_e-signature.htm
fetched_at: 2026-10-13
---

# Workflow to Setup E-Signature for Standard and Custom Objects

Send documents generated from a quote, order, opportunity, or other standard and custom objects for e-signature by using e-signature APIs. DocuSign integration and an active DocuSign account are required.

IMPORTANT In the Spring ‘23 release, you can only use e-signature APIs to send documents from standard and custom objects other than contract objects.

Salesforce Contracts uses DocuSign to support e-signatures. Using DocuSign, you can :

Define DocuSign tags on a contract template and contract documents.

Send a contract document for review and signatures.

Track the signed contract document and update the contract record status.

Accept the signed contract document online or by fax.

Automatically invalidate a contract document that is pending signatures if a new contract document supersedes it.

System admin must enable these configurations to use DocuSign for standard and custom objects:

Electronic Signature Envelope Configuration for Salesforce Contracts
Using the Electronic Signature Envelope Config the system admin can define the default reminders and expiry for the envelopes submitted for eSignature.
