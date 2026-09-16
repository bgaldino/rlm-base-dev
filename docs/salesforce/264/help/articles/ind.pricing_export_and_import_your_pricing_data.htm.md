---
article_id: ind.pricing_export_and_import_your_pricing_data.htm
title: Export and Import Your Pricing Data
source_url: https://help.salesforce.com/s/articleView?id=ind.pricing_export_and_import_your_pricing_data.htm&type=5&release=264
release: 264
release_name: Winter '27
area: pricing
parent_article: ind.pricing_considerations_for_importing_and_exporting_pricing_data.htm
fetched_at: 2026-09-07
---

# Export and Import Your Pricing Data

To create a new package with your pricing data to reuse them in another Salesforce org, create a new package and deploy it on another Salesforce org.

REQUIRED EDITIONS
USER PERMISSIONS NEEDED
To deploy and use a package:	Salesforce Pricing Design Time
IMPORTANT Before importing data, check your org's current decision tables to ensure you're within the limits. Importing decision tables without verifying available space may cause the data import to fail.
Log in to your Salesforce org that you want to export pricing data.
From Setup, in the Quick Find box, find and select Package Manager.
Click New.
In the Create a Package window, give your package a name and, choose to add details in the optional Description field.
Save your changes.
In the Package Detail window, select the Components tab and click Add.
Select a Component Type. You can select one or more component names from the displayed list.
Click Add to Package.
On the Package Detail page, click Upload.
Enter a Version Name. Edit the Version Number or use the auto-populated value. If needed, enter a description and set a password to protect the package.
Click Upload, again.
After you upload the package, the installation URL is available in the Version Detail.
Click the installation URL on the Version Detail window or copy and paste the URL on a browser window.
The installation URL prompts the user to log in to the subscriber org and then enables them to install the package in any org and enable it when ready.
Enter the username and password of the org where you want to install your package.
Select one of these options.
Install for admins only
Install for all users
Install for specific profiles
Click Install.
Your pricing metadata is now available on your new org.
