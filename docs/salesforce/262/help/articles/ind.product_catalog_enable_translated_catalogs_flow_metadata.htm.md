---
article_id: ind.product_catalog_enable_translated_catalogs_flow_metadata.htm
title: Use Flow Metadata to Enable Translated Product Catalogs
source_url: https://help.salesforce.com/s/articleView?id=ind.product_catalog_enable_translated_catalogs_flow_metadata.htm&type=5&release=262
release: 262
release_name: Summer '26
area: pcm
fetched_at: 2026-05-12
---

# Use Flow Metadata to Enable Translated Product Catalogs

One method for enabling translated product catalogs is to download an updated version of the Discover Products flow and use its metadata to create a new flow.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions of Agentforce Revenue Management where Transaction Management is enabled
USER PERMISSIONS NEEDED
To open, edit, or create a flow in Flow Builder:	Manage Flow
To enable translations:	Manage Product Catalog

To use the metadata from the updated Discover Products flow, you'll create and download a new flow from your org to your local machine. Then you'll replace the contents of the new flow with the contents of the updated Discover Products flow and upload the new flow to your org.

Download Discover_Products_With_Translations.flow.
In Your Salesforce org, select Setup then search for and select Flows.
Open the flow Discover Products.
In Flow Builder, select Save As New Flow and name your new flow Discover Products With Translations.

Make a note of the API name that's generated automatically. For example, Discover_Products_With_Translations.

Open Workbench from https://workbench.developerforce.com and connect it to your org. Salesforce doesn’t maintain Workbench, so we can’t address issues or bugs related to using it. We recommend that you use our alternative and integrated tools. See Replacement Tools for Workbench for more information.
On the Metadata tab, choose the option for Metadata groups
For Input, enter Flow
For Members, enter the API name of the new flow, Discover_Products_With_Translations.
Check Single Package
Select Retrieve.
When the retrieval succeeds, select Fetch then Download.
In the default download location on your local machine, find and extract the file retrieve.zip.
Delete the file Discover_Products_With_Translations.flow that you extracted from the ZIP file. On Windows, it's retrieve\flows\Discover_Products_With_Translations.flow. On MacOS and Linux systems it's retrieve/flows/Discover_Products_With_Translations.flow
Move or copy the version of Discover_Products_With_Translations.flow you downloaded in the first step to the folder retrieve\flows (for Windows) or retrieve/flows (for MacOS and Linux).
Open Discover_Products_With_Translations.flow in a text editor an verify that the flow name defined in the <interviewLabel> and <label> XML tags matches the name of your flow. Also, note of the API version that's defined in the <apiVersion> tag and be sure that Workbench is set to the same version.
Save the file and close the editor.
Create a zip file called package.zipthat includes the flows directory (which in turn contains Discover_Products_With_Translations.flow) and the file package.xml. Be sure to keep the same relative locations of the flow and XML files in the zip file. The flow should be in the flows folder and the XML file should be at the top level of the archive.
To upload the new flow to your org, go back to Workbench and select the Deploy tab.
For File, choose the package.zip file.
Check Single Pagkage.
Select Deploy.
When package.zip finishes uploading, activate the new flow by going to Setup > Flows.
Locate and select the flow Discover Products With Translations.
In the flow, select Activate.

To check your work, go to any quote or order and select Browse Catalogs to see the translated product catalog names.
