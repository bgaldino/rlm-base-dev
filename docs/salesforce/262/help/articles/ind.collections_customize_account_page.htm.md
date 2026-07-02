---
article_id: ind.collections_customize_account_page.htm
title: Customize Lightning Pages to View Collections Summary and Linked Collection Plans
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_customize_account_page.htm&type=5&release=262
release: 262
release_name: Summer '26
area: collections
parent_article: ind.collections_setup_insights_account_page.htm
fetched_at: 2026-06-21
---

# Customize Lightning Pages to View Collections Summary and Linked Collection Plans

To show the key collections metrics, such as average days past due, total initial due amount, total current due amount, and total payments received of all the collection plans linked to an account, add the ShowCollectionsSummaryForAccount Flexcard to an account record page. To view all the collection plans linked to an account, add the Dynamic Related List–Single component to an account record page.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
USER PERMISSIONS NEEDED
To add the ShowCollectionsSummaryForAccount Flexcard, and the Dynamic Related Lists component to Lightning pages in the Lightning app Builder:	

Collections and Recovery Admin permission set

AND

Customize Application permission

From the App Launcher, find and select Collections.
Click Accounts, and open an account record details page.
Click , and then select Edit Page.
Drag the Flexcard component from the Components panel to the Lightning page canvas location where you want to position the component on the record page.
In the Properties pane, select the Flexcard that you have cloned and customized from the prebuilt Flexcard, ShowCollectionsSummaryForAccount.
Drag the Dynamic Related List–Single component from the Components panel to the Lightning page canvas location where you want to position the component on the record page.
In the Dynamic Related List–Single properties pane, enter these details.
For related list, search and select Collection Plans
Enter a label for the related list.
For related list, search and select Type.
Specify the number of records to show in the list.
Specify the fields to show.
Specify the sort field and sort order.
Save the changes and activate the page.
