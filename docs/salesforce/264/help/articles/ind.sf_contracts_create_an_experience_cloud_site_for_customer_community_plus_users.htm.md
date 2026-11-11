---
article_id: ind.sf_contracts_create_an_experience_cloud_site_for_customer_community_plus_users.htm
title: Create an Experience Cloud Site for Customer Community Plus Users
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_an_experience_cloud_site_for_customer_community_plus_users.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_setup_cc_plus_user.htm
fetched_at: 2026-10-13
---

# Create an Experience Cloud Site for Customer Community Plus Users

Create an Experience Cloud site so that external users can view contract documents, check e-signature status, and access signed contracts.

Set up the customer community plus user in Salesforce Contracts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, Professional, and Developer Editions
USER PERMISSIONS NEEDED	 
To view a contract document:	

Contract Management CC Plus Digital Experience User

From Setup, in the Quick Find box, enter Digital Experiences, and select All Sites.
Click New.
Choose one of these supported templates.
Customer Account Portal
Customer Service
Build Your Own (Aura)
Click Get Started.
Enter a name for the Experience Cloud site.
In URL, enter the name of your site.
This name is appended to the domain that you created when you ​enabled digital experiences​ for this org. For example, if your domain name is UniversalTelco.my.site.com and you're creating a customer community, you can enter customers to create the unique URL UniversalTelco.my.site.com/customers.
Click Create.
The site is created in the Preview status. Now you can build and customize or manage your site.
Click Builder.
If you selected the Customer Account Portal or Customer Service template:
Click Edit Default Navigation.
Click Add Menu Item.
In the Menu Item section, enter a name. For example, Contract Detail View.
Select Salesforce Object as the type, and then select Contract as the object type.
Select Default as the default list view.
Select Publicly available.
Save your changes.
If you selected the Build Your Own (Aura) template:
Click Home, and then click New Page.
Select Standard Page.
Select Contract Detail View, and then click Next.
Enter a name. For example, Contract Detail View.
Leave the API Name field blank.
Click Create.
Click Publish, and then click Publish.
Click Got It.
To see the published site, click Preview.
To view the contracts visible for a customer community user, click Contracts, and change the list view to All Contracts.

See Also

Set Up Salesforce Contracts Customer Community Plus User

Customize the Theme of Your Experience Builder Site

Initiate Non-Private External Review

Actions Available for Customer Community Plus Users in Salesforce Contracts
