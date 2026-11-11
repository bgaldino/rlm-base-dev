---
article_id: ind.sf_contracts_workflow_for_submitting_a_contract_for_e-signature.htm
title: Workflow for Submitting a Contract for E-Signature
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_for_submitting_a_contract_for_e-signature.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_e-signature_overview.htm
fetched_at: 2026-10-13
---

# Workflow for Submitting a Contract for E-Signature

Salesforce Contracts is integrated with DocuSign to provide e-signatures. DocuSign manages the contract document signature flow.

After DocuSign gathers the signatures, Salesforce Contracts syncs up with DocuSign servers and retrieves the signed contract document. Salesforce Contracts automatically attaches the signed contract document to the latest version of the contract.

When a contract document is sent for e-signatures, Salesforce Contracts notifies the recipients via email and can include a message. You can configure who the recipients are, where in the contract they sign, and the labels and other text used. Recipients are associated with Contacts.

A contract comes into effect when it's signed and executed. The Contract Status field indicates the current contract state, for example:

Negotiating

Awaiting Approval

Signed

Active

Expired

E-Signature Workflow:

Send the contract for signing when all involved parties agree upon the terms and conditions after the negotiations. For information on e-signature APIs, see E-signature Resources.

Submit a Contract for E-Signature
DocuSign manages the contract document signature flow. Use the Send for Signature button to initiate the e-signature process.
Add E-Signature Recipients
The recipients are associated with the contacts. You can add the signers also by using Add Recipient.
Insert DocuSign Signature Tags
You must insert the DocuSign signature tags directly into Microsoft Word (.docx) or Microsoft PowerPoint (.pptx) file.
