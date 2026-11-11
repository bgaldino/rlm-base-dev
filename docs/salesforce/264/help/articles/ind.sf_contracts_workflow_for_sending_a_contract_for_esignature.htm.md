---
article_id: ind.sf_contracts_workflow_for_sending_a_contract_for_esignature.htm
title: Workflow for Signing a Contract Via E-Signature
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_for_sending_a_contract_for_esignature.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_e-signature_overview.htm
fetched_at: 2026-10-13
---

# Workflow for Signing a Contract Via E-Signature

Salesforce Contracts renders Send Envelope flow when submitted for e-signature.

When the contract is submitted for e-signature, it creates an envelope in DocuSign and returns the envelope id to Salesforce Contracts. Docusign sends a notification email to the recipient where they can access the document, and review or sign it. The contract state changes from ‘Negotiating’ to ‘Awaiting Signature’.

Review the DocuSign email.

Open the email to review the document and agree to the signature disclosure to start the signing process.

Start the signing process.

Once you are ready to sign the document after review, select the SIGN tag to verify and save your signature information. For details, see Insert DocuSign Signature tags.

Confirm signing.

You receive a notification stating your signature process is completed. The sender receives an email with the signed document.

For details, see DocuSign e-signature: How to sign a document.
