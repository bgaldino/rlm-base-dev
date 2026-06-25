---
article_id: ind.collections_clone_customize_flexcard_collections_summary.htm
title: Clone and Customize Prebuilt Flexcard for Collections Summary
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_clone_customize_flexcard_collections_summary.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_insights_account_page.htm
fetched_at: 2026-06-21
---

# Clone and Customize Prebuilt Flexcard for Collections Summary

Clone the prebuilt flexcard, ShowCollectionsSummaryForAccount. Link the Data Processing Engine definition that you cloned and customized earlier.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To clone the prebuilt Flexcard:	

Collections and Recovery Admin permission set

AND

Omnistudio Admin

From the App Launcher, find and select Flexcards.
Open the ShowCollectionsSummaryForAccount Flexcard.
Click Clone.
Enter the name, and description, and save the changes.
Open the cloned Flexcard.
From the Setup panel, expand Datasource.
Under the Test Parameters section, for the recordId key, enter the record ID of the Data Processing Engine definition that you cloned and customized earlier.
You can get the record ID of the cloned Data Processing Engine definition by running this API endpoint.
‘SELECT Id FROM BatchCalcJobDefinition WHERE DeveloperName = '<API name of the cloned definition>'’
Save the changes and activate the cloned Flexcard.
