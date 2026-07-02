---
article_id: ind.collections_setup_insights_account_page.htm
title: Set Up Account Summary for Collections and Recovery
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_setup_insights_account_page.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-06-21
---

# Set Up Account Summary for Collections and Recovery

Add custom fields to the Account object to store collections summary of all the collection plans associated with an account. Clone and customize the predefined Data Processing Engine definition to compute the aggregated summary of specific collection plan fields. Clone and customize the prebuilt Flexcard to show the aggregated collections summary. Customize the Lightning pages to view the Collections Summary, and all the collection plans linked to an account.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
Create Custom Account Fields for Collections Summary
Add custom fields to the Account object to store aggregated collections data, such as total initial due amount, total current total due amount, total payments received, and average days past due. Set field-level security to these fields.
Clone and Customize the Predefined Data Processing Engine Definition for Collections Summary
Clone and customize the predefined Data Processing Engine definition. This definition is designed to compute the aggregated summary of specific collection plan fields, such as the initial amount due, current amount due, payments received, and the average days past due for all collection plans linked to an account.
Clone and Customize Prebuilt Flexcard for Collections Summary
Clone the prebuilt flexcard, ShowCollectionsSummaryForAccount. Link the Data Processing Engine definition that you cloned and customized earlier.
Customize Lightning Pages to View Collections Summary and Linked Collection Plans
To show the key collections metrics, such as average days past due, total initial due amount, total current due amount, and total payments received of all the collection plans linked to an account, add the ShowCollectionsSummaryForAccount Flexcard to an account record page. To view all the collection plans linked to an account, add the Dynamic Related List–Single component to an account record page.
