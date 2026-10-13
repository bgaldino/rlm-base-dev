---
article_id: ind.sf_contracts_ms365_minimum_pri_sharepoint.htm
title: Create a SharePoint Site Manually Through Minimum Privilege Setup
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_ms365_minimum_pri_sharepoint.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_ms365_minimum_pri_overview.htm
fetched_at: 2026-10-13
---

# Create a SharePoint Site Manually Through Minimum Privilege Setup

Create a SharePoint site to store document templates and contract documents. When you create a SharePoint site, use the same user details that you used for creating the Azure app. To use an existing site, make sure you’re following it in SharePoint so it appears in the site list.

REQUIRED EDITIONS
NOTE To use a guided setup to integrate Microsoft 365 and Azure, see Set Up Microsoft 365 and Azure Integration Using Guided Setup.
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To create a site in SharePoint:	User without admin privileges in Azure

Create a SharePoint site.
Log in to your OneDrive account.
Click , and then click SharePoint.
Click Create site, and then click Team site.
Enter a site name without any spaces.
Click Next.
To add members, search for and select the admin user.
Users added to the site have access to all the folders and documents saved on the site. Salesforce recommends only the Microsoft Admin to be a member to preserve the integrity of the documents.
Click Finish.
Extract the drive ID.
Go to Graph Explorer and log in with your Microsoft credentials.
When retrieving the site ID in Microsoft Graph Explorer, sign in with the same least-privilege integration user.
In the Request body, select GET, v1.0, and to retrieve your site details, paste https://graph.microsoft.com/v1.0/me/followedSites.
Click Run query.
From the Response, copy and save the site ID for the SharePoint site that you created earlier.

In the graph-explorer, select GET, v1.0, and paste https://graph.microsoft.com/v1.0/sites/<SITE ID>/drives.
Replace the <Site ID> placeholder with the site ID that you copied in step 2d.
Click Run query.
From the Response, copy and save the drive ID. Use the drive ID while configuring the external document storage.
