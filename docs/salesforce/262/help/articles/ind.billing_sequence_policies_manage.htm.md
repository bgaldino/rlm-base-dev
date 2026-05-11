---
article_id: ind.billing_sequence_policies_manage.htm
title: Configure Sequence Policies
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_sequence_policies_manage.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Configure Sequence Policies

You are here:

SALESFORCE HELP
DOCS
AGENTFORCE REVENUE MANAGEMENT
Configure Sequence Policies

Define the sequential number structure and the filters for choosing which invoice or credit memo records to number.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To configure sequence policies:	

Billing Admin permission set

OR

Billing Operations User permission set

To configure sequence policies, your Billing Admin must turn On Sequential Numbering.

From the App Launcher, find and select Sequence Policies.
Click New.
Enter a sequence policy name.
If necessary, enter a description.
Select the target object for which you’re creating the sequence policy.
Specify the sequence policy's effective date and time range.
To activate the sequence policy, select Active.

You can also create draft sequence policies and activate them later.

To generate and assign continuous sequential numbering to the target object records, select Enforce gapless sequence.
NOTE Select this option to ensure sequential numbers are gapless. Any skipped or unassigned numbers are stored in the Sequence Gap Reconciliations records and reassigned to - to the target object records to maintain continuity.
Set selection conditions to determine which sequence policy is applied to a target object record.
If you don't specify any selection conditions, all eligible posted - target object records are automatically assigned a number.
Enter the sequence start number from which the sequential numbering begins.
To determine the value by which the sequential number increases, specify an increment value.
To indicate the last sequence value in the series, enter a maximum sequence number.
If you need the date, month, year, or fiscal year information to be included in the invoice and the credit memo number, select the date stamp format.
To indicate the minimum desired number of digits for the sequence number, add a minimum sequence number width.
If the generated sequence number is shorter than this width, it’s prepended with zeros. For example, if the width is 5 and the generated sequence number is 123, the sequence value becomes 00123.
Construct your sequence pattern with static texts and placeholder values.
The sequence pattern combines static text, such as prefixes or separators, with dynamic placeholders. Only the Date and Sequence Value placeholders are supported, and {SequenceValue} dynamic value is mandatory. The {Date} placeholder in a sequence pattern is replaced with a date in the date stamp format defined in the sequence policy. Supported formats are MM-DD-YYYY, MM-YYYY, YYYY-YY (Fiscal Year), and YYYY.
Save the changes.

Sequential numbering is applied to invoice or credit memo records when they are posted. When you set up sequence policies, make sure to define a unique policy that resolves for invoice or credit memo records that meet a specific set of conditions.

You can edit a sequence policy only when it’s in draft status. After activation, you can't edit the Increment Number, Sequence Pattern, and Target Object fields. You can also delete a deactivated sequence policy if it isn’t associated with any invoice and credit memo record.
