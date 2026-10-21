---
article_id: ind.sf_contracts_microsoft_365_frequently_asked_questions_faqs.htm
title: Microsoft 365 Frequently Asked Questions (FAQs)
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_microsoft_365_frequently_asked_questions_faqs.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integration_ms365_overview.htm
fetched_at: 2026-10-13
---

# Microsoft 365 Frequently Asked Questions (FAQs)

This document provides answers to the common questions about integrating Salesforce Contracts with Microsoft 365 and Azure.

COMMON QUESTIONS	ANSWERS
Integration
Why must I integrate Salesforce Contracts with Azure?	

Integrate Salesforce Contracts with Microsoft 365 Azure to enable document editing and collaboration in Word. Azure provides the secure connection required for this integration. With the integration users can:

Design and maintain contract templates by using Microsoft Word.
Create and edit contract documents by using familiar Word features within the Microsoft 365 environment.

Can Salesforce Contracts work without Azure?	

Yes, Salesforce Contracts works without Azure, but with limited capabilities. Without Azure integration, you can:

Create and manage document templates in Salesforce by using Omnistudio or the Salesforce Core tools.
Download documents for offline editing and review.
Upload updated versions manually and maintain multiple versions in Salesforce.

Azure and Microsoft Word 365 integration is required to use these advanced features.

Edit documents online.
Insert Salesforce data, such as clauses, into documents.
Perform internal and external collaborative redlining.
Automatically reconcile and save the changes back to Salesforce.

Do customers purchase an Azure license, or does Salesforce manage it?	

Salesforce doesn't manage or supply Microsoft 365 or Azure licenses. Customers are responsible for setting up and maintaining their own Microsoft licensing for the integration. Customers must:

Have a Microsoft Azure account.
Provide an Office 365 E1 license (or later) for users who need the integration.
Handle license setup and renewal directly with Microsoft.

Setup and Configuration
What main setup steps are required to integrate Salesforce Contracts with Azure?	

To integrate Salesforce Contracts with Microsoft 365 and Azure, follow these steps.

Configure a Microsoft Azure App.
Configure an Auth Provider in Salesforce.
Create a Named Credential in Salesforce.
Create a SharePoint Site.
Configure External Document Storage for Contracts.
Deploy the Salesforce Contracts Connector for Word Add-in.
(Optional) Insert the Add-in into Microsoft Word.

Do you have a quick way to execute the integration setup steps?	

Yes. Salesforce provides a guided setup to help you configure Microsoft 365 and Azure integration quickly and accurately. The guided setup:

Streamlines the configuration of the Azure App, Auth Provider, and Named Credential.
Includes step-by-step instructions with embedded help and walkthrough videos.
Validates your entries to reduce setup errors.
Can be launched from Salesforce Setup by selecting Microsoft 365 and Azure Integration.

See Set Up Microsoft 365 and Azure Integration Using Guided Setup.


How do we set up Auth Provider and Named Credentials for the Microsoft 365 integration?	You must manually create Auth Provider and Named Credentials in Salesforce. They aren't created through any automated component or wizard. This manual setup process is common across most Salesforce integrations and isn't specific to Microsoft 365. See Configuring an Auth Provider for Microsoft App.
Roles and Access
What is the Connected App on Azure?	

This is the application you register in Microsoft Azure Active Directory for the integration. It:

Acts as Salesforce's identity within Azure.
Salesforce to request access to Microsoft 365 resources such as SharePoint and OneDrive.
Is identified by a Client ID and secured with a Client Secret.

Why is a specific Salesforce user required for the Azure integration, and what permissions must I have?	

The integration user authenticates with the Named Credential that connects to Azure. This user:

Must be the person who created the Azure app
Is used by Salesforce to generate access tokens from Azure.
Enables the Microsoft Word Add-in to access and work with Microsoft 365 files.

What is the required Azure integration user profile for authenticating the Salesforce-Azure connection?	

You must create a dedicated Azure user with the right level of access for authenticating the Salesforce integration. The integration user:

Must be restricted from general access—no other employees in your org should use this account.

This setup ensures secure and consistent authentication for the integration.


Can we restrict access to specific contract clauses based on user roles?	Yes. Document Clause Sets and Clause records are Salesforce objects. You can apply record-level and field-level sharing rules, as in the case of any other standard or custom object. See Define Sharing Settings for Clause Sets and Clauses.
Permissions and Security
What privileges are required by the Connected App and why?	

The Connected App (Azure AD application) requires Microsoft Graph API permissions so the Salesforce Contracts Add-in for Word works seamlessly.

To configure with admin or higher privileges, the Azure app requires write permissions:

Files.ReadWrite.All
Enables the app to save and open document templates and contracts from OneDrive.
Sites.Read.All
Lets the Add-in access and manage documents in SharePoint collaboration sites.
User.ReadWrite.All
Lets the connected app create user extensions, which store identifiers for linking users to the correct Salesforce organization.
Directory.Read.All
Provides access to directory data (such as users and groups) — used for user mapping and access control.
openId and offline_access
Secures user authentication and to maintain session tokens.
mail.send
Enables the Add-in to send notification emails if required.

To configure with minimum privileges, the Azure app requires only read permissions. No write access is needed:

Sites.Selected
Restricts the app to access only explicitly approved SharePoint sites rather than the entire tenant. This permission can be used to replace Files.ReadWrite.All for added security. This ensures the app can write to specific sites configured via the graph explorer without granting global file permissions.
User.ReadBasic.All
Grants the app permission to read a limited set of non-sensitive profile properties such as displayName, mail, photo, userPrincipalName of all users in your organization on behalf of the signed-in user.
User.Read
Provides full profile access and allows reading the signed-in user’s profile (name, email, ID). Typical default scope for apps requiring user identity and portrait. Allows limited access needed for auth and personalization contexts.
openId and offline_access
Secures user authentication and to maintain session tokens.

These permissions support seamless document flow between Salesforce and Microsoft 365. Users collaborate and edit documents in Word, and Salesforce remains the system of record.


Why does the integration app require the User.ReadWrite.All permission?	

The User.ReadWrite.All permission allows the app to write extensions for all users, not just the one who authenticated. The Microsoft 365 integration:

Uses a single Microsoft account to authenticate named credentials.
Needs this permission to write extensions for every user who opens the Add-in.
Can't function properly with only User.ReadWrite, which limits access to the current user.

Why does the app require the Files.ReadWrite.All permission?	The Files.ReadWrite.All permission allows the app to write files to OneDrive or SharePoint on behalf of all users. This access is required to support features such as saving and updating documents through the integration.
Are there any workarounds available to avoid the permissions?	

No. The Microsoft Graph API permissions are required for the Salesforce Contracts integration with Word 365 to function as designed. Key points:

There are no workarounds to avoid the required Azure app permissions.
The integration depends on Microsoft Graph API for secure access to OneDrive, SharePoint, and user data.
These permissions are required to:
Copy files between Salesforce and OneDrive or SharePoint.
Modify the user extensions used for authentication.
Create or access SharePoint sites for storing documents.

Other options if you don't require Word 365 integration:

Use the desktop version of Microsoft Word for offline editing.
Consider third-party document management solutions with different integration models.

Extension Management
What information does the Microsoft 365 integration store in extensions?	

The Microsoft 365 integration extension stores linked Salesforce organization details:

Organization's web addresses (URLs).
Single Sign-On (SSO) web addresses used for logging in securely.
Active Organization: Web address of your most recently accessed Salesforce org.
First-Time User status: Tracks if you're using the Add-in for the first time.

How does the Microsoft 365 integration use extensions?	

When you open the Microsoft 365 Add-in, the integration:

Checks whether there's stored information linking your document to a Salesforce org.
Retrieves your stored Salesforce org details such as active and linked orgs.
Initiates the authentication process by using these org details.
Verifies whether the current document matches the active Salesforce org:
If it matches, you can continue using the Add-in.
If it doesn't match, you're prompted to switch to another linked Salesforce org, and the verification is repeated.

When are Microsoft 365 integration extensions created?	

Extensions are created when you open a document in an external editor for the first time and no extension exists. The Microsoft 365 integration:

Checks if an extension already exists.
Communicates with the configured Microsoft Azure app to create the extension for your Microsoft account.
Requires the Azure app to have the correct permissions to write the extension.

Storage Behavior
How are SharePoint and OneDrive used?	

SharePoint is used as a centralized repository for:

Storing contract documents and templates from Salesforce Contracts.
Organizing files in a dedicated SharePoint site for structured access.
Collaborating across teams with version control and shared access within Microsoft 365.

OneDrive is used for temporary file handling and online editing.

Temporarily stores documents when a user initiates editing in Microsoft Word 365.
Allows real-time editing of documents from Salesforce.
Saves the changes back to Salesforce after the document is checked in.

Does the document remain in SharePoint until redlining and check-in are complete?	Yes. The document stays in SharePoint while edits are in progress and until it's checked in. If redlining happens over multiple iterations, each editing cycle is treated as a separate document.
Are documents temporarily stored in SharePoint during check-out from CLM?	Yes. Documents are temporarily held in SharePoint or OneDrive during editing. Salesforce is the source of truth after checking the documents back in.
Are SharePoint documents linked or related to each other?	No. Each document stored in SharePoint is independent and not linked to other documents. Salesforce remains the source of truth, and documents stay in the SharePoint folder that you configured for external storage. See Configure External Document Storage for Contracts.
Does Salesforce delete documents from SharePoint after check-in?	No. Salesforce doesn't automatically delete documents. Customers must manually manage deletions or automate cleanup based on SharePoint retention policies. See Learn about retention for SharePoint and OneDrive.
Does deleting a contract record from Salesforce Contracts automatically remove the corresponding document from OneDrive?	

No. Deleting a contract record in Salesforce doesn't remove the related file from OneDrive automatically. Key points:

Files remain in OneDrive even after the contract record is deleted.
If needed, you must remove the files manually or use automated cleanup jobs in OneDrive or Microsoft 365.

Word Add-in Functionality
What is the Microsoft Word 365 Add-in used for?	

Users can work with contract documents in Microsoft Word while staying connected to Salesforce by using the Salesforce Contracts Connector for Word Add-in. With the Add-in, users can:

Design and maintain templates directly in Word by using its formatting tools.
Open and edit contract documents pulled from Salesforce.
Insert Salesforce data, including clauses from the Clause Library.
Save the changes back to Salesforce.
Use Contracts AI to draft clauses in Word.

What is the role of the Microsoft Word 365 Add-in if files already move from Salesforce to OneDrive without it?	

Files are automatically moved from Salesforce to OneDrive or SharePoint after you set up the Microsoft Azure connection. The Add-in isn't required for this step. However, the Add-in is required to:

Pull data from Salesforce into the document.
Create sections inside the document.
Add and track internal and external reviews.
Reconcile the document and push the final version back to Salesforce.

How is the Microsoft Word 365 Add-in deployed?	

Salesforce administrators deploy the Salesforce Contracts Connector for Word Add-in centrally through the Microsoft 365 admin center. Deployment steps:

Upload the Add-in manifest file provided by Salesforce to the Microsoft 365 admin center.
Assign the Add-in to all users or specific groups as needed.

After the Microsoft Add-in is deployed, users can:

Open Microsoft Word 365.
Click More Options, and then select Salesforce Contracts Connector for Word.

How often is a new version of the Microsoft Add-in made available by Salesforce?	

Salesforce doesn't publish a fixed schedule for updates to the Salesforce Contracts Connector for Word Add-in. Here's what to expect.

Major updates often align with Salesforce's seasonal release cycles (Spring, Summer, Winter).
Minor patches or fixes are often released more frequently, depending on need.

Release announcements are typically shared through:

Salesforce release notes.
Microsoft AppSource listing for the Add-in.

For the latest version and update details, regularly check these sources.


Redlining
Does document comparison show who made the changes during redlining?	No. Document comparison highlights content changes but doesn't show who made them—Salesforce doesn't track user names in comparison results. See Compare Two Versions of a Contract Document from the Microsoft 365 Editor.
How can I track who made the changes during redlining?	Use non-private mode during external redlining and make sure that Microsoft's Track Changes is turned on. When users return the document, you can see who made each change and when. See Initiate Non-Private External Review and Track changes in Word.
Can internal or external users access Salesforce clauses via the Add-in during redlining in Microsoft 365?	Internal users with access to Salesforce and the clause library can use the Add-in to view and insert clauses during redlining. External users can't access Salesforce data or the clause library through the Add-in. See Contract Authoring in Microsoft 365 Editor.
Document Signing
Why are DocuSign signatures overlapping the tags in my template?	This usually happens when the anchor tag in your template doesn't match the token defined in the DocuSignAnchorTabSetting. To place signatures correctly, make sure that the same token is used in both the template and the anchor tab setting. A mismatch can prevent proper placement and cause the signature to appear over the tag. See DocuSign Configuration Settings for Generic Documents.
