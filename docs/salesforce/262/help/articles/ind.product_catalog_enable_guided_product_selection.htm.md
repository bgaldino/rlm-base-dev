---
article_id: ind.product_catalog_enable_guided_product_selection.htm
title: Enable Guided Product Selection
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_enable_guided_product_selection.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Enable Guided Product Selection

Before you configure Guided Product Selection to help users find the right products, you must enable Product Discovery, Discovery Framework, Omnistudio, and Guided Product Selection. Then, deploy a predefined template to create an Omniscript that’s used to configure questionnaires.

REQUIRED EDITIONS
View supported products and editions.
USER PERMISSIONS NEEDED
To set up Guided Product Selection:	

Product Catalog Management Designer permission set

AND

OmniStudio Admin permission set

Complete the Prerequisites for Guided Product Selection Setup
Make sure that you have access to Omnistudio.
NOTE Omnistudio isn’t available with Product Catalog Management by default. Omnistudio is available as a part of other products such as Agentforce Revenue Management or as a standalone Omnistudio license.
The Omniscript for Guided Product Selection can be accessed by using the Omnistudio managed package designer or the Omnistudio standard designer.
To use the Omnistudio managed package designer, enable the Managed Package Runtime setting, and then enable the Managed Package Designer setting. If needed, enable the Deploy Custom Lightning Web Components setting. See Omnistudio Settings.
To use the Omnistudio standard designer, disable the Managed Package Runtime setting, and then disable the Managed Package Designer setting. See Omnistudio Standard Designer.
Enable Discovery Framework and then turn on the Import or Export setting. See Enable Discovery Framework and Configure Import or Export Settings.
Turn on the Use Indexed Data for Product Listing and Search setting. See Product Index and Search in Product Catalog Management.
Enable the necessary Product Discovery settings. See Configure Product Discovery Settings.
Enable Guided Product Selection
From Setup, find and select Product Discovery Settings.
Enable Guided Product Selection.
Deploy the ProductGuidedSelectionIntegration Omniscript

The ProductGuidedSelectionIntegration Omniscript generates a Pub/Sub event—containing the discovery framework response ID—which initiates a search on the Product List component. In Discovery Framework, the Omniscript also saves user responses, which are used by the Guided Product Selection API to search for products. When designing Omniscripts for assessments, include the ProductGuidedSelectionIntegration Omniscript as the final step to configure these essential settings automatically.

From Setup, in the Quick Find box, enter Discovery Framework, and then, under Discovery Framework, select General Settings.
Enable Sample Templates.
In the Sample Templates section, click the Discovery Framework Sample Template page link. The Discovery Framework Sample Templates page appears.
Deploy the Guided Product Selection template.
Access Omnistudio: From the App Launcher, find and select the Omnistudio app. The Omniscripts tab appears.
Expand ProductGuidedSelection/Integration.
Click ProductGuidedSelectionIntegration.
IMPORTANT Don’t change the ProductGuidedSelectionIntegration omniscript. On the Setup tab, the message framework must be Pub/Sub. On the Properties tab, the remote class must be Store Responses and the remote method must be invokeMethod.
Click Activate Version.

To users (sales reps and customers) who use Guided Product Selection, assign the necessary permission sets and provide record access. See Permissions to Access Product Discovery.
