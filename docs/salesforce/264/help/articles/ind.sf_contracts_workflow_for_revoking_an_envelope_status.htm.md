---
article_id: ind.sf_contracts_workflow_for_revoking_an_envelope_status.htm
title: Workflow for Revoking an Envelope Status
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_workflow_for_revoking_an_envelope_status.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_e-signature_overview.htm
fetched_at: 2026-10-13
---

# Workflow for Revoking an Envelope Status

Salesforce Contracts renders Revoke Envelope Status flow when request for revoking e-signature.

You can use the “Revoke Signature” action to revoke the signature request that was sent to the recipient when the contract document is in Awaiting Signature state.

Revoke Signature action voids all the docusign envelopes previously sent for the document and terminates the e-signing process. The signature becomes null and void and the document version is unlocked. The contract status changes to ‘Negotiating’ and ‘Send for Signature’ button is enabled.
