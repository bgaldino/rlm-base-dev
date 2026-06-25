---
article_id: ind.collections_set_up_actionable_segmentation.htm
title: Set Up Actionable Segmentation for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_set_up_actionable_segmentation.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-06-21
---

# Set Up Actionable Segmentation for Collections and Recovery

Enable Actionable Segmentation, which helps you segment similar client profiles, curate them, and design timely and personalized client outreach programs. Create actionable list definitions by using the Collection Plan and related objects. Your collections managers can use these list definitions to create prioritized lists of collection plans, and plan collections activities more effectively.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
Create and run actionable list definitions:	

Actionable Segmentation

AND

Data Pipelines Base User

AND

Query for Data Pipelines

Create actionable list definitions that help you ‌build datasets containing collection plan records by joining information across Collection Plan and related objects. For example, to create a list of collection plans of high-risk borrowers, create a dataset containing such records by performing cross-object joining of Collection Plan, Collection Plan Reason, Account, Contact, Financial Account, and other related objects.

Create an actionable list definition by creating a Data Processing Engine definition. In the Data Processing Engine definition, you can specify cross-object join criteria to transform the data in the format you want. After you save, activate, and run a Data Processing Engine definition, a dataset is created. The dataset is saved in a shared space in Salesforce, which is associated with the actionable list definition.

After the actionable list definition is created, you can configure the columns and list member statuses, and then activate the actionable list definition. After an actionable list definition is activated, it’s available for your collection managers to create prioritized lists of collection plans.

Enable Actionable Segmentation.
Set tab visibility and assign object permissions.
Create an actionable list definition by using the Collection Plan and related objects.
The definition helps you transform data available in your Salesforce org and write back the transformation results as a new dataset.
Select default visible columns for actionable lists.
The dataset associated with an actionable list definition contains records that you can use as a data source to create actionable lists. Select the fields from this dataset to be visible as default columns in the actionable list and set their display order.
Set the display format for actionable list columns.
Set the format of dataset fields, and change the order in which these fields appear in actionable lists. The formatting and reordering capability helps collection managers to visualize data easily.
Configure list member status values to represent the status of client engagement activities planned for list members. For example, if a client engagement activity is to call list members, the various call status values are Successful, Failed, Busy, No-Answer, and Canceled. You can add values and icons that best represent these status values.
To make the actionable list definition available for your collection managers to create actionable lists, activate the definition.
You can activate an actionable list definition only after you configure default visible columns and list member status values. After you activate and run a data processing engine definition, a dataset is created and saved in a shared space in CRM Analytics.
To ensure the dataset is refreshed periodically so that it contains the latest records, run the data processing engine definition by using a schedule-triggered flow.
