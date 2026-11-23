---
article_id: ind.sf_contracts_workflow_for_updating_an_envelope_status.htm
title: Workflow for Updating an Envelope Status
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_for_updating_an_envelope_status.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_e-signature_overview.htm
fetched_at: 2026-11-23
---

# Workflow for Updating an Envelope Status

Salesforce Contracts renders Update Envelope Status flow when submitted for e-signature.

When the contract is in Awaiting Signature state, you can either update the envelope status on demand or wait for the scheduled job to query docusign to verify whether the e-signature envelope was signed or declined by the signers.

To update the envelope status manually:

When you click Update Envelope Status, the Update Envelope Status Action is executed. Then, the Envelope Status modal opens and shows the envelope ID, subject, and status, along with the signing order, status, and last updated time for each recipient.

If envelope is signed, the contract state changes to Signed and the pdf version of the signed document is generated with the prefix ‘signed’.

If any of the signers decline to sign then the state will be changed to Signature Declined.

For more information on scheduling a docusign job, see Schedule a DocuSign Job to Poll for Document Signed Status.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_for_updating_an_envelope_status.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
