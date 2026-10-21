---
article_id: ind.sf_contracts_setup_cc_plus_user.htm
title: Set Up Salesforce Contracts Customer Community Plus User
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_setup_cc_plus_user.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_setup_digital_experience_sites.htm
fetched_at: 2026-10-13
---

# Set Up Salesforce Contracts Customer Community Plus User

Tasks to set up the customer community plus user in Salesforce Contracts.

Turn on the Customer Community Plus for Salesforce Contracts settings.

Configure a domain name, and then enable standard external profiles.
From Setup, in the Quick Find box, enter Digital Experiences, and then select Settings.
Select Enable Digital Experiences.
Enter a domain name, and then click Check Availability.
Click Save, and then click OK.
From Settings, scroll to Role and User Setting, and select Allow using standard external profiles for self-registration, user creation, and login.
Click OK, and then click Save.
Create a customer community plus account and associate it with a contact.
In the App Launcher, search for and open Accounts.
Click New, add the required details, and then save the account.
Clone and configure a customer community plus profile.
From Setup, in the Quick Find box, enter Profiles, and then select Profiles.
Click the name of a profile that’s similar to the one that you want to create, and then in the profile page, click Clone.
Enter a profile name.
Click Save.
Click Edit, next to the cloned profile name.
In the Administrative Permissions section, select API Enabled.
Click Save.
Create a customer community plus user by creating a contact under an account and enable it as customer.
In the App Launcher, search for and open Contacts.
Click New.
Add the required details in the Name field.
Save the contact.
Open the new contact that you created, and then select Enable Customer User.
In the New User page, select these items:

User License: Customer Community Plus

Profile: <Name of the cloned profile>

NOTE If you’ve cloned a profile, then in the profile field, select the cloned profile name.
Define other required fields, such as email and nickname.
Select Salesforce CRM Content User.
Click Save, and then click OK.
[Optional] From the Permission Set Assignments, click Edit Assignments and assign DocGen Run-time Community User, and Contract Management CC Plus Digital Experience User permission set.
Create an Experience Cloud Site for Customer Community Plus Users.
Activate the customer community plus digital experience site and associate the site to the cloned customer community plus profile.
From Setup, in the Quick Find box, enter Digital Experiences, and click All Sites.
Find the customer community plus site that you created, and then click Workspaces | Administration.
In Settings, click Activate, and then click OK.
In Preferences, select the Show All Settings in Workspace.
Click Save.
In Members, select Customer from the Search dropdown.
Select the profile that you cloned earlier from Available Profiles, and then click Add to move the profiles to the Selected Profiles list. Click Save.
Return to the Digital Experiences All Sites page.
Close the window.

Before you generate documents, make sure Field-Level Security (FLS) is enabled on the community user's profile or on a permission set assigned to that user. For the list of objects and fields that require FLS, see FLS Requirements for Contract Document Generation.

Create an Experience Cloud Site for Customer Community Plus Users
Create an Experience Cloud site so that external users can view contract documents, check e-signature status, and access signed contracts.
Actions Available for Customer Community Plus Users in Salesforce Contracts
Users with the CLM Digital Experience Partner or CLM Runtime User permission set can share contract documents with Customer Community Plus users. After the contract documents are shared, Customer Community Plus users can access the documents through the Customer Community portal. Within the portal, they can perform a range of actions on the shared documents.
