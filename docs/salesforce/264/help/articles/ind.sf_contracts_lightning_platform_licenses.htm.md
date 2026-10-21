---
article_id: ind.sf_contracts_lightning_platform_licenses.htm
title: Set Up Salesforce Contracts for Lightning Platform Licenses
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_lightning_platform_licenses.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_post-install_steps_for_salesforce_contracts_winter_23.htm
fetched_at: 2026-10-13
---

# Set Up Salesforce Contracts for Lightning Platform Licenses

You can set up users to access Salesforce Contracts with a Lightning Platform Starter or Lightning Platform Plus license. Create a custom profile, assign the required permission sets, and grant read access to the required Contracts objects.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Performance Editions
To use Salesforce Contracts, you must have a Core CRM (Sales Cloud or Sales and Service Cloud), Lightning Platform Starter, or Lightning Platform Plus license. See Features Available with Lightning Platform Starter, Lightning Platform Plus, and Salesforce Platform Login Licenses. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To set up Salesforce Contracts with Lightning Platform Starter or Lightning Platform Plus license:	CLM Admin User

Prerequisite: Before you begin, make sure that Salesforce Contracts is enabled in your org. See Enable Salesforce Contracts.

Create a custom profile.
From Setup, in the Quick Find box, enter Profiles, and then select Profiles.
Clone an existing profile that has a Salesforce Platform or Salesforce Platform Login user license.
Click Assigned Apps, and then click Edit.
To make the contract app visible, select Visible next to Salesforce Contracts.
Save your changes.
Create a user.
From Setup, in the Quick Find box, enter Users, and then select Users.
Click New User.
In the User License field, select Salesforce Platform or Salesforce Platform Login.
In the Profile field, select the custom profile that you created.
Save your changes.
Assign the CLM Admin User or CLM Runtime User permission set to the user.
If needed, add the other permission sets, such as Clause Designer User and Microsoft 365 Word Designer.
See Personas and Permission Set Licenses for Salesforce Contracts.
Grant required object access.
Assign read and edit access to these objects and set field-level security (FLS) in the user's profile.
Document Template Token
Document Template
Contract Document Version
Document Generation Process
Contract
Document Clause
Document Clause Set
Contract Document Version Content Document
Object State-related entities
Document Recipient
Document Envelope
Document Template Content Document
OmniProcess Compilation
OmniProcess
OmniProcess Element
Assign the relevant record types, such as Contract Lifecycle Management, to the profile.
Set the sharing setting for Object State Definitions and Document Recipient to Public Read Only.
If the user requires admin access, grant read and edit access to Clause Category Configuration.
Considerations for Salesforce Contracts on Lightning Platform Licenses
Lightning Platform Starter and Lightning Platform Plus licenses provide more limited object access than Core CRM licenses, and those restrictions carry over to Salesforce Contracts. Review these object-access limitations before you set up Salesforce Contracts for users with a Lightning Platform license.
SEE ALSO
Considerations for Salesforce Contracts on Lightning Platform Licenses
