---
article_id: ind.collections_setup_actionable_segmentation.htm
title: Create an Actionable List Definition by Using Predefined Data Processing Engine Definition
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_setup_actionable_segmentation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_outbound_dialer.htm
fetched_at: 2026-06-21
---

# Create an Actionable List Definition by Using Predefined Data Processing Engine Definition

Use the prebuilt Data Processing Engine definition to create an actionable list definition that helps you create a dataset of delinquent collections and associated accounts. You can use this dataset to create an actionable list of delinquent borrowers to get started with the outreach activity.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To create actionable list definitions:	

Collections and Recovery Admin permission set

AND

Actionable Segmentation permission set

AND

Data Pipelines Base User permission set

AND

View Setup and Configuration permission

From Setup, in the Quick Find box, find, and select Actionable Segmentation Settings.
Click Use Existing Data Processing Engine Definition.
Enter a name for the list definition. Enter a name that contains only alphanumeric characters and begins with a letter.
Select the Collection Plan object.
Select the cloned Data Processing Engine definition, Filter Collection Plans by Overdue Amount Data Processing Engine definition, and click Save.
Activate and run the definition.
To view the actionable list definition and the associated dataset name and status, from Setup, in the Quick Find box, find, and select Actionable Segmentation Settings.
Locate the list definition that you created earlier, and click the corresponding List Member Status Count entry.
Add these status values, New, and Call Connected, and select an icon that best represents these values.
Select default visible columns for actionable lists that you plan to create from this actionable list definition.
Create an actionable list of delinquent collections by using this newly created actionable list definition.
