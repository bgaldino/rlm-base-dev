---
article_id: ind.sf_contracts_add_recipients.htm
title: Add E-Signature Recipients
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_add_recipients.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_for_submitting_a_contract_for_e-signature.htm
fetched_at: 2026-10-13
---

# Add E-Signature Recipients

The recipients are associated with the contacts. You can add the signers also by using Add Recipient.

On the Add Recipient page, you can add these details:

FIELD	DESCRIPTION
Recipient Name	Name of the recipient. Select the name from the list of contacts or add the name manually.
Recipient Email	Email address of the recipient. This is automatically populated if the recipient is selected from the list of contacts. Else, enter the email address manually.
Recipient Type	

Roles of DocuSign recipient. Supported recipient types are:

Signer: Signs and adds data to form fields on the documents in the envelope.

Host in Person: Acts as a signing host in the same physical location as the signer.

Carbon Copy: Gets a copy of the envelope but doesn't need to sign any documents.

Certified Delivery: Receives the signed documents for the envelope to be completed. See EnvelopeRecipients Resource.


Signer Name	Value required is dependent on what you selected as the recipient type. This field is available only for the Host in Person recipient type.
Signer Role	Determines the signer token that gets filled by their signature in the document. Not needed if you select Certified Delivery or Carbon Copy. Signer roles are defined in the electronic signature config entity.
Access Code	Passcode that the recipient must use to access the document.
Routing Number	Defines the sequence in which DocuSign sends the document for signing.
Recipient Locale	Defines the language for the recipient's email.
