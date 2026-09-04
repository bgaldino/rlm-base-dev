---
article_id: ind.billing_collections_specialist_console_setup.htm
title: Set Up the Collections Specialist Console
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_collections_specialist_console_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_collections_specialist_console.htm
fetched_at: 2026-09-04
---

# Set Up the Collections Specialist Console

Grant your collections team access to the Collections Specialist Console: turn on the tab and add the console to the Collections app.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To set up the Collections Specialist Console:	

System Administrator

AND

Billing Collections and Recovery Specialist permission set

From Setup, in the Quick Find box, enter Profiles, and then select Profiles.
Select the profile assigned to your collections team.
Under Tab Settings, make sure the Collections Specialist Console tab's visibility is set to Default On.
From Setup, in the Quick Find box, enter App Manager, and then select App Manager.
Find the Collections app and click Edit.
In App Options or Navigation Items, add the Collections Specialist Console page, and then save your changes.
Grant field-level security access to the Initial Due Amount field on the Collection Plan Item object for the profile or permission set your collections team uses. Without this access, the Collection Progress chart in the console appears empty for those users.

After setup, assign the Billing Collections and Recovery Specialist permission set to each user who opens the console.
