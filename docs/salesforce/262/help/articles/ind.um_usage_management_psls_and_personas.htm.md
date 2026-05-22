---
article_id: ind.um_usage_management_psls_and_personas.htm
title: Permission Set Licenses, Personas, and User Permissions
source_url: https://help.salesforce.com/s/articleView?id=ind.um_usage_management_psls_and_personas.htm&type=5&release=262
release: 262
release_name: Summer '26
area: usage
fetched_at: 2026-05-11
---

# Permission Set Licenses, Personas, and User Permissions

Manage the Usage Management functionality securely with permission set licenses. Assign user permissions to specific user personas to enable them to complete the work that's assigned to their role.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license
Create Users and Profiles

To begin, create users for Usage Management. Then assign users the appropriate permission sets. To help you plan, refer to the permissions table for Usage Management.

When you create a user, you must also assign a profile. Profiles define default settings for users. Some organizations create their own profiles, while others choose to use profiles included with Salesforce.

Remember, users can have only one profile, but can have many permission sets assigned to them.

Assign Permissions
PERMISSION
SET LICENSE	USER PERMISSION	PERSONAS	WHAT PERSONAS CAN DO
Usage Management Design Time	Usage Management Designer	

Usage Management Admin

Usage Designers

	
Create, read, update, and delete all design time objects
Read all run time objects

Usage Management Run Time	Usage Management Run Time User	

Usage Management Admin

Usage Designers

Account Executive

Customers

	
Create, read, update, and delete all run time objects
Read all design time objects

Wallet Management User	Wallet Management User	

Usage Management Admin

Account Executive

Customers

	R​ead all design time and run time objects

To view the count of the Usage Management permission set licenses that are available in your Salesforce org, go to Company Information in Setup. If you need permission set licenses in addition to the ones provided by the Usage Management license enabled in your org, contact your Salesforce account executive.

SEE ALSO
View and Manage Users
Create or Clone Profiles
Permission Set Licenses
