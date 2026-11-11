---
article_id: ind.sf_contracts_default_electronic_signature_envelope_configurations_for_contracts.htm
title: Default Electronic Signature Envelope Configurations for Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_default_electronic_signature_envelope_configurations_for_contracts.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_electronic_signature_envelope_config.htm
fetched_at: 2026-10-13
---

# Default Electronic Signature Envelope Configurations for Contracts

The Electronic Signature Envelope Config serves as a fallback for e-signature settings when the Contract Type Config doesn't define signature settings for a contract type.

No envelope config records exist by default. If your Contract Type Config settings don't include signature settings for a contract type, create an envelope config record using the values in this table as a reference. For standard and custom objects other than contracts, an envelope config is required.

FIELD	DESCRIPTION	DEFAULT VALUE
Target Object Name	The name of the standard or custom object for which you are defining the envelope configurations.	Contract
Vendor	The application vendor you are using to send documents for e-signature.	DocuSign
Vendor Account Identifier	N/A	N/A
Expiration Enabled	

When set to Yes, the envelope expires and is no longer available for signing after the specified number of days after it is sent. When set to No, the account default setting is used. You can modify the expiration days as needed. You can configure an option to send signers an expiration warning. When an envelope expires, the status changes to Voided and it can no longer be viewed or signed by recipients.

The number of days before sending the expiration warning must be less than the number of days before the envelope expires.

	Disabled
Expiration Period	The number of days that a sent envelope remains active before it expires. A negative number in response means that the envelope has already expired.	5
Expiration Warning Period	The number of days before the envelope expires that an expiration warning email is sent to the recipient. If set to 0 (zero), no warning email is sent.	1
Reminder Enabled	

When set to Yes, follow-up emails are sent to the signers automatically. You specify when and how often to send notifications. When set to No, no reminders are sent.

The number of days before sending the first reminder should be less than the number of days before the request expires.

	Disabled
First Reminder Period	The number of days after which the first reminder is sent.	2
Reminder Interval Period	The frequency for sending reminders, i.e. how many days to wait between subsequent reminders.	1
Vendor Default Notification Enabled	

The setting indicates whether or not the defaults for notifications should be used on the envelope.

You will not be able to edit the Electronic Signature Envelope Config configurations while sending the envelope if this option is enabled.

	Disabled
