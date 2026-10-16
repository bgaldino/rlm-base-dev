---
article_id: ind.sf_contracts_e-signature_workflows.htm
title: E-Signature Workflows
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_e-signature_workflows.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_e-signature_overview.htm
fetched_at: 2026-10-13
---

# E-Signature Workflows

Each e-signature action is available at a specific contract state and transitions the contract to the next state in the lifecycle.

The following table shows the e-signature actions, the contract states where each action is available, and the resulting state transition.

PRODUCT ACTION	DESCRIPTION	FROM CONTRACT STATE	TO CONTRACT STATE	WORKFLOW
Send for Signature	Sends the latest contract document version to DocuSign and notifies recipients to review and sign.	Negotiating	Awaiting Signature	Send Envelope flow
Update Envelope Status	Queries DocuSign for the latest envelope status. If all recipients signed, the contract moves to Signed. If a recipient declined, the contract moves to Signature Declined.	Awaiting Signature	Signed or Signature Declined	Update envelope status flow
Revoke Signature	Voids all DocuSign envelopes for the document and terminates the signing process. The document version is unlocked for further editing.	Awaiting Signature	Negotiating	Revoke envelope flow
