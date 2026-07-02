---
article_id: ind.product_configurator_product_configurator_permissions.htm
title: Product Configurator Permission Sets
source_url: https://help.salesforce.com/s/articleView?id=ind.product_configurator_product_configurator_permissions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: configurator
fetched_at: 2026-05-12
---

# Product Configurator Permission Sets

Product Configurator is managed by users with varying roles and expertise. Give users appropriate access by assigning prebuilt permission sets or custom permission set groups.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions of Revenue Cloud with the Revenue Cloud Growth license or the Revenue Cloud Advanced license
Create Users and Profiles

To begin, create users for Product Configurator. Then assign users the appropriate permission sets. To help you plan, refer to the permission set table for Product Configurator.

When you create a user, you must also assign a profile. Profiles define default settings for users. Some organizations create their own profiles, while others choose to use profiles included with Salesforce.

Remember, users can have only one profile, but can have many permission sets assigned to them.

Assign Permission Sets

These prebuilt permission sets are based on user personas. Assigning these permission sets automatically grants the necessary user permissions and permission set license, and access to the features, objects, and fields needed to set up and use Product Configurator.

All these permission sets are available with the Product Configuration User permission set license.

Permission Sets
PERMISSION SET	INCLUDED PERMISSIONS
Product Configurator	Assign this permission set to users who need read and edit access to Product Configurator objects and APIs.
Product Configuration Rules Designer	Assign this permission set to users who create and manage product configuration rules in Product Configurator with Business Rules Engine.
Product Configuration Constraints Designer	Assign this permission set to users who create and manage constraint types and rules in Product Configurator with Constraint Rules Engine.
Assign User Permissions

If you require more granular control and flexibility over user access, create a custom permission set and assign these individual user permissions based on the specific tasks that users must perform.

User Permissions
USER PERMISSION	INCLUDED PERMISSIONS
Product Configurator	Assign this user permission to users who need read and edit access to Product Configurator objects.
Product Configurator API User	Assign this user permission to users who need read and edit access to Headless Configurator APIs.
Manage Configurator with Business Rules Engine	Assign this user permission to users who need to create, read, edit, and delete configuration rules in Product Configurator with Business Rules Engine.
Manage Configurator with Constraint Rules Engine	Assign this user permission to users who need create, read, edit, and delete constraint types and rules in Product Configurator with Constraint Rules Engine.
SEE ALSO
View and Manage Users
Create or Clone Profiles
Manage Permission Set Assignments
Permission Set Groups
Manage Muting Permission Sets
