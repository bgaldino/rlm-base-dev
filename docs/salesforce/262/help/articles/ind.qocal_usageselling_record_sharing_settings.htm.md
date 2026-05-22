---
article_id: ind.qocal_usageselling_record_sharing_settings.htm
title: Configure Record Sharing and Sharing Rules for Usage Selling
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_usageselling_record_sharing_settings.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Configure Record Sharing and Sharing Rules for Usage Selling

For users to access the data created by usage designers or catalog admins, Setup record sharing for all usage-related objects. This configuration is crucial for the seamless execution of usage selling processes within Salesforce.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create and edit sharing settings:	

Manage Sharing

From Setup, in the Quick Find box, enter Security, and then select Sharing Settings.
Click Edit.
Set the organization-wide defaults for these Usage Selling objects.
	
Object	Organization-Wide Defaults
Quote	All Partner Users Read/Write
Opportunity	All Partner Users Read/Write
Price Book	Public Read Only
Price Book Rate Card	Public Read Only
Binding Object Custom Extension	Public Read Only
Save your changes.
In the Sharing Rules section, click New against the object’s sharing rule that you want to define a rule for.
Give your rule a label, a name, and, if necessary, a description.
Select Guest user access, based on criteria as the rule type.
Specify the field, operator, and value criteria to filter the records to be included in the sharing rule.
The fields available depend on the object selected, and the value is always a string or number.
Specify the users that you want to provide access to the data.
Save your changes.
