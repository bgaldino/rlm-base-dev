---
article_id: ind.collections_community_user_profiles_permissions.htm
title: Clone and Assign Permissions Sets for Collections and Recovery Portal
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_community_user_profiles_permissions.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_community_portal_setup.htm
fetched_at: 2026-06-21
---

# Clone and Assign Permissions Sets for Collections and Recovery Portal

To control access to the Collections and Recovery features, create a profile for portal users with the appropriate permissions by cloning a community user profile. Assign object permissions. Clone the Collections and Recovery for Experience Cloud permission set and assign it to your portal users. This permission set gives the portal users the license and permissions to access the Collections and Recovery Portal and the prebuilt quick actions and flows.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create profiles:	Manage Profiles and Permission Sets
To clone and assign permission sets:	

Assign Permission Sets

AND

View Setup and Configuration

AND

Collections and Recovery Admin


To assign standard object permissions:	Financial Services For Partner Community

Before you begin, make sure that you have set up Collections and Recovery.

Create a partner community user profile.
From Setup, in the Quick Find box, enter Profiles, and then select Profiles.
Next to the user profile that maps to your partner community license, click Clone.
Enter a name for the cloned profile, for example Collections and Recovery Partner Community User, and then save your changes.
This cloned profile becomes the baseline that grants your portal users access to Collections and Recovery features.
Assign the relevant object permissions to the partner community user profile that you created earlier.
From Setup, in the Quick Find box, enter Profiles, and then select Profiles.
Click the partner community profile that you created earlier, and click Edit.
Under Standard Object Permissions, assign read, create, edit, and delete permissions to these objects according to your business requirements.
OBJECT

PaymentSchedule
PaymentScheduleItem
Collection Plan
Collection Plan Item
Case
Case Proceeding
Case Proceeding Participant
Clone the Collections and Recovery for Experience Cloud permission set.
In Setup, find and select Permission Sets.
Next to the Collections and Recovery for Experience Cloud permission set, click Clone.
Enter a label and an API name, and save your changes.
Create site users to access the Experience Cloud site that was created from the Collections and Recovery Portal template.
Assign the permission sets to the Experience Cloud site users that you created earlier.
In Setup, find and select Users.
Click the site user that you created earlier.
In Permission Set Assignments, click Edit Assignments.
From Available Permission Sets, add these permission sets to Available Permission Sets, and save your changes.
PERMISSION SET

The permission set that you cloned from Collections and Recovery for Experience Cloud permission set
OmniStudio User
Industry Service Excellence
Industries Visit
