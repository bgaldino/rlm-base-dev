---
article_id: ind.collections_add_cpstatus_picklist_values.htm
title: Configure Picklist Values and Assign Field-Level Access
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_add_cpstatus_picklist_values.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_interaction_outcome.htm
fetched_at: 2026-06-21
---

# Configure Picklist Values and Assign Field-Level Access

Add the picklist values for the various fields on the Collection Plan, Case, and Case Proceeding objects, and assign field-level access. Enable Business Rule Engine components.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To assign permission sets:	

Assign Permission Sets

AND

View Setup and Configuration

AND

Collections and Recovery Admin


To add picklist values:	Customize Application
To set field-level security:	

Collections and Recovery Admin

AND

Manage Profiles and Permission Sets permission

AND

Customize Application permission

Make sure that you have set up case management for Collections and Recovery.

To help collections specialists to create a case for a collection plan, assign read and edit access to the Case Source field on the Case object.
Add Active and Pending as picklist values to the Status field on the Collection Plan object.
Collections specialists can create a case of type Legal for a collection plan only if the collection plan status is Active or Pending. If you change these status values to any other similar terms, make sure that you make these changes in the prebuilt expression template, Determine Case Eligibility for Legal Proceedings. Clone this expression set template, and update the CollectionPlanActiveStatus and CollectionPlanPendingStatus values.
Add Legal as a picklist value to the Type field on the Case object.
If you change this picklist value from Legal to any other similar term, make sure to customize the Collections: Create Case and Related Case Proceeding Records prebuilt flow to reflect this change. This flow checks if the case type is Legal, and then creates case proceeding and case proceeding participant records.
To help collections specialists update a case proceeding record for a legal case created for a collection plan, assign read and edit access to the Type and Subtype fields on the Case Proceeding object.
Add Email, Phone, Meeting, and any other type of interaction that you want to have with a customer as picklist values to the Type field on the Event object.
To help collections specialists create a collections interaction event, assign read and edit access to the Type field on the Event object.
To enable collections specialists or collections managers transfer cases to different users, assign the Transfer Cases permission to the collections specialist and collections manager profiles.
In Setup, find and select Profiles.
Click the profile that you want to edit.
Click Edit.
Under General User Permissions, select Transfer Cases.
Make sure that you assign this permission to the collections specialist user profile. This profile is often used in managing collection plans and their related cases.
Enable Business Rules Engine components.
